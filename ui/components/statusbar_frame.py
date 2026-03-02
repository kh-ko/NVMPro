from PySide6.QtWidgets import QFrame, QHBoxLayout
from ui.components.ncaption_label import NCaptionLabel
from ui.theme.ntheme import NTheme

class StatusBarFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBarFrame")

        self.setFixedHeight(23)

        self.container = QHBoxLayout(self)
        self.container.setContentsMargins(10, 0, 10, 0)  # 여백 조절

        self.connection_info = NCaptionLabel("COM3-38400-8-N-1", self)

        # 레이아웃에 배치
        self.container.addWidget(self.connection_info)
        
        # ---------------------------------------------------------
        # 1. 테마 매니저 인스턴스 가져오기 및 이벤트(시그널) 연결
        # ---------------------------------------------------------
        self.theme_manager = NTheme()  # 싱글톤이므로 어디서 호출하든 같은 객체입니다.
        
        # 테마가 바뀔 때(theme_changed) _apply_theme_colors 함수가 실행되도록 연결(connect)합니다.
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        # 2. 화면이 처음 생성될 때도 현재 테마 색상을 한 번 적용해 줍니다.
        self._apply_theme_colors()

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
