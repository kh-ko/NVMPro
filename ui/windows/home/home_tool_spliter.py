from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt
from .home_status_frame import HomeStatusFrame
from .home_control_frame import HomeControlFrame
from .home_position_frame import HomePositionFrame
from .home_pressure_frame import HomePressureFrame
from ui.theme.ntheme import NTheme

class HomeToolSpliter(QSplitter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeToolSpliter")
        self.setFixedHeight(300)

        self.setOrientation(Qt.Orientation.Horizontal)

        # 4개의 프레임 인스턴스 생성
        self.status_frame = HomeStatusFrame(self)
        self.control_frame = HomeControlFrame(self)
        self.position_frame = HomePositionFrame(self)
        self.pressure_frame = HomePressureFrame(self)

        # Splitter에 4개의 프레임을 순서대로 추가
        self.addWidget(self.status_frame)
        self.addWidget(self.control_frame)
        self.addWidget(self.position_frame)
        self.addWidget(self.pressure_frame)
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
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        border_color = self.theme_manager.get_color("border_color")

        self.setStyleSheet(f"""
            QSplitter#homeToolSpliter {{
                background-color: {frame_bg_color};
                border-top: 1px solid {border_color};
                border-bottom: 0px;
                border-left: 0px;
                border-right: 0px;
                border-radius: 0px;
            }}
            
            /* 스플리터의 구분자(핸들) 영역을 완전히 투명하게 설정 */
            QSplitter::handle {{
                background-color: transparent;
                border: none;
                image: none;  /* <--- 이 줄을 추가하면 가운데 짧은 선이 사라집니다! */
            }}
        """)