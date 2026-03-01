from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPlainTextEdit
from qfluentwidgets import FluentWidget, PushButton, CheckBox
from datetime import datetime


class DummyWindow(FluentWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APC 밸브 제어 - 시스템 로그 콘솔")
        self.resize(900, 700)

        # 메인 레이아웃 설정
        self.main_layout = QVBoxLayout(self)

        # [수정됨] 타이틀바와의 간격을 위해 상단 마진(Top)을 40으로 늘림
        # 순서: (Left, Top, Right, Bottom)
        self.main_layout.setContentsMargins(20, 40, 20, 20)

        # 체크박스 영역과 로그창 사이의 간격
        self.main_layout.setSpacing(10)

        # 1. 의존성 해결: 콘솔 창을 먼저 생성
        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0c0c0c;
                color: #cccccc;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #333333;
                border-radius: 5px;
            }
        """)
        self.console.document().setMaximumBlockCount(3000)

        # 2. 상단 컨트롤 영역 구성
        self._setup_controls()

        # 3. 콘솔 창을 레이아웃에 추가
        self.main_layout.addWidget(self.console)

        # 테스트용 더미 로그 발생기
        self._print_test_logs()

    def _setup_controls(self):
        """필터(체크박스) 및 화면 지우기 컨트롤 UI 구성"""
        control_layout = QHBoxLayout()
        # 컨트롤 레이아웃 자체의 마진을 제거하여 main_layout의 규칙을 그대로 따르게 함
        control_layout.setContentsMargins(0, 0, 0, 0)

        # 다중 선택을 위한 체크박스 딕셔너리 생성
        self.filter_checkboxes = {}
        log_types = ["INFO", "WARNING", "ERROR", "DEBUG", "RX", "TX"]

        # 각 로그 타입별로 체크박스 나열
        for log_type in log_types:
            cb = CheckBox(log_type, self)
            cb.setChecked(True)  # 기본값: 모두 표시
            self.filter_checkboxes[log_type] = cb
            control_layout.addWidget(cb)

        # 우측으로 밀어주기 위한 빈 공간
        control_layout.addStretch(1)

        # 로그 지우기 버튼
        self.clear_btn = PushButton("로그 지우기", self)
        self.clear_btn.clicked.connect(self.console.clear)
        control_layout.addWidget(self.clear_btn)

        self.main_layout.addLayout(control_layout)

    def append_log(self, message: str, log_type: str = "INFO"):
        """
        외부 모듈에서 이 메서드를 호출하여 로그를 찍습니다.
        """
        log_type_upper = log_type.upper()
        if log_type_upper in self.filter_checkboxes:
            if not self.filter_checkboxes[log_type_upper].isChecked():
                return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        colors = {
            "INFO": "#ffffff",
            "WARNING": "#f1c40f",
            "ERROR": "#e74c3c",
            "DEBUG": "#3498db",
            "RX": "#2ecc71",
            "TX": "#9b59b6"
        }

        color = colors.get(log_type_upper, "#cccccc")
        formatted_msg = f'<span style="color: {color};">[{timestamp}] [{log_type_upper}] {message}</span>'

        self.console.appendHtml(formatted_msg)

        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _print_test_logs(self):
        self.append_log("로그 시스템 초기화 완료.", "INFO")
        self.append_log("워커 스레드 1번 대기 중...", "DEBUG")
        self.append_log("장치 연결 실패!", "ERROR")
        self.append_log("0x02 0x04 0x00 0x01", "RX")
        self.append_log("0x02 0x03 0x00 0x00", "TX")