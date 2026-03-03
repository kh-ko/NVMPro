from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from b_core.a_manager.tag_manager import TagManager
from b_core.d_model.combo_box_tag_model import ComboBoxTagModel
from c_ui.b_components.a_custom.base_caption_label import BaseCaptionLabel

class ConnectionWin(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Settings")
        self.resize(350, 400)
        
        # 태그 매니저 싱글톤 인스턴스 가져오기
        self.tag_manager = TagManager()
        
        # 위젯 참조를 저장할 딕셔너리
        self.ui_widgets = {}

        self._setup_ui()
        self._load_tags_to_ui()

    def _setup_ui(self):
        """UI 기본 레이아웃과 위젯 구성"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        # 타이틀
        title_label = QLabel("Serial Connection Settings")
        font = title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)

        # 태그들이 표시될 폼 레이아웃
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(10)
        self.main_layout.addLayout(self.form_layout)

        self.main_layout.addStretch()

        # 하단 조작 버튼
        self.btn_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setMinimumHeight(30)
        self.btn_connect.clicked.connect(self._on_connect_clicked)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setMinimumHeight(30)
        self.btn_disconnect.clicked.connect(self._on_disconnect_clicked)

        self.btn_layout.addWidget(self.btn_connect)
        self.btn_layout.addWidget(self.btn_disconnect)

        self.main_layout.addLayout(self.btn_layout)

    def _load_tags_to_ui(self):
        """TagManager에서 Connection 폴더 안의 태그들을 가져와 동적으로 UI를 생성합니다."""
        connection_folder = self.tag_manager.get_folder("Connection")
        
        if not connection_folder:
            print("[ConnectionWin] Failed to load 'Connection' folder from TagManager.")
            return

        # 폴더 안의 태그들을 순회하며 위젯 추가
        for tag_name, tag_obj in connection_folder.tags.items():
            if not tag_obj.IsUsed:
                continue

            widget = None
            
            # ComboBox 타입일 경우
            if tag_obj.DefaultComponent == "ComboBox" or isinstance(tag_obj, ComboBoxTagModel):
                combo = QComboBox()
                if isinstance(tag_obj, ComboBoxTagModel):
                    # 모델에 정의된 옵션 리스트를 바탕으로 콤보박스 아이템 추가
                    for option in tag_obj.Options:
                        combo.addItem(option.Label, option.Value)
                widget = combo

            # InputNumber 타입일 경우
            elif tag_obj.DefaultComponent == "InputNumber":
                line_edit = QLineEdit()
                # 필요시 QIntValidator 등 숫자 제한 검증기를 추가할 수 있습니다.
                widget = line_edit
            
            # 그 외 기본 위젯
            else:
                widget = QLineEdit()

            # 레이아웃에 추가
            if widget:
                # 위젯에 이름 부여 (향후 객체 조회 시 유용)
                widget.setObjectName(tag_name)
                
                # 커스텀 라벨 사용
                label = BaseCaptionLabel(tag_name)
                
                self.form_layout.addRow(label, widget)
                
                # 조회를 위해 딕셔너리에 저장
                self.ui_widgets[tag_name] = widget

    def _on_connect_clicked(self):
        """Connect 버튼 클릭 시 동작 로직"""
        # UI에서 입력·선택된 값들을 읽어오는 예시
        current_settings = {}
        for tag_name, widget in self.ui_widgets.items():
            if isinstance(widget, QComboBox):
                val = widget.currentData()
                current_settings[tag_name] = val
            elif isinstance(widget, QLineEdit):
                current_settings[tag_name] = widget.text()

        print("Current Connection Settings:")
        for k, v in current_settings.items():
            print(f"  {k}: {v}")
            
        # TODO: 프로토콜 매니저 연결 (ProtocolManager 연결 함수 호출 등)
        QMessageBox.information(self, "Connection", "Connect logic not fully implemented yet.\\nSee console for parsed settings.")

    def _on_disconnect_clicked(self):
        """Disconnect 버튼 클릭 시 동작 로직"""
        # TODO: 연결 해제 로직
        QMessageBox.information(self, "Connection", "Disconnected.")