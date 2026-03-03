from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal

class NonAutoToggleButton(QPushButton):
    """
    클릭해도 스스로 상태(Checked)를 변경하지 않는 커스텀 버튼입니다. 
    상태 변경은 오직 외부에서 setChecked()를 호출할 때만 바뀝니다.
    """
    def nextCheckState(self):
        pass


class BaseSwitchButton(QFrame):
    # UI 클릭 시 Service 쪽에 변경 요청을 보내는 시그널 (0: 왼쪽, 1: 오른쪽)
    mode_requested = Signal(int) 

    def __init__(self, left_text="Local", right_text="Remote", parent=None):
        super().__init__(parent)
        self.setObjectName("customModeSwitch")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4) 

        # 1. 범용적인 이름(btn_left, btn_right)으로 버튼 생성
        # 생성자에서 전달받은 초기 텍스트로 라벨을 설정합니다.
        self.btn_left = NonAutoToggleButton(left_text, self)
        self.btn_left.setCheckable(True)
        self.btn_left.setCursor(Qt.PointingHandCursor)

        self.btn_right = NonAutoToggleButton(right_text, self)
        self.btn_right.setCheckable(True)
        self.btn_right.setCursor(Qt.PointingHandCursor)

        # 2. 클릭 시그널 연결 (0: 왼쪽 요청, 1: 오른쪽 요청)
        self.btn_left.clicked.connect(lambda: self.mode_requested.emit(0))
        self.btn_right.clicked.connect(lambda: self.mode_requested.emit(1))

        self.layout.addWidget(self.btn_left)
        self.layout.addWidget(self.btn_right)

        # 3. 초기 상태 설정 (0: 왼쪽 선택)
        self.set_check(0)

        # QDarkTheme 기본 스타일 유지 + 선택된 글자만 굵게 표시
        self.setStyleSheet("""
            QPushButton {
                /* 좌우 패딩을 넉넉하게 주어 글자가 굵어질 때 필요한 공간을 미리 확보합니다 */
                padding-left: 12px;
                padding-right: 12px;
                
                /* 글자가 짧아도 버튼이 너무 작아지지 않게 최소 너비를 보장합니다 */
                min-width: 60px; 
            }
            QPushButton:checked {
                font-weight: bold;
            }
        """)

    def set_labels(self, left_text: str, right_text: str):
        """
        왼쪽과 오른쪽 버튼의 텍스트(라벨)를 변경합니다.
        """
        self.btn_left.setText(left_text)
        self.btn_right.setText(right_text)

    def set_check(self, value: int):
        """
        Service 레이어에서 로직 처리 완료 후, 실제 UI 상태를 변경할 때 호출하는 함수입니다.
        value == 0: 왼쪽 버튼을 선택된 상태로 만듭니다.
        value == 1: 오른쪽 버튼을 선택된 상태로 만듭니다.
        """
        if value == 0:
            self.btn_left.setChecked(True)
            self.btn_right.setChecked(False)
        elif value == 1:
            self.btn_left.setChecked(False)
            self.btn_right.setChecked(True)