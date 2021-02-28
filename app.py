from PyQt5.QtWidgets import QApplication
from pathlib import Path
import sys
import os

from gui.window import MainWindow
from gui.styles import GUI_STYLES
from lib.logger import log


if __name__ == '__main__':
    try:
        # Create App
        app = QApplication(sys.argv)
        app.setStyleSheet(GUI_STYLES)

        # Create & show UI window
        window = MainWindow()
        window.show()

        # Handle window close
        exit_code = app.exec_()
        sys.exit(exit_code)
    except Exception as ex:
        log.error("Encountered exception %s on main thread" % ex, exc_info=True)
        raise Exception