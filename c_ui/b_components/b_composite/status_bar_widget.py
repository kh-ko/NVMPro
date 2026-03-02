from PySide6.QtWidgets import QFrame, QHBoxLayout
from c_ui.b_components.a_custom.base_caption_label import BaseCaptionLabel
from c_ui.a_global.ntheme import NTheme

class StatusBarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBarFrame")

        self.container = QHBoxLayout(self)

        self.connection_info = BaseCaptionLabel("COM3-38400-8-N-1", self)
        self.container.addWidget(self.connection_info)

        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        self.setFixedHeight(23)
        self.container.setContentsMargins(10, 0, 10, 0)  # 여백 조절

        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        # 테마 매니저에서 현재 테마에 맞는 색상값을 꺼내옵니다.
        bg_color = self.theme_manager.get_color("border_color")
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")

        # QSS(Qt Style Sheets)를 이용해 현재 프레임의 색상을 변경합니다.
        self.setStyleSheet(f"""
            QFrame#statusBarFrame {{
                background-color: {frame_bg_color};
                border-top: 1px solid {bg_color};
                border-radius: 0px;
            }}
        """)
