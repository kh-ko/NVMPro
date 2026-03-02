from PySide6.QtWidgets import QFrame
from c_ui.a_global.ntheme import NTheme

class HomePressureFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePressureFrame")

        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        # 테마 매니저에서 현재 테마에 맞는 색상값을 꺼내옵니다.
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        border_color = self.theme_manager.get_color("border_color")

        # QSS(Qt Style Sheets)를 이용해 현재 프레임의 색상을 변경합니다.
        self.setStyleSheet(f"""
            QFrame#homePressureFrame {{
                background-color: {frame_bg_color}; 
                border-right: 1px solid {border_color};
                border-radius: 0px;
            }}
        """)        