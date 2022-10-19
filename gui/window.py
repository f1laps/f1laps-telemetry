from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, \
    QVBoxLayout, QCheckBox
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtSvg import QSvgWidget
import requests
import datetime

from gui.base_classes import F1QLabel, QHSeperationLine, QVSpacer
from gui.workers import APIUserPreferenceWorker
from lib.logger import log
from lib.file_handler import ConfigFile, get_path_temporary
from receiver.receiver import RaceReceiver
from receiver.helpers import get_local_ip
import config
import socket

F1LAPS_VERSION_ENDPOINT = "https://www.f1laps.com/api/f12020/telemetry/app/version/current/"
DEFAULT_PORT = 20777
DEFAULT_REDIRECT_HOST = "127.0.0.1"
DEFAULT_REDIRECT_PORT = 20957


class StartButton(QPushButton):
    """ Main button to start/stop telemetry receiver"""

    def __init__(self):
        super().__init__('Start Telemetry')
        self.setObjectName("startButton")
        self.setFixedSize(160, 45)

    def set_validating_api_key(self):
        self.setText("Starting...")

    def set_running(self):
        self.setText("Stop Telemetry")
        self.setStyleSheet("background-color: #B91C1C;")

    def reset(self):
        self.setText("Start Telemetry")
        self.setStyleSheet("background-color: #4338CA;")


class StatusLabel(F1QLabel):
    """ Text below StartButton to display current receiver status """

    def __init__(self):
        super().__init__()
        self.setText("Status: not started")
        self.setObjectName("statusLabel")
        self.setFixedSize(100, 15)

    def set_validating_api_key(self):
        self.setStyleSheet("color: #6B7280;")
        self.setText("Checking API key...")

    def set_invalid_api_key(self):
        self.setStyleSheet("color: #B91C1C;")
        self.setText("Invalid API key")

    def set_running(self):
        self.setStyleSheet("color: #6B7280;")
        self.setText("Status: running")

    def reset(self):
        self.setStyleSheet("color: #6B7280;")
        self.setText("Status: not started")


class TelemetrySession:
    def __init__(self):
        # The actual receiver session
        self.session = None
        self.is_active = False

    def start(self, api_key, enable_telemetry, use_udp_broadcast, ip_value, port_value, redirect_host, redirect_port,
              use_udp_redirect):
        receiver_thread = RaceReceiver(api_key, enable_telemetry=enable_telemetry, use_udp_broadcast=use_udp_broadcast,
                                       host_ip=ip_value, host_port=port_value, redirect_host=redirect_host,
                                       redirect_port=redirect_port, use_udp_redirect=use_udp_redirect)
        receiver_thread.start()
        self.session = receiver_thread
        self.is_active = True
        log.info("Started telemetry session")
        return True

    def kill(self):
        self.session.kill()
        self.is_active = False
        log.info("Stopped telemetry session")
        return True


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Get user config (before drawing UI!)
        self.user_config = ConfigFile().load()
        self.api_key_field = None
        self.api_key = self.user_config.get("API_KEY") or None
        self.broadcast_mode_enabled = self.user_config.get("UDP_BROADCAST_ENABLED") or False
        self.app_version = config.VERSION
        self.ip_value = self.user_config.get("IP_VALUE") or str(get_local_ip())
        self.port_value = self.user_config.get("PORT_VALUE") or str(DEFAULT_PORT)

        # Redirection config info
        self.udp_redirect_enabled = self.user_config.get("UDP_REDIRECT_ENABLED") or False
        self.redirect_host_value = self.user_config.get("REDIRECT_HOST_VALUE") or str(DEFAULT_REDIRECT_HOST)
        self.redirect_port_value = self.user_config.get("REDIRECT_PORT_VALUE") or str(DEFAULT_REDIRECT_PORT)

        # Draw the window UI
        self.init_ui()
        # Check if there's a new version
        self.check_version()
        # Track if we have an active receiver
        self.session = TelemetrySession()
        # Disable IP field if broadcast is checked
        self.udp_broadcast_checked()
        # Auto-start app if api key is set
        if self.api_key:
            self.start_button_click()



    def init_ui(self):
        # 1) Logo & heading
        logo_label = QSvgWidget(get_path_temporary('logo.svg'))
        logo_label.setFixedSize(100, 28)

        # 1) Enter API key section
        api_key_field_label = F1QLabel(
            text="1) Enter your API key",
            object_name="apiKeyFieldLabel"
        )
        api_key_help_text_label = F1QLabel(
            text="You can find your API key on the <a href='https://www.f1laps.com/telemetry'>F1Laps Telemetry page</a>",
            object_name="apiKeyHelpTextLabel"
        )
        self.api_key_field = QLineEdit()
        self.api_key_field.setObjectName("apiKeyField")
        self.api_key_field.setText(self.api_key)

        # 2) Check IP section
        ip_value_label = F1QLabel(
            text="2) Set your F1 game Telemetry settings",
            object_name="ipValueLabel"
        )
        ip_value_help_text_label = F1QLabel(
            text="Open the F1 Game Settings -> Telemetry and set the IP to this value:",
            object_name="ipValueHelpTextLabel"
        )
        self.ip_value_field = QLineEdit()
        self.ip_value_field.setObjectName("hostValueField")
        self.ip_value_field.setText(self.ip_value)

        self.port_value_help_text_label = F1QLabel(
            text="Set the port to this value (anything from 1024 to 49151, default is %s): " % DEFAULT_PORT,
            object_name="udpBroadcastHelpTextLabel"
        )
        self.port_value_field = QLineEdit()
        self.port_value_field.setObjectName("portValueField")
        self.port_value_field.setText(self.port_value)

        udp_broadcast_help_text_label = F1QLabel(
            text="Alternatively you can set and use UDP broadcast mode:",
            object_name="udpBroadcastHelpTextLabel"
        )
        self.udp_broadcast_checkbox = QCheckBox("Use UDP broadcast mode")
        self.udp_broadcast_checkbox.setChecked(self.broadcast_mode_enabled)
        self.udp_broadcast_checkbox.stateChanged.connect(lambda: self.udp_broadcast_checked())

        # UDP Redirection section
        udp_redirect_label = F1QLabel(
            text="3) UDP Redirection for Bass Shakers",
            object_name="udpRedirectValueLabel"
        )
        udp_redirect_help_text_label = F1QLabel(
            text="Enable forwarding the packets to another port (Useful for bass-shakers):",
            object_name="udpRedirectHelpTextLabel"
        )

        self.redirect_host_value_help_text_label = F1QLabel(
            text="Set the IP to Redirect traffic to (Default is %s): " % DEFAULT_REDIRECT_HOST,
            object_name="redirectIPHelpTextLabel"
        )

        self.udp_redirect_checkbox = QCheckBox("Enable UDP Redirection")
        self.udp_redirect_checkbox.setChecked(self.udp_redirect_enabled)

        self.redirect_host_field = QLineEdit()
        self.redirect_host_field.setObjectName("redirectIPValueField")
        self.redirect_host_field.setText(self.redirect_host_value)

        self.redirect_port_value_help_text_label = F1QLabel(
            text="Set the Port to Redirect traffic to (Default: %s): " % DEFAULT_REDIRECT_PORT,
            object_name="redirectPortHelpTextLabel"
        )
        self.redirect_port_field = QLineEdit()
        self.redirect_port_field.setObjectName("redirectPortValueField")
        self.redirect_port_field.setText(self.redirect_port_value)

        # Start/Stop button section
        self.start_button = StartButton()
        self.start_button.clicked.connect(lambda: self.start_button_click())
        self.status_label = StatusLabel()

        # Support & notes section
        help_text_label = F1QLabel(
            text="Need help? <a href='https://community.f1laps.com/c/telemetry-app-faqs'>Check out the FAQs!</a>",
            object_name="helpTextLabel"
        )
        self.app_version_label = F1QLabel(
            text="You're using app version %s." % self.app_version,
            object_name="appVersionLabel"
        )
        self.subscription_label = F1QLabel(
            text="",
            object_name="subscriptionLabel"
        )

        # Draw layout
        self.layout = QVBoxLayout()

        # Logo section
        self.layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(QHSeperationLine())

        # API key section
        # self.layout.addWidget(QVSpacer(0))
        self.layout.addWidget(api_key_field_label)
        self.layout.addWidget(api_key_help_text_label)
        self.layout.addWidget(self.api_key_field)

        # Telemetry settings
        self.layout.addWidget(QVSpacer(0.5))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(QVSpacer(0.5))
        self.layout.addWidget(ip_value_label)
        self.layout.addWidget(ip_value_help_text_label)
        self.layout.addWidget(self.ip_value_field)
        self.layout.addWidget(self.port_value_help_text_label)
        self.layout.addWidget(self.port_value_field)
        self.layout.addWidget(udp_broadcast_help_text_label)
        self.layout.addWidget(self.udp_broadcast_checkbox)

        # Redirect settings
        self.layout.addWidget(QVSpacer(0.5))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(QVSpacer(0.5))
        self.layout.addWidget(udp_redirect_label)
        self.layout.addWidget(udp_redirect_help_text_label)
        self.layout.addWidget(self.udp_redirect_checkbox)
        self.layout.addWidget(self.redirect_host_value_help_text_label)
        self.layout.addWidget(self.redirect_host_field)
        self.layout.addWidget(QVSpacer(0.5))
        self.layout.addWidget(self.redirect_port_value_help_text_label)
        self.layout.addWidget(self.redirect_port_field)

        # Start button
        self.layout.addWidget(QVSpacer(1))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(QVSpacer(5))
        self.layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Status & help
        self.layout.addWidget(QVSpacer(1))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(help_text_label)
        self.layout.addWidget(self.app_version_label)
        self.layout.addWidget(self.subscription_label)
        self.layout.setContentsMargins(30, 20, 30, 10)

        self.setLayout(self.layout)
        self.setFixedWidth(420)
        self.setWindowTitle("F1Laps Telemetry")

    def check_version(self):
        try:
            response = requests.get(F1LAPS_VERSION_ENDPOINT)
            version = response.json()['version']
            user_version_int = int(self.app_version.replace(".", ""))
            current_version_int = int(version.replace(".", ""))
            if version > self.app_version:
                self.app_version_label.setText(
                    "There's a new app version available (you're on v%s).<br><a href='https://www.f1laps.com/telemetry'>Click here to download the new version!</a>" % self.app_version)
                self.app_version_label.setStyleSheet("color: #B45309")
            elif version < self.app_version:
                self.app_version_label.setText(
                    "This is pre-release version v%s (stable version is v%s)." % (self.app_version, version))
                self.app_version_label.setStyleSheet("color: #059669")
        except Exception as ex:
            log.warning("Couldn't get most recent version from F1Laps due to: %s" % ex)

    def udp_broadcast_checked(self):
        if self.udp_broadcast_checkbox.isChecked():
            self.ip_value_field.setDisabled(True)
            self.ip_value_field.setReadOnly(True)
        else:
            self.ip_value_field.setDisabled(False)
            self.ip_value_field.setReadOnly(False)

    def start_button_click(self):
        if not self.session.is_active:
            log.info("Starting new session")
            self.start_telemetry()
            self.api_key_field.setReadOnly(True)
            self.api_key_field.setDisabled(True)
            self.ip_value_field.setReadOnly(True)
            self.ip_value_field.setDisabled(True)
            self.port_value_field.setReadOnly(True)
            self.port_value_field.setDisabled(True)
            self.udp_broadcast_checkbox.setDisabled(True)
            self.redirect_host_field.setDisabled(True)
            self.redirect_host_field.setReadOnly(True)
            self.redirect_port_field.setDisabled(True)
            self.redirect_port_field.setReadOnly(True)
            self.udp_redirect_checkbox.setDisabled(True)
        else:
            log.info("Stopping session...")
            self.stop_telemetry()
            self.start_button.reset()
            self.api_key_field.setReadOnly(False)
            self.api_key_field.setDisabled(False)
            self.ip_value_field.setReadOnly(False)
            self.ip_value_field.setDisabled(False)
            self.port_value_field.setReadOnly(False)
            self.port_value_field.setDisabled(False)
            self.udp_broadcast_checkbox.setDisabled(False)
            self.redirect_host_field.setDisabled(False)
            self.redirect_host_field.setReadOnly(False)
            self.redirect_port_field.setDisabled(False)
            self.redirect_port_field.setReadOnly(False)
            self.udp_redirect_checkbox.setDisabled(False)
            self.status_label.setText("Status: stopped")

    def start_telemetry(self):
        if self.session.is_active:
            log.error("A new session can't be started when another one is active")
            return False
        # Update user config
        self.api_key = self.api_key_field.text()
        self.broadcast_mode_enabled = self.udp_broadcast_checkbox.isChecked()
        self.user_config.set("API_KEY", self.api_key)
        self.user_config.set("UDP_BROADCAST_ENABLED", self.broadcast_mode_enabled)

        # Update Redirection config
        self.udp_redirect_enabled = self.udp_redirect_checkbox.isChecked()
        self.user_config.set("UDP_REDIRECT_ENABLED", self.udp_redirect_enabled)

        # Validate API key via F1Laps API
        self.validate_api_key(self.api_key)

    def validate_api_key(self, api_key):
        # Create a QThread object
        self.thread = QThread()
        # Create the worker object
        self.worker = APIUserPreferenceWorker(api_key)
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.user_settings.connect(self.set_user_settings)
        # Start the thread
        self.thread.start()
        # Set buttons to loading state
        self.start_button.set_validating_api_key()
        self.status_label.set_validating_api_key()

    def set_user_settings(self, user_settings_dict):
        api_key_valid = user_settings_dict.get("api_key_valid")
        telemetry_enabled = user_settings_dict.get("telemetry_enabled")
        subscription_plan = user_settings_dict.get("subscription_plan")
        subscription_expires = user_settings_dict.get("subscription_expires")
        if (api_key_valid and subscription_plan) or (self.api_key == 'F1LAPS_TESTER'):
            log.info("Valid API key and subscription. Starting session...")
            self.display_subscription_information(subscription_plan, subscription_expires)
            self.start_button.set_running()
            self.status_label.set_running()
            # Actually start receiver thread
            self.session.start(self.api_key, enable_telemetry=telemetry_enabled,
                               use_udp_broadcast=self.broadcast_mode_enabled,
                               ip_value=self.get_ip_value(),
                               port_value=self.get_port_value(),
                               redirect_host=self.get_redirect_host_value(),
                               redirect_port=self.get_redirect_port_value(),
                               use_udp_redirect=self.udp_redirect_enabled

                               )
        else:
            log.info("Not starting Telemetry session (api key %s, subscription %s)" % \
                     ("valid" if api_key_valid else "invalid", subscription_plan if subscription_plan else "not set"))
            self.display_subscription_information(subscription_plan, subscription_expires)
            self.start_button.reset()
            self.api_key_field.setDisabled(False)
            self.port_value_field.setReadOnly(False)
            self.udp_broadcast_checkbox.setDisabled(False)
            self.status_label.set_invalid_api_key()

    def get_ip_value(self):
        self.ip_value = self.ip_value_field.text()
        # Make sure IP is valid, otherwise revert to default
        try:
            socket.inet_aton(self.ip_value)
            # Save user value in config
            self.user_config.set("IP_VALUE", self.ip_value)
        except socket.error:
            self.ip_value = get_local_ip()
            # Update in UI if we reverted it
            self.ip_value_field.setText(self.ip_value)
        return str(self.ip_value)

    def get_port_value(self):
        self.port_value = self.port_value_field.text()
        # Make sure port is integer, otherwise fall back to default port
        try:
            self.port_value = str(int(self.port_value))
            # Save user value in config
            self.user_config.set("PORT_VALUE", self.port_value)
        except:
            self.port_value = DEFAULT_PORT
            # Update in UI if we reverted it
            self.port_value_field.setText(str(self.port_value))
        return int(self.port_value)

    def get_redirect_port_value(self):
        self.redirect_port_value = self.redirect_port_field.text()
        # Make sure port is integer, otherwise fall back to default port
        try:
            self.redirect_port_value = str(int(self.redirect_port_value))
            # Save user value in config
            self.user_config.set("REDIRECT_PORT_VALUE", self.redirect_port_value)
        except:
            self.redirect_port_value = DEFAULT_REDIRECT_PORT
            # Update in UI if we reverted it
            self.redirect_port_field.setText(str(self.redirect_port_value))
        return int(self.redirect_port_value)

    def get_redirect_host_value(self):
        self.redirect_host_value = self.redirect_host_field.text()
        # Make sure IP is valid, otherwise revert to default
        try:
            socket.inet_aton(self.redirect_host_value)
            # Save user value in config
            self.user_config.set("REDIRECT_HOST_VALUE", self.redirect_host_value)
        except socket.error:
            self.redirect_host_value = DEFAULT_REDIRECT_HOST
            # Update in UI if we reverted it
            self.redirect_host_field.setText(self.redirect_host_value)
        return str(self.redirect_host_value)

    def display_subscription_information(self, plan, expires_at):
        """ Plan and expires at are only returned if it's active """
        if plan:
            sub_text = "Subscribed to F1Laps %s plan" % plan
            self.subscription_label.setStyleSheet("color: #6B7280")
        else:
            sub_text = "You have no active F1Laps subscription. <a href='https://www.f1laps.com/telemetry'>Please subscribe now.</a>"
            self.subscription_label.setStyleSheet("color: #B45309")
        self.subscription_label.setText(sub_text)

    def stop_telemetry(self):
        if not self.session.is_active:
            log.error("Session can't be stopped as there is no active session")
            return None
        self.session.kill()
        return None
