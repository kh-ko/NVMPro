from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QFrame, QHBoxLayout
from qfluentwidgets import (FluentWidget, CommandBar, SegmentedWidget, Action, TransparentPushButton,
                            TransparentDropDownPushButton, RoundMenu, FluentIcon, setCustomStyleSheet)
from .home_viewmodel import HomeViewModel

class HomeWindow(FluentWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NVMPro")
        self.setWindowIcon(QIcon("data/assets/image/nova_icon.ico"))  # 리소스 시스템 적용 시
        self.resize(1024, 710)

        # 1. 메인 레이아웃 설정
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 30, 0, 0)  # CommandBar 공간 확보를 위해 Top 마진 조절
        self.main_layout.setSpacing(10)

        # 2. CommandBar 배경 강제 적용을 위한 컨테이너 생성
        # qFluentWidgets의 CommandBar 자체가 QSS 색상 적용을 무시할 수 있으므로 QFrame으로 감쌉니다.
        self.command_bar_container = QFrame(self)
        self.command_bar_container.setObjectName("commandBarContainer")
        self.command_bar_container.setStyleSheet(
            "#commandBarContainer {"
            "    background-color: rgba(0, 120, 212, 1);"
            "}"
        )

        self.command_bar_layout = QHBoxLayout(self.command_bar_container)
        self.command_bar_layout.setContentsMargins(4, 4, 4, 4)  # 여백 조절

        self.command_bar = CommandBar(self.command_bar_container)
        
        # [오류 수정] 창이 좁아져서 '...' 더보기 메뉴가 뜰 때 발생하는 QFont 계산 에러 방지
        #from PySide6.QtGui import QFont
        #self.command_bar.setFont(QFont("Segoe UI", 10))
        
        self.command_bar_layout.addWidget(self.command_bar)

        # 메뉴 항목들 추가
        self._setup_command_bar()

        # 레이아웃 최상단에 CommandBar가 담긴 컨테이너(QFrame) 추가
        self.main_layout.addWidget(self.command_bar_container)

        # 나머지 영역은 나중에 ChartView 등이 차지하게 됩니다.
        self.main_layout.addStretch(1)

        # UI 생성이 끝난 후 ViewModel 생성 및 View(self) 주입
        self.viewmodel = HomeViewModel(self)

    def _setup_command_bar(self):
        """커맨드 바에 Local/Remote 모드 선택용 SegmentedWidget을 구성합니다."""

        # 1. SegmentedWidget 생성
        self.mode_selector = SegmentedWidget(self)

        # 2. 아이템 추가 (식별자 키, 화면에 보일 텍스트)
        local_item = self.mode_selector.addItem('local', 'Local')
        remote_item = self.mode_selector.addItem('remote', 'Remote')

        # 선택 시(검은색) / 미선택 시(하얀색) 글씨 색상을 지정합니다.
        # qFluentWidgets의 SegmentedItem은 내부적으로 'isSelected' 속성(Property)을 가지고 있습니다.
        segmented_qss = (
            "SegmentedItem { color: white; }\n"
            "SegmentedItem[isSelected=true] { color: black; }"
        )
        setCustomStyleSheet(local_item, segmented_qss, segmented_qss)
        setCustomStyleSheet(remote_item, segmented_qss, segmented_qss)

        # 3. 초기 선택값 강제 지정 (시작할 때 Local에 불이 들어오게 함)
        self.mode_selector.setCurrentItem('local')

        # 5. CommandBar에 위젯으로 추가
        self.command_bar.addWidget(self.mode_selector)

        # 구분선 추가
        self.command_bar.addSeparator()
        
        # ---------------------------------------------------------
        # 2. CommandBar에 글자가 보이는 버튼 추가 (수정된 부분)
        # ---------------------------------------------------------
        
        # CommandBar는 원래 Action을 추가해 내부적으로 CommandButton을 생성해야,
        # 창이 좁아졌을 때 나타나는 ... (더보기) 메뉴로 항목들이 정상 이관됩니다.
        self.log_action = Action(FluentIcon.ADD, "Show Log", self)
        self.log_btn = self.command_bar.addAction(self.log_action)
        self.log_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        self.port_select_action = Action(FluentIcon.ADD, "Port Select", self)
        self.port_select_btn = self.command_bar.addAction(self.port_select_action)
        self.port_select_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
