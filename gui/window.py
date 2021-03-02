from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
import logging

from lib.logger import log, get_path
from receiver.receiver import RaceReceiver
from receiver.helpers import get_local_ip
import config


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.api_key_field = None
        self.start_button = None
        self.app_version = config.VERSION

        # Draw the windw UI
        self.init_ui()

        # Show the IP to the user
        self.set_ip()

        # Track if we have an active receiver
        # A receiver process can only run once
        self.session = None


    def init_ui(self):
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

        # 2) Check IP section
        ip_value_label = QLabel()
        ip_value_label.setText("2) Check your F1 game Telemetry IP setting")
        ip_value_label.setText(get_path())
        ip_value_label.setObjectName("ipValueLabel")
        ip_value_label.setContentsMargins(0, 20, 0, 0)
        ip_value_help_text_label = QLabel()
        ip_value_help_text_label.setText("You can ignore this step if you're running this program on the same computer as the F1 game. Otherwise, open Settings --> Telemetry in the F1 game, and make sure the IP setting is set to this value.")
        ip_value_help_text_label.setObjectName("ipValueHelpTextLabel")
        ip_value_help_text_label.setWordWrap(True)
        self.ip_value = QLabel()
        self.ip_value.setObjectName("ipValueField")
        self.ip_value.setContentsMargins(0, 5, 0, 20)

        # Start/Stop button
        start_button = QPushButton('Start Telemetry')
        start_button.setObjectName("startStopButton")
        start_button.clicked.connect(lambda: self.start_button_click())
        start_button.setFixedSize(160, 45)
        self.start_button = start_button

        help_text_label = QLabel()
        help_text_label.setText("Need help? <a href='https://www.notion.so/F1Laps-Telemetry-Documentation-55ad605471624066aa67bdd45543eaf7'>Check out the Documentation & Help Center!</a>")
        help_text_label.setObjectName("helpTextLabel")
        help_text_label.setOpenExternalLinks(True)
        help_text_label.setContentsMargins(0, 40, 0, 0)
        app_version_label = QLabel()
        app_version_label.setText("You're using F1Laps Telemetry version %s" % self.app_version)
        app_version_label.setObjectName("appVersionLabel")

        # Draw layout
        layout = QVBoxLayout()

        # API key section
        layout.addWidget(api_key_field_label)
        layout.addWidget(api_key_help_text_label)
        layout.addWidget(self.api_key_field)

        # IP section
        layout.addWidget(ip_value_label)
        layout.addWidget(ip_value_help_text_label)
        layout.addWidget(self.ip_value)

        # Start button
        layout.addWidget(start_button, alignment=Qt.AlignCenter)

        # Status & help
        layout.addWidget(help_text_label)
        layout.addWidget(app_version_label)

        layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(layout)
        self.setWindowTitle("F1Laps Telemetry") 
        #self.resize(500, 600)
        log.info("Welcome to F1Laps Telemetry! You will see all logging in this text field.")


    def set_ip(self):
        self.ip_value.setText(get_local_ip())


    def start_button_click(self):
        if not self.session:
            log.info("Starting new session")
            self.session = self.start_telemetry()
            self.start_button.setText("Stop Telemetry")
        else:
            log.info("Stopping session")
            self.session = self.stop_telemetry()
            self.start_button.setText("Start Telemetry")


    def start_telemetry(self):
        if self.session:
            log.error("A new session can't be started when another one is active")
            return self.session
        # Get API key from input field
        api_key = self.api_key_field.text()
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
