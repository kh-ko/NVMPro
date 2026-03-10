from PySide6.QtWidgets import QWidget, QHBoxLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt
from c_ui.b_components.a_custom.custom_caption import CustomCaption

class AppStatusBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 3, 10, 3)
        self.main_layout.setSpacing(10)

        # 1. 왼쪽: 상태 캡션 (고정 너비)
        self.status_caption = CustomCaption("Status")
        self.main_layout.addWidget(self.status_caption)

        self.main_layout.addStretch()
