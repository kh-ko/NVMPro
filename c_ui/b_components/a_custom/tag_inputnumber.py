from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Signal

class TagInputNumber(QWidget):
    dirtyChanged = Signal(bool)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = None
        self._is_dirty = False

        # UI 컴포넌트 생성 및 설정
        self.label = QLabel("Label")
        self.label.setFixedWidth(150) # 라벨 폭 150pt 기본값
        
        self.line_edit = QLineEdit()
        # 정수만 입력되도록 강제 (필요에 따라 최소/최대값 제한 가능)
        self.line_edit.setValidator(QIntValidator()) 

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 사용자 조작 감지 (코드에 의한 변경 textChanged가 아닌, 순수 타이핑 textEdited 감지)
        self.line_edit.textEdited.connect(self._on_user_text_edited)

        self.set_model(model)

    def set_label_width(self, width: int):
        """라벨의 고정 폭을 지정합니다."""
        self.label.setFixedWidth(width)

    def set_model(self, model):
        """모델을 연동하고, 모델의 값 변경 시그널을 위젯에 연결합니다."""
        # 기존 모델이 있었다면 시그널 연결 해제
        if self._model:
            if hasattr(self._model, 'readValueChanged'):
                try:
                    self._model.readValueChanged.disconnect(self.update_from_read_value)
                except RuntimeError:
                    pass
            if hasattr(self._model, 'rangeChanged'):
                try:
                    self._model.rangeChanged.disconnect(self._update_validator)
                except RuntimeError:
                    pass                
            
        self._model = model
        self.label.setText(model.Name)

        # [추가된 부분] 모델에 Min, Max 속성이 있다면 Validator에 범위 적용
        if hasattr(self._model, 'Min') and hasattr(self._model, 'Max'):
            # 값이 None일 경우를 대비해 32비트 정수 최소/최대값(안전장치)으로 기본 세팅
            min_val = self._model.Min if self._model.Min is not None else -2147483648
            max_val = self._model.Max if self._model.Max is not None else 2147483647
            
            # 입력창에 최소~최대값 제한을 거는 QIntValidator 적용
            self.line_edit.setValidator(QIntValidator(min_val, max_val, self.line_edit))
        
        # 모델 연결 시 초기 시그널 연결
        if hasattr(self._model, 'readValueChanged'):
            self._model.readValueChanged.connect(self.update_from_read_value)
        
        if hasattr(self._model, 'rangeChanged'):
            self._model.rangeChanged.connect(self._update_validator)

        # 첫 생성 시 초기값 세팅
        self.update_from_read_value()

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def set_dirty(self, state: bool):
        """통신 성공 등 확실한 시점에 ViewModel에서 IsDirty를 해제할 때 호출."""
        if self._is_dirty != state:
            self._is_dirty = state
            self.dirtyChanged.emit(self._is_dirty)

            # IsDirty가 False로 풀렸을 때 강제 갱신
            if self._is_dirty == False:
                self.update_from_read_value() 

    def update_from_read_value(self):
        """모델의 ReadValue가 갱신되었을 때 실행됩니다."""
        if not self._model: return
        if self._is_dirty: return

        read_val = self._model.ReadValue

        self.line_edit.blockSignals(True)
        
        # 값이 없거나 예외 상태일 때는 "-" 표시
        if read_val is None:
            self.line_edit.setText("-")
        else:
            self.line_edit.setText(str(read_val))
            
        self.line_edit.blockSignals(False)

    def _update_validator(self):
        """모델의 Min, Max 값에 따라 QIntValidator를 갱신합니다."""
        if not hasattr(self._model, 'Min') or not hasattr(self._model, 'Max'):
            return

        # None일 경우를 대비해 32비트 정수 극한값으로 기본 세팅
        min_val = self._model.Min if self._model.Min is not None else -2147483648
        max_val = self._model.Max if self._model.Max is not None else 2147483647
        
        # 기존 Validator 교체
        self.line_edit.setValidator(QIntValidator(min_val, max_val, self.line_edit))
        
        # 만약 현재 입력되어 있는 값이 바뀐 범위를 벗어났다면 어떻게 처리할지 로직을 추가할 수도 있습니다.
        # 예:
        
    def _on_user_text_edited(self, text):
        """사용자가 입력창에 직접 타이핑을 했을 때"""
        if not self._model: return

        # 1. 사용자가 입력한 텍스트를 정수로 변환 시도
        try:
            # 완전히 지웠거나 "-" 만 입력된 상태면 None으로 취급
            if text == "" or text == "-":
                input_val = None
            else:
                input_val = int(text)
        except ValueError:
            input_val = None

        read_val = self._model.ReadValue

        # 2. 형변환된 입력값과 ReadValue를 비교하여 IsDirty 판단
        new_dirty_state = (input_val != read_val)
        
        if self._is_dirty != new_dirty_state:
            self._is_dirty = new_dirty_state
            self.dirtyChanged.emit(self._is_dirty)

    def applyToTag(self):
        """ViewModel이 호출하여 현재 UI 값을 모델의 WriteValue에 적용합니다."""
        if self._model and self._is_dirty:
            text = self.line_edit.text()
            try:
                self._model.WriteValue = int(text)
            except ValueError:
                self._model.WriteValue = None