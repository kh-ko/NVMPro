from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from c_ui.b_components.b_composite.console_widget import ConsoleWidget

class LogWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("APC 밸브 제어 - 시스템 로그 콘솔")
        self.resize(900, 700)

        # 메인 레이아웃 설정
        self.main_layout = QVBoxLayout(self)

        # 타이틀바와의 간격을 위해 상단 마진(Top)을 40으로 늘림
        # 순서: (Left, Top, Right, Bottom)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # ConsoleWidget 추가
        self.console_widget = ConsoleWidget(self)
        self.main_layout.addWidget(self.console_widget)

    def closeEvent(self, event):
        """창이 닫힐 때 메모리에서 완전히 소멸되도록 매니저의 참조를 제거합니다."""
        from b_core.a_manager.log_manager import LogManager
        
        # 내부 큐 비활성화/삭제
        if hasattr(self, 'console_widget') and self.console_widget:
            self.console_widget.update_timer.stop()
            self.console_widget.clear_message()
            
        # LogManager의 참조 제거 (완전 소멸)
        LogManager().log_window = None
        super().closeEvent(event)
