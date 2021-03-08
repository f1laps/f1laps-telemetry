from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, \
                            QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QPixmap
from PyQt5.QtSvg import QSvgWidget
import logging
import requests

from lib.logger import log
from lib.file_handler import ConfigFile, get_path_temporary
from receiver.receiver import RaceReceiver
from receiver.helpers import get_local_ip
import config


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


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.api_key_field = None
        self.api_key = ConfigFile().get_api_key()
        self.start_button = None
        self.app_version = config.VERSION

        # Draw the window UI
        self.init_ui()

        # Show the IP to the user
        self.set_ip()

        # Check if there's a new version
        self.check_version()

        # Track if we have an active receiver
        # A receiver process can only run once
        self.session = None


    def init_ui(self):
        # 1) Logo & heading
        logo_label = QSvgWidget(get_path_temporary('logo.svg'))
        logo_label.setFixedSize(100, 28)

        # 1) Enter API key section
        api_key_field_label = QLabel()
        api_key_field_label.setText("1) Enter your API key")
        api_key_field_label.setObjectName("apiKeyFieldLabel")
        api_key_help_text_label = QLabel()
        api_key_help_text_label.setText("You can find your API key on the <a href='https://www.f1laps.com/api/telemetry_apps'>F1Laps Telemetry page</a>")
        api_key_help_text_label.setObjectName("apiKeyHelpTextLabel")
        api_key_help_text_label.setOpenExternalLinks(True)
        self.api_key_field = QLineEdit()
        self.api_key_field.setObjectName("apiKeyField")
        self.api_key_field.setText(self.api_key)

        # 2) Check IP section
        ip_value_label = QLabel()
        ip_value_label.setText("2) Check your F1 game Telemetry IP setting")
        ip_value_label.setObjectName("ipValueLabel")
        ip_value_help_text_label = QLabel()
        ip_value_help_text_label.setText("You can ignore this step if you're running this program on the same computer as the F1 game. Otherwise open Settings -> Telemetry in the F1 game and set the IP to this value.")
        ip_value_help_text_label.setObjectName("ipValueHelpTextLabel")
        ip_value_help_text_label.setWordWrap(True)
        self.ip_value = QLabel()
        self.ip_value.setObjectName("ipValueField")
        self.ip_value.setContentsMargins(0, 5, 0, 0)

        # Start/Stop button
        self.start_button = QPushButton('Start Telemetry')
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(lambda: self.start_button_click())
        self.start_button.setFixedSize(160, 45)
        self.status_label = QLabel()
        self.status_label.setText("Status: not started")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFixedSize(100, 15)

        help_text_label = QLabel()
        help_text_label.setText("Need help? <a href='https://www.notion.so/F1Laps-Telemetry-Documentation-55ad605471624066aa67bdd45543eaf7'>Check out the Documentation & Help Center!</a>")
        help_text_label.setObjectName("helpTextLabel")
        help_text_label.setOpenExternalLinks(True)
        self.app_version_label = QLabel()
        self.app_version_label.setText("You're using app version %s." % self.app_version)
        self.app_version_label.setObjectName("appVersionLabel")
        self.app_version_label.setWordWrap(True)

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
            response = requests.get("https://www.f1laps.com/api/f12020/telemetry/app/version/current/")
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
        if not self.session:
            log.info("Starting new session")
            self.session = self.start_telemetry()
            self.start_button.setText("Stop Telemetry")
            self.start_button.setStyleSheet("background-color: #B91C1C;")
            self.status_label.setText("Status: running")
        else:
            log.info("Stopping session")
            self.session = self.stop_telemetry()
            self.start_button.setText("Start Telemetry")
            self.start_button.setStyleSheet("background-color: #4338CA;")
            self.status_label.setText("Status: stopped")


    def start_telemetry(self):
        if self.session:
            log.error("A new session can't be started when another one is active")
            return self.session
        # Get API key from input field
        api_key = self.get_api_key()
        # Start receiver thread
        receiver_thread = RaceReceiver(api_key)
        receiver_thread.start()
        log.debug("Session initiated and started")
        return receiver_thread


    def stop_telemetry(self):
        if not self.session:
            log.error("Session can't be stopped as there is no active session")
            return None
        self.session.kill()
        log.debug("Session has been stopped")
        self.session = None
        return None
