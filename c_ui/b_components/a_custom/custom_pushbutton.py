from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize

class CustomButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("padding: 5px 20px;")