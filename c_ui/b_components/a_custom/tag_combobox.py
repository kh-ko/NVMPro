from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout
from PySide6.QtCore import Signal

class TagComboBox(QWidget):
    dirtyChanged = Signal(bool)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = None
        self._is_dirty = False

        # UI 컴포넌트 생성 및 설정
        self.label = QLabel("Label")
        self.label.setFixedWidth(150) # 라벨 폭 150pt 기본값
        self.combo_box = QComboBox()

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # 사용자 조작 감지 (순수 마우스/키보드 조작만 감지)
        self.combo_box.activated.connect(self._on_user_selection_changed)

        self.set_model(model)

    def set_label_width(self, width: int):
        """라벨의 고정 폭을 지정합니다."""
        self.label.setFixedWidth(width)

    def set_model(self, model):
        """모델을 연동하고, 모델의 값 변경 시그널을 위젯에 연결합니다."""
        # 기존 모델이 있었다면 시그널 연결 해제 (안전성 확보)
        if self._model:
            # 1-1. ReadValue 변경 시그널 해제
            if hasattr(self._model, 'readValueChanged'):
                try:
                    self._model.readValueChanged.disconnect(self.update_from_read_value)
                except RuntimeError:
                    pass
            
            # 1-2. Options 변경 시그널 해제 (추가된 부분!)
            if hasattr(self._model, 'optionsChanged'):
                try:
                    self._model.optionsChanged.disconnect(self._reload_combo_options)
                except RuntimeError:
                    pass
            
        self._model = model
        self.label.setText(model.Name)

        self.combo_box.blockSignals(True)
        self.combo_box.clear()

        # 예외/초기 상태를 위한 기본 아이템 추가
        self.combo_box.addItem("-", userData=None)

        for option in model.Options:
            self.combo_box.addItem(option.Label, userData=option.Value)
        self.combo_box.blockSignals(False)

        # 2. 모델에서 값이 바뀔 때 발생하는 시그널 자동 연계
        if hasattr(self._model, 'readValueChanged'):
            self._model.readValueChanged.connect(self.update_from_read_value)

        if hasattr(self._model, 'optionsChanged'):
            self._model.optionsChanged.connect(self._reload_combo_options)

        # 첫 생성 시 초기값 세팅
        self.update_from_read_value()

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def set_dirty(self, state: bool):
        """
        3. 통신 성공(응답 수신) 등 확실한 시점에 ViewModel에서 IsDirty를 해제할 때 호출.
        (밀린 ReadValue 강제 갱신 로직은 제거됨)
        """

        if self._is_dirty != state:
            self._is_dirty = state
            self.dirtyChanged.emit(self._is_dirty)

            if self._is_dirty == False:
                self.update_from_read_value() 

    def update_from_read_value(self):
        """
        모델의 ReadValue가 갱신되었다는 시그널(readValueChanged)을 받으면 자동으로 실행됩니다.
        """
        if not self._model: return

        # IsDirty값이 True이면 ReadValue 변경은 무시 (사용자 조작 우선)
        if self._is_dirty:
            return

        read_val = self._model.ReadValue
        idx = self.combo_box.findData(read_val)

        # 범위에 벗어나거나 아직 값이 없을 경우 "-"로 표시
        if idx == -1 or read_val is None:
            idx = self.combo_box.findData(None) 

        self.combo_box.blockSignals(True)
        self.combo_box.setCurrentIndex(idx)
        self.combo_box.blockSignals(False)

    def _reload_combo_options(self):
        """
        모델의 Options가 변경되었을 때 호출되어 콤보박스 항목을 갱신합니다.
        """
        if not self._model: return
        
        self.combo_box.blockSignals(True)

        self.combo_box.clear()
        
        # 예외/초기 상태를 위한 기본 아이템 추가
        self.combo_box.addItem("-", userData=None)
        
        for option in self._model.Options:
            self.combo_box.addItem(option.Label, userData=option.Value)
        
        # 옵션 갱신 후 현재 값에 맞는 인덱스 다시 찾아서 설정
        self.update_from_read_value()

        self.combo_box.blockSignals(False)

    def _on_user_selection_changed(self, index):
        """사용자가 콤보박스 값을 직접 변경했을 때"""
        if not self._model: return

        selected_value = self.combo_box.itemData(index)
        read_val = self._model.ReadValue

        # 선택된 값과 ReadValue값이 다르면 IsDirty = True, 같으면 False
        new_dirty_state = (selected_value != read_val)
        
        if self._is_dirty != new_dirty_state:
            self._is_dirty = new_dirty_state
            self.dirtyChanged.emit(self._is_dirty)

    def applyToTag(self):
        """ViewModel이 호출하여 현재 UI 값을 모델의 WriteValue에 적용합니다."""
        if self._model and self._is_dirty:
            selected_value = self.combo_box.currentData()
            self._model.WriteValue = selected_value