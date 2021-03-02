#!/usr/bin/env python3
from PyQt5.QtWidgets import QApplication
from pathlib import Path
import sys
import os

from gui.window import MainWindow
from gui.styles import GUI_STYLES



if __name__ == '__main__':
    # Create App
    app = QApplication(sys.argv)
    app.setStyleSheet(GUI_STYLES)

    # Create & show UI window
    window = MainWindow()
    
    window.show()

    # Handle window close
    exit_code = app.exec_()
    sys.exit(exit_code)