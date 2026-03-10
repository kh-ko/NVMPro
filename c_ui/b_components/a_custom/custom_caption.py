from PySide6.QtWidgets import QLabel

class CustomCaption(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        # 1. 현재 라벨에 기본으로 상속된 폰트 객체를 복사해 옵니다.
        font = self.font()

        # 2. 폰트 크기가 포인트(pt) 기준인지 픽셀(px) 기준인지 확인하여 70%로 축소합니다.
        # (만약 크기가 1보다 작아지면 안 되므로 최소값은 1로 보장해 줍니다)
        if font.pointSize() > 0:
            new_size = max(1, int(font.pointSize() * 0.7))
            font.setPointSize(new_size)
        elif font.pixelSize() > 0:
            new_size = max(1, int(font.pixelSize() * 0.7))
            font.setPixelSize(new_size)

        # 3. 크기가 작아진 폰트를 라벨에 다시 적용합니다.
        self.setFont(font)