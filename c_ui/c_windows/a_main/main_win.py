from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSplitter
from .sub_parts.main_top_menu_frame import MainTopMenuFrame
from .sub_parts.main_chart_frame import MainChartFrame
from .sub_parts.main_valve_status_frame import MainValveStatusFrame
from .sub_parts.main_valve_control_mode_frame import MainValveControlModeFrame
from .sub_parts.main_position_frame import MainPositionFrame
from .sub_parts.main_pressure_frame import MainPressureFrame
from c_ui.b_components.b_composite.status_bar_widget import StatusBarWidget
from c_ui.a_global.ntheme import NTheme
from .main_viewmodel import MainViewModel

class MainWin(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NVMPro")
        self.resize(1024, 710)

        # 1. 메인 레이아웃 설정
        self.main_layout = QVBoxLayout(self)

        # 2. CommandBar 추가
        self.top_menu_frame = MainTopMenuFrame(self)
        self.main_layout.addWidget(self.top_menu_frame)

        # Body 영역 (상하 2등분 분리)
        # 상단: 차트 뷰 등이 차지할 영역 (나머지 공간 꽉 채움)
        self.chart_frame = MainChartFrame(self)
        self.main_layout.addWidget(self.chart_frame, 1)
        # 하단 : Body영역의 하단에 위치하며 status, control, position, pressure 프레임을 담을 컨테이너 영역
        self.tool_splitter = QSplitter(self)
        self.tool_splitter.setObjectName("mainToolSpliter")

        self.valve_status_frame = MainValveStatusFrame(self)
        self.valve_control_mode_frame = MainValveControlModeFrame(self)
        self.position_frame = MainPositionFrame(self)
        self.pressure_frame = MainPressureFrame(self)

        self.tool_splitter.addWidget(self.valve_status_frame)
        self.tool_splitter.addWidget(self.valve_control_mode_frame)
        self.tool_splitter.addWidget(self.position_frame)
        self.tool_splitter.addWidget(self.pressure_frame)

        self.main_layout.addWidget(self.tool_splitter)

        # 3. StatusBar 추가 (하단 영역)
        self.status_bar_frame = StatusBarWidget(self)
        self.main_layout.addWidget(self.status_bar_frame)

        # CommandBar의 레이아웃 그림자가 아래 위젯(ChartWidget 등)에
        # 가려지지 않도록 Z-order를 최상단으로 끌어올립니다.
        self.top_menu_frame.raise_()

        # UI 생성이 끝난 후 ViewModel 생성 및 View(self) 주입
        self.viewmodel = MainViewModel(self)

        self.theme_manager = NTheme()  # 싱글톤이므로 어디서 호출하든 같은 객체입니다.
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        self.resize(1024, 710)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.tool_splitter.setFixedHeight(300)

        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        border_color = self.theme_manager.get_color("border_color")

        self.setStyleSheet(f"""
            QSplitter#mainToolSpliter {{
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
