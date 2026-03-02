from PySide6.QtWidgets import QLabel

class NCaptionLabel(QLabel):
    """폰트 크기가 8px로 고정된 커스텀 QLabel"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        #폰트 사이즈만 8 pt로 설정
        font = self.font()
        font.setPointSize(8)
        self.setFont(font)
