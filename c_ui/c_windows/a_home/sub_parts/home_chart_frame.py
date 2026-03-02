from PySide6.QtWidgets import QFrame
from c_ui.a_global.ntheme import NTheme

class HomeChartFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeChartFrame")

        # ---------------------------------------------------------
        # 1. 테마 매니저 인스턴스 가져오기 및 이벤트(시그널) 연결
        # ---------------------------------------------------------
        self.theme_manager = NTheme()  # 싱글톤이므로 어디서 호출하든 같은 객체입니다.
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        # 테마 매니저에서 현재 테마에 맞는 색상값을 꺼내옵니다.
        border_color = self.theme_manager.get_color("border_color")
        chart_bg_color = self.theme_manager.get_color("chart_bg_color")

        # QSS(Qt Style Sheets)를 이용해 현재 프레임의 색상을 변경합니다.
        self.setStyleSheet(f"""
            QFrame#homeChartFrame {{
                background-color: {chart_bg_color};
                border-top: 1px solid {border_color};
                border-radius: 0px;
            }}
        """)