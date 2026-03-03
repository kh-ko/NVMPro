from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from c_ui.a_global.ntheme import NTheme
from c_ui.b_components.a_custom.base_tool_bar import BaseToolBar
from c_ui.b_components.b_composite.status_bar_widget import StatusBarWidget

class BaseWin(QWidget):
    def __init__(self):
        super().__init__()

        self._toolbar_actions = {}

        # 1. 전체 메인 레이아웃 (수직 배치)
        self.main_layout = QVBoxLayout(self)

        # 2. 상단 툴바 배치
        self.tool_bar = BaseToolBar(self)
        self.main_layout.addWidget(self.tool_bar)

        # 3. 중앙 스크롤 영역 설정 (Body)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame) # 경계선 제거
        
        # 스크롤 영역 안에 담길 실제 위젯과 레이아웃
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        
        
        self.scroll_area.setWidget(self.body_container)
        self.main_layout.addWidget(self.scroll_area)

        # 4. 하단 상태바 배치
        self.status_bar = StatusBarWidget(self)
        self.main_layout.addWidget(self.status_bar)

        # 5. 테마 매니저 설정
        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    def _apply_design(self):
        # 기본 사이즈 설정 (필요시 조절)
        self.resize(800, 600)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.body_layout.setContentsMargins(10, 10, 10, 10) # 기본 여백 설정

        self._apply_theme_colors()

    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        bg_color = self.theme_manager.get_color("frame_bg_color")
        
        # 전체 배경색 및 스크롤 영역 배경 설정
        self.setStyleSheet(f"""
            BaseWin {{
                background-color: {bg_color};
            }}
        """)
        
    def add_action(self, text, callback, checkable=False):
        """
        툴바에 버튼(Action)을 추가합니다.
        :param text: 버튼에 표시될 텍스트
        :param callback: 클릭 시 실행될 함수
        :param checkable: 토글 버튼 여부
        """
        action = QAction(text, self)
        action.setCheckable(checkable)
        action.triggered.connect(callback)
        
        self.tool_bar.addAction(action)
        self._toolbar_actions[text] = action  # 관리를 위해 저장
        return action

    def clear_actions(self):
        """툴바의 모든 액션을 제거합니다."""
        self.tool_bar.clear()
        self._toolbar_actions.clear()

    def disable_action(self, text, disable=True):
        """
        특정 액션을 비활성화 또는 활성화합니다.
        :param text: 추가할 때 사용한 버튼 텍스트
        :param disable: True면 비활성화, False면 활성화
        """
        action = self._toolbar_actions.get(text)
        if action:
            action.setEnabled(not disable)