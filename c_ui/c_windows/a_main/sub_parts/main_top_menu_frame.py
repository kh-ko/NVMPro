from PySide6.QtWidgets import (QFrame, QToolBar, QVBoxLayout, QToolButton)
from PySide6.QtGui import QAction, QActionGroup, QFont
from PySide6.QtCore import Qt
from c_ui.a_global.ntheme import NTheme 

class MainTopMenuFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainTopMenuFrame")
        self.setFixedHeight(42)

        self.layout = QVBoxLayout(self)
        
        self.toolbar = QToolBar(self)
        self.toolbar.setObjectName("mainToolBar")
        self.toolbar.setMovable(False)   
        self.toolbar.setFloatable(False) 
        
        self.layout.addWidget(self.toolbar)

        self._setup_actions()

        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)        

        self._apply_design()

    def _setup_actions(self):
        # 1. Local / Remote 토글 버튼
        self.action_local = QAction("Local", self)
        self.action_local.setCheckable(True)
        self.action_local.setChecked(True)

        self.action_remote = QAction("Remote", self)
        self.action_remote.setCheckable(True)

        self.mode_group = QActionGroup(self)
        self.mode_group.addAction(self.action_local)
        self.mode_group.addAction(self.action_remote)
        self.mode_group.setExclusive(True)

        self.toolbar.addAction(self.action_local)
        self.toolbar.addAction(self.action_remote)
        
        # 2. 구분선
        self.toolbar.addSeparator()

        # 3. 일반 메뉴 버튼들
        self.action_connection = QAction("Connection", self)
        self.action_parameter = QAction("Parameter", self)
        self.action_logview = QAction("LogView", self)
        self.action_help = QAction("Help", self)

        self.toolbar.addAction(self.action_connection)
        self.toolbar.addAction(self.action_parameter)
        self.toolbar.addAction(self.action_logview)
        self.toolbar.addAction(self.action_help)

        # ---------------------------------------------------------
        # 내가 추가한 Action에 해당하는 일반 버튼들에만 'menuBtn' 속성 부여
        # ---------------------------------------------------------
        for action in self.toolbar.actions():
            widget = self.toolbar.widgetForAction(action)
            if isinstance(widget, QToolButton):
                widget.setProperty("menuBtn", True)
                widget.setToolButtonStyle(Qt.ToolButtonTextOnly)

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        self.layout.setContentsMargins(10, 0, 10, 0) 
        self.layout.setSpacing(0)

        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        btn_hover_color = self.theme_manager.get_color("btn_hover_color")
        separator_color = self.theme_manager.get_color("separator_color")

        # 확장 버튼에 넣을 텍스트(유니코드). 파이썬 문자열로 처리하여 QSS에 주입합니다.
        # \ue5d4 는 Material Icons의 'more_vert' (세로 점 3개) 입니다.
        ext_icon_text = "\ue5cc"

        self.setStyleSheet(f"""
            QFrame#mainMainMenuFrame {{
                background-color: {frame_bg_color};
                border: none;
            }}
            
            QToolBar#mainToolBar {{
                background: transparent;
                border: none;
                spacing: 0px; 
            }}
            
            /* 일반 메뉴 버튼 디자인 */
            QToolButton[menuBtn="true"] {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }}
            
            QToolButton[menuBtn="true"]:hover {{
                background-color: {btn_hover_color}; 
            }}
            
            QToolButton[menuBtn="true"]:checked {{
                background-color: palette(highlight); 
                color: palette(highlighted-text);
                font-weight: bold;
            }}
            
            QToolBar::separator {{
                width: 1px;
                background-color: {separator_color};
                margin: 8px 4px; 
            }}

            /* ---------------------------------------------------------
               [아이콘 폰트 적용] 툴바 확장 버튼(...) 스타일 제어
               --------------------------------------------------------- */
            QToolButton#qt_toolbar_ext_button {{
                /* 아이콘 폰트 지정 및 텍스트 모드 강제 */
                qproperty-toolButtonStyle: ToolButtonTextOnly;
                qproperty-text: "{ext_icon_text}";
                font-family: "Material Icons";
                
                background: transparent;
                border: none;
                border-radius: 4px;
            }}

            QToolButton#qt_toolbar_ext_button:hover {{
                background-color: {btn_hover_color}; 
            }}
        """)