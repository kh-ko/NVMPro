from PySide6.QtWidgets import QToolBar, QToolButton
from PySide6.QtCore import Qt, QEvent
from c_ui.a_global.ntheme import NTheme 

class BaseToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)   
        self.setFloatable(False) 

        # 테마 매니저 연동
        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)        

        self._apply_theme_colors()

    def actionEvent(self, event):
        """
        툴바에 Action이 추가/제거될 때 발생하는 이벤트를 감지합니다.
        Action이 추가될 때 자동으로 ToolButton의 속성을 설정합니다.
        """
        super().actionEvent(event)
        
        if event.type() == QEvent.Type.ActionAdded:
            action = event.action()
            widget = self.widgetForAction(action)
            
            if isinstance(widget, QToolButton):
                widget.setProperty("menuBtn", True)
                widget.setToolButtonStyle(Qt.ToolButtonTextOnly)
                
                # 동적으로 Property가 추가되었으므로 스타일 강제 업데이트
                widget.style().unpolish(widget)
                widget.style().polish(widget)

    def _apply_theme_colors(self, theme_name=None):
        btn_hover_color = self.theme_manager.get_color("btn_hover_color")
        separator_color = self.theme_manager.get_color("separator_color")
        
        # 확장 버튼 아이콘 (Material Icons)
        ext_icon_text = "\ue5cc"

        self.setStyleSheet(f"""
            QToolBar {{
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

            /* 확장 버튼(...) 스타일 제어 */
            QToolButton#qt_toolbar_ext_button {{
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