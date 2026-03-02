from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout, QWidget
from .home_viewmodel import HomeViewModel
from .home_mainmenu_frame import HomeMainMenuFrame
from .home_chart_frame import HomeChartFrame
from .home_status_frame import HomeStatusFrame
from .home_position_frame import HomePositionFrame
from .home_pressure_frame import HomePressureFrame
from .home_control_frame import HomeControlFrame
from ui.components.statusbar_frame import StatusBarFrame
from .home_tool_spliter import HomeToolSpliter

class HomeWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NVMPro")
        #self.setWindowIcon(QIcon("data/assets/image/nova_icon.ico"))  # 리소스 시스템 적용 시
        self.resize(1024, 710)

        # 1. 메인 레이아웃 설정
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # CommandBar 공간 확보를 위해 Top 마진 조절
        self.main_layout.setSpacing(0)

        # 2. CommandBar 추가
        self.mainmenu_frame = HomeMainMenuFrame(self)
        self.main_layout.addWidget(self.mainmenu_frame)

        # Body 영역 (상하 2등분 분리)
        # 상단: 차트 뷰 등이 차지할 영역 (나머지 공간 꽉 채움)
        self.chart_frame = HomeChartFrame(self)
        self.main_layout.addWidget(self.chart_frame, 1)
        # 하단 : Body영역의 하단에 위치하며 status, control, position, pressure 프레임을 담을 컨테이너 영역
        self.tool_splitter = HomeToolSpliter(self)
        self.main_layout.addWidget(self.tool_splitter)

        # 3. StatusBar 추가 (하단 영역)
        self.status_bar_frame = StatusBarFrame(self)
        self.main_layout.addWidget(self.status_bar_frame)

        # CommandBar의 레이아웃 그림자가 아래 위젯(ChartWidget 등)에
        # 가려지지 않도록 Z-order를 최상단으로 끌어올립니다.
        self.mainmenu_frame.raise_()

        # UI 생성이 끝난 후 ViewModel 생성 및 View(self) 주입
        self.viewmodel = HomeViewModel(self)
