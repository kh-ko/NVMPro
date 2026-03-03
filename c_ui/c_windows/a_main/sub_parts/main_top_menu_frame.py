from PySide6.QtWidgets import QFrame, QHBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from c_ui.b_components.a_custom.base_tool_bar import BaseToolBar
from c_ui.a_global.ntheme import NTheme 
from c_ui.b_components.a_custom.base_switch_button import BaseSwitchButton

class MainTopMenuFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainTopMenuFrame")
        self.setFixedHeight(42)

        # 1. 가로 배치(QHBoxLayout)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(10) # 위젯 사이의 간격

        # 2. Local / Remote 커스텀 스위치 추가
        # (생성 시 파라미터로 라벨을 바로 넘길 수 있습니다)
        self.acc_switch = BaseSwitchButton("Local", "Remote", self)   
        self.layout.addWidget(self.acc_switch)

        # 3. 위젯 사이의 세로 구분선 (Visual Separator)
        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.VLine) # 세로줄
        self.separator.setFrameShadow(QFrame.Plain)
        self.separator.setObjectName("menuSeparator")
        self.layout.addWidget(self.separator)

        # 4. 일반 메뉴 툴바 추가
        self.toolbar = BaseToolBar(self)
        self.toolbar.setObjectName("mainToolBar")
        self.layout.addWidget(self.toolbar)

        # 5. 남는 여백을 우측으로 밀어주어 왼쪽 정렬 유지
        self.layout.addStretch()

        self._setup_actions()

        # 테마 매니저 연동
        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)        

        self._apply_design()

    def _setup_actions(self):
        # 툴바에는 순수한 일반 메뉴 Action들만 추가합니다.
        self.action_connection = QAction("Connection", self)
        self.action_parameter = QAction("Parameter", self)
        self.action_logview = QAction("LogView", self)
        self.action_help = QAction("Help", self)

        self.toolbar.addAction(self.action_connection)
        self.toolbar.addAction(self.action_parameter)
        self.toolbar.addAction(self.action_logview)
        self.toolbar.addAction(self.action_help)

    def _apply_design(self):
        self._apply_theme_colors()

    def _apply_theme_colors(self, theme_name=None):
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        separator_color = self.theme_manager.get_color("separator_color")

        # QPushButton과 관련된 스타일은 CustomModeSwitch에서 알아서 처리하므로 
        # 여기서는 프레임과 구분선 스타일만 남깁니다.
        self.setStyleSheet(f"""
            QFrame#mainTopMenuFrame {{
                background-color: {frame_bg_color};
                border: none;
            }}
            
            /* 세로 구분선 색상 지정 */
            QFrame#menuSeparator {{
                color: {separator_color};
                min-width: 1px;
                max-width: 1px;
                min-height: 20px;
                max-height: 20px;
            }}
        """)