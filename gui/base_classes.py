from PyQt5.QtWidgets import QLabel, QFrame


class F1QLabel(QLabel):
    def __init__(self, text=None, object_name=None):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.setWordWrap(True)
        if text is not None:
            self.setText(text)
        if object_name is not None:
            self.setObjectName(object_name)


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