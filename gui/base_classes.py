from PyQt5.QtWidgets import QLabel

class F1QLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.setWordWrap(True)