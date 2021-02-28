from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QPlainTextEdit, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging

from lib.logger import log
from receiver.receiver import RaceReceiver
from receiver.helpers import get_local_ip
import config


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum()) 


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
        ip_value_label.setObjectName("ipValueLabel")
        ip_value_help_text_label = QLabel()
        ip_value_help_text_label.setText("You can ignore this step if you're running this program on the same computer as the F1 game. Otherwise, open Settings --> Telemetry in the F1 game, and make sure the IP setting is set to this value.")
        ip_value_help_text_label.setObjectName("ipValueHelpTextLabel")
        ip_value_help_text_label.setWordWrap(True)
        self.ip_value = QLabel()
        self.ip_value.setObjectName("ipValueField")

        # Start/Stop button
        start_button = QPushButton('Start Telemetry')
        start_button.setObjectName("startStopButton")
        start_button.clicked.connect(lambda: self.start_button_click())
        self.start_button = start_button

        # Status logging & help text
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.HLine)
        horizontal_line.setFrameShadow(QFrame.Sunken)
        horizontal_line.setObjectName("horizontalLine")
        status_heading_label = QLabel()
        status_heading_label.setText("Status")
        status_heading_label.setObjectName("statusHeadingLabel")
        logger_field = QTextEditLogger(self)
        logger_field.widget.setObjectName("loggerField")
        logger_field.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        log.addHandler(logger_field)
        help_text_label = QLabel()
        help_text_label.setText("Need help? <a href='https://www.notion.so/F1Laps-Telemetry-Documentation-55ad605471624066aa67bdd45543eaf7'>Check out the Documentation & Help Center!</a>")
        help_text_label.setObjectName("helpTextLabel")
        help_text_label.setOpenExternalLinks(True)
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
        layout.addWidget(start_button)
        layout.setAlignment(start_button, Qt.AlignLeft)

        # Status & help
        layout.addWidget(horizontal_line)
        layout.addWidget(status_heading_label)
        layout.addWidget(logger_field.widget)
        layout.addWidget(help_text_label)
        layout.addWidget(app_version_label)

        layout.setContentsMargins(40, 32, 40, 35)
        
        self.setLayout(layout)
        self.setWindowTitle("F1Laps Telemetry") 
        self.resize(800, 500)
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
        try:
            receiver_thread = RaceReceiver(api_key)
            receiver_thread.start()
        except Exception as ex:
            log.error("Encountered exception %s on receiver thread" % ex, exc_info=True)
            raise Exception
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
