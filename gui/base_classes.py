from PyQt5.QtWidgets import QLabel, QFrame


class F1QLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.setWordWrap(True)


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