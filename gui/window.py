from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, \
                            QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtSvg import QSvgWidget
import logging
import requests

from gui.base_classes import F1QLabel
from gui.workers import APIUserPreferenceWorker
from lib.logger import log
from lib.file_handler import ConfigFile, get_path_temporary
from receiver.receiver import RaceReceiver
from receiver.helpers import get_local_ip
import config

F1LAPS_VERSION_ENDPOINT = "https://www.f1laps.com/api/f12020/telemetry/app/version/current/"
F1LAPS_USER_SETTINGS_ENDPOINT = "https://www.f1laps.com/api/f12020/telemetry/app/user/settings/"


class QHSeperationLine(QFrame):
    """ Horizontal seperation line """
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVSpacer(QLabel):
    """ Vertical empty space """
    def __init__(self, height):
        super().__init__()
        self.setText(" ")
        self.setFixedHeight(height)


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
        self.setText("Checking API key...")
    
    def set_running(self):
        self.setText("Status: running")

    def reset(self):
        self.setText("Status: not started")


class TelemetrySession:
    def __init__(self):
        # The actual receiver session
        self.session = None
        self.is_active = False

    def start(self, api_key):
        receiver_thread = RaceReceiver(api_key)
        receiver_thread.start()
        self.is_active = True
        log.info("Started receiver tread")
        return True

    def kill(self):
        self.session.kill()
        self.is_active = False
        log.info("Stopped receiver tread")
        return True


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key_field = None
        self.api_key = ConfigFile().get_api_key()
        self.app_version = config.VERSION
        # Draw the window UI
        self.init_ui()
        # Show the IP to the user
        self.set_ip()
        # Check if there's a new version
        self.check_version()
        # Track if we have an active receiver
        self.session = TelemetrySession()

    def init_ui(self):
        # 1) Logo & heading
        logo_label = QSvgWidget(get_path_temporary('logo.svg'))
        logo_label.setFixedSize(100, 28)

        # 1) Enter API key section
        api_key_field_label = F1QLabel()
        api_key_field_label.setText("1) Enter your API key")
        api_key_field_label.setObjectName("apiKeyFieldLabel")
        api_key_help_text_label = F1QLabel()
        api_key_help_text_label.setText("You can find your API key on the <a href='https://www.f1laps.com/api/telemetry_apps'>F1Laps Telemetry page</a>")
        api_key_help_text_label.setObjectName("apiKeyHelpTextLabel")
        self.api_key_field = QLineEdit()
        self.api_key_field.setObjectName("apiKeyField")
        self.api_key_field.setText(self.api_key)

        # 2) Check IP section
        ip_value_label = F1QLabel()
        ip_value_label.setText("2) Check your F1 game Telemetry IP setting")
        ip_value_label.setObjectName("ipValueLabel")
        ip_value_help_text_label = F1QLabel()
        ip_value_help_text_label.setText("You can ignore this step if you're running this program on the same computer as the F1 game. Otherwise open Settings -> Telemetry in the F1 game and set the IP to this value.")
        ip_value_help_text_label.setObjectName("ipValueHelpTextLabel")
        ip_value_help_text_label.setWordWrap(True)
        self.ip_value = F1QLabel()
        self.ip_value.setObjectName("ipValueField")
        self.ip_value.setContentsMargins(0, 5, 0, 0)

        # Start/Stop button
        self.start_button = StartButton()
        self.start_button.clicked.connect(lambda: self.start_button_click())
        self.status_label = StatusLabel()

        help_text_label = F1QLabel()
        help_text_label.setText("Need help? <a href='https://www.notion.so/F1Laps-Telemetry-Documentation-55ad605471624066aa67bdd45543eaf7'>Check out the Documentation & Help Center!</a>")
        help_text_label.setObjectName("helpTextLabel")
        help_text_label.setOpenExternalLinks(True)
        self.app_version_label = F1QLabel()
        self.app_version_label.setText("You're using app version %s." % self.app_version)
        self.app_version_label.setObjectName("appVersionLabel")
        self.subscription_label = F1QLabel()
        self.subscription_label.setObjectName("subscriptionLabel")

        # Draw layout
        self.layout = QVBoxLayout()

        # Logo section
        self.layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(QHSeperationLine())

        # API key & IP section
        self.layout.addWidget(QVSpacer(0))
        self.layout.addWidget(api_key_field_label)
        self.layout.addWidget(api_key_help_text_label)
        self.layout.addWidget(self.api_key_field)

        self.layout.addWidget(QVSpacer(10))
        self.layout.addWidget(ip_value_label)
        self.layout.addWidget(ip_value_help_text_label)
        self.layout.addWidget(self.ip_value)

        # Start button
        self.layout.addWidget(QVSpacer(2))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(QVSpacer(5))
        self.layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Status & help
        self.layout.addWidget(QVSpacer(3))
        self.layout.addWidget(QHSeperationLine())
        self.layout.addWidget(help_text_label)
        self.layout.addWidget(self.app_version_label)
        self.layout.addWidget(self.subscription_label)
        self.layout.setContentsMargins(30, 20, 30, 30)
        
        self.setLayout(self.layout)
        self.setFixedWidth(420)
        self.setWindowTitle("F1Laps Telemetry") 
        log.info("Welcome to F1Laps Telemetry! You will see all logging in this text field.")

    def set_ip(self):
        self.ip_value.setText(get_local_ip())

    def get_api_key(self):
        """ Get API key from user input field and store it in local file """
        api_key = self.api_key_field.text()
        ConfigFile().set_api_key(api_key)
        return api_key

    def check_version(self):
        try:
            response = requests.get(F1LAPS_VERSION_ENDPOINT)
            version = response.json()['version']
            user_version_int = int(self.app_version.replace(".", ""))
            current_version_int = int(version.replace(".", ""))
            if version > self.app_version:
                self.app_version_label.setText("There's a new app version available (you're on v%s).<br><a href='https://www.f1laps.com/api/telemetry_apps'>Click here to download the new version!</a>" % self.app_version)
                self.app_version_label.setStyleSheet("color: #B45309")
            elif version < self.app_version:
                self.app_version_label.setText("This is pre-release version v%s (stable version is v%s)." % (self.app_version, version))
                self.app_version_label.setStyleSheet("color: #059669")
        except Exception as ex:
            log.warning("Couldn't get most recent version from F1Laps due to: %s" % ex)

    def start_button_click(self):
        if not self.session.is_active:
            log.info("Starting new session")
            self.start_telemetry()
        else:
            log.info("Stopping session")
            self.session = self.stop_telemetry()
            self.start_button.setText("Start Telemetry")
            self.start_button.setStyleSheet("background-color: #4338CA;")
            self.status_label.setText("Status: stopped")

    def start_telemetry(self):
        if self.session.is_active:
            log.error("A new session can't be started when another one is active")
            return False
        # Get API key from input field
        api_key = self.get_api_key()
        # Validate API key via F1Laps API
        self.validate_api_key(api_key)

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
        if api_key_valid:
            log.info("Starting Telemetry session")
            self.start_button.set_running()
            self.status_label.set_running()
            # Actually start receiver thread
            self.session.start(api_key)
        else:
            log.info("Not starting Telemetry session")
            self.start_button.reset()
            self.status_label.reset()


    def stop_telemetry(self):
        if not self.session.is_active:
            log.error("Session can't be stopped as there is no active session")
            return None
        self.session.kill()
        log.debug("Session has been stopped")
        return None
