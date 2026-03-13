import math
from PySide6.QtWidgets import ( QWidget, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox, QSizePolicy )
from PySide6.QtCore import Qt, QRegularExpression, Signal
from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
from b_core.d_model.tag_model import TagModel, E_ComponentType
from c_ui.b_components.c_utils.custom_validator import EmptyOrIntValidator, EmptyOrDoubleValidator

class TagWidget(QWidget):
    user_input_changed = Signal(object)
    dirty_changed  = Signal()

    def __init__(self, tag_model: TagModel, component_type: E_ComponentType, parent=None):
        super().__init__(parent)
        self._is_internal_updating = False
        self.enable_dirty = True
        self.tag_model = tag_model
        self.component_type = component_type
        
        self.int_validator = None
        self.float_validator = None

        self.__init_ui()
        self.__connect_signals()
        self.on_range_changed()
        self.on_options_changed()
        self.set_dirty(False)
        self.update_ui_state()

    def __init_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 1. 태그 이름 라벨
        self.name_label = QLabel(self.tag_model.Name)
        self.name_label.setFixedWidth(120)
        self.main_layout.addWidget(self.name_label)
        
        # 2. Dirty 인디케이터 (초기는 투명하게)
        self.dirty_indicator = QLabel()
        self.dirty_indicator.setText("*")
        self.main_layout.addWidget(self.dirty_indicator)
        
        # 3. Default Component 에 따른 동적 위젯 생성
        self.value_widget = self.__create_value_component()
        
        if self.value_widget:
            self.value_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.main_layout.addWidget(self.value_widget)
        else:
            # 매칭되는 위젯이 없으면 빈 라벨 
            self.main_layout.addWidget(QLabel("Unknown Component"))

    def __create_value_component(self):
        comp_type = self.component_type
        
        if self.component_type == E_ComponentType.LABEL:
            widget = QLabel()
            return widget

        elif comp_type == E_ComponentType.INPUT_STR:
            widget = QLineEdit()
            return widget

        elif comp_type == E_ComponentType.INPUT_NUM:
            widget = QLineEdit()
            self.int_validator = EmptyOrIntValidator(0, 100)
            widget.setValidator(self.int_validator)
            return widget
            
        elif comp_type == E_ComponentType.INPUT_HEX:
            widget = QLineEdit()
            widget.setPlaceholderText("Hex 값 입력")
            # 정규식을 이용해 16진수(0-9, a-f, A-F)만 입력 가능하도록 제한
            hex_validator = QRegularExpressionValidator(QRegularExpression("^[0-9A-Fa-f]+$"))
            widget.setValidator(hex_validator)            
            return widget
            
        elif comp_type == E_ComponentType.INPUT_FLOAT:
            widget = QLineEdit()
            self.float_validator = EmptyOrDoubleValidator(0, 100)
            widget.setValidator(self.float_validator)
            return widget
            
        elif comp_type == E_ComponentType.COMBO_BOX:
            widget = QComboBox()
            # 옵션 추가
            for opt in self.tag_model.Options:
                widget.addItem(opt.Label, userData=opt.Value)
            return widget
            
        elif comp_type == E_ComponentType.CHECK_BOX:
            widget = QCheckBox()
            return widget
            
        return None

    def __connect_signals(self):
        # 모델의 시그널 연결
        self.tag_model.isUsedChanged.connect(self.on_is_used_changed)
        self.tag_model.isProtocolErrorChanged.connect(self.on_is_protocol_error_changed)
        self.tag_model.displayValueChanged.connect(self.on_display_value_changed)
        self.tag_model.remoteValueChanged.connect(self.on_remote_value_changed)
        self.tag_model.optionsChanged.connect(self.on_options_changed)
        self.tag_model.rangeChanged.connect(self.on_range_changed)

        
        # UI 입력 요소의 변경 이벤트 연결 (Dirty 체크용 임시 구현)
        if isinstance(self.value_widget, QLineEdit):
            self.value_widget.textChanged.connect(self.on_user_input_changed)
        elif isinstance(self.value_widget, QComboBox):
            self.value_widget.currentIndexChanged.connect(self.on_user_input_changed)
        elif isinstance(self.value_widget, QCheckBox):
            self.value_widget.toggled.connect(self.on_user_input_changed)

    def on_is_used_changed(self):
        self.setVisible(self.tag_model.IsUsed)

    def on_is_protocol_error_changed(self):
        #아직 관련 컨셉 확정 안됨 : 보류
        pass
    
    def on_display_value_changed(self):
        #아직 관련 컨셉 확정 안됨 : 보류
        pass

    def on_remote_value_changed(self):
        self.update_ui_state()

    def on_options_changed(self):
        # 콤보 박스일 때만 동작
        if self.component_type == E_ComponentType.COMBO_BOX:
            # 아이템 갱신 중 원치 않는 user_input_changed 시그널 발생을 방지
            self._is_internal_updating = True
            
            # 기존 목록 초기화
            self.value_widget.clear()
            
            # 모델의 새로운 옵션 목록을 기반으로 아이템 추가
            if self.tag_model.Options:
                for opt in self.tag_model.Options:
                    self.value_widget.addItem(opt.Label, userData=opt.Value)
                    
            # 갱신 완료 후 시그널 다시 활성화
            self._is_internal_updating = False

            self.update_ui_state()

    def on_options_updated(self):
        # 콤보 박스일 때만 동작
        if self.component_type == E_ComponentType.COMBO_BOX:
            # 아이템 갱신 중 원치 않는 user_input_changed 시그널 발생을 방지
            self._is_internal_updating = True
            
            combo = self.value_widget
            new_options = self.tag_model.Options

            for i, opt in enumerate(new_options):
                if combo.itemText(i) != opt.Label:
                    combo.setItemText(i, opt.Label)
                    
            # 갱신 완료 후 시그널 다시 활성화
            self._is_internal_updating = False

            self.update_ui_state()            

    def on_range_changed(self):
        min_val, max_val = None, None
        comp_type = self.component_type

        if self.tag_model.MinMaxRange:
            min_val, max_val = self.tag_model.MinMaxRange

        if comp_type == E_ComponentType.INPUT_NUM:
            low = int(min_val) if min_val is not None else -2147483648
            high = int(max_val) if max_val is not None else 2147483647
            self.int_validator.setRange(low, high)

        elif comp_type == E_ComponentType.INPUT_FLOAT:
            low = float(min_val) if min_val is not None else -float('inf')
            high = float(max_val) if max_val is not None else float('inf')
            # QDoubleValidator는 소수점 자릿수(decimals) 설정도 가능합니다.
            self.float_validator.setRange(low, high, 323)    
            self.float_validator.setNotation(QDoubleValidator.Notation.StandardNotation)

    def on_user_input_changed(self, value=None):
        current_val = self.get_current_ui_value()
        self.user_input_changed.emit(current_val)

        if self._is_internal_updating:
            return

        if not self.value_widget:
            return

        # Emit the current value via the custom signal
        comp_type = self.component_type
        is_empty = False
        is_same_as_remote = False
        remote_val = getattr(self.tag_model, 'RemoteValue', None)                    
                    
        if isinstance(self.value_widget, QLineEdit):
            text_val = self.value_widget.text().strip()
            if not text_val:
                is_empty = True
            elif remote_val is not None:
                try:
                    if comp_type == E_ComponentType.INPUT_NUM:
                        # QLineEdit에는 .value()가 없으므로 int 변환 필요
                        is_same_as_remote = (int(text_val) == int(remote_val))
                    elif comp_type == E_ComponentType.INPUT_FLOAT:
                        is_same_as_remote = math.isclose(float(text_val), float(remote_val), rel_tol=1e-9)
                    elif comp_type == E_ComponentType.INPUT_HEX:
                        # remopte_val 을 Hex 로 바꿔야 할것같은데 ... 보류
                        is_same_as_remote = (text_val == str(remote_val))
                    else:
                        is_same_as_remote = (text_val == str(remote_val))

                except ValueError:
                    is_same_as_remote = True # 변환 실패 시 생각이 필요함...
                
        elif isinstance(self.value_widget, QComboBox):
            if self.value_widget.currentIndex() == -1:
                is_empty = True
            elif remote_val is not None:
                # 콤보박스는 화면에 보이는 글자가 아닌 내부 데이터(userData)로 비교
                is_same_as_remote = (self.value_widget.currentData() == remote_val)
                
        elif isinstance(self.value_widget, QCheckBox):
            if remote_val is not None:
                is_same_as_remote = (self.value_widget.isChecked() == bool(remote_val))

        # 2. 조건에 따라 Dirty 상태 결정
        self.set_dirty(not (is_empty or is_same_as_remote))

    def get_current_ui_value(self):
        """현재 UI 요소에 입력되어 있는 값을 추출하여 반환합니다."""
        if not self.value_widget:
            return None
            
        comp_type = self.component_type
        
        if isinstance(self.value_widget, QLineEdit):
            text_val = self.value_widget.text().strip()
            if not text_val:
                return None
                
            try:
                if comp_type == E_ComponentType.INPUT_NUM:
                    return int(text_val)
                elif comp_type == E_ComponentType.INPUT_FLOAT:
                    return float(text_val)
                elif comp_type == E_ComponentType.INPUT_STR:
                    return text_val
                elif comp_type == E_ComponentType.INPUT_HEX:
                    return text_val # Hex는 일단 문자열로 취급
            except ValueError:
                return None
                
        elif isinstance(self.value_widget, QComboBox):
            if self.value_widget.currentIndex() == -1:
                return None
            return self.value_widget.currentData()
            
        elif isinstance(self.value_widget, QCheckBox):
            return self.value_widget.isChecked()
            
        return None

    def set_dirty(self, is_dirty: bool):
        if not self.enable_dirty:
            return

        self.dirty = is_dirty
        if is_dirty:
            # 글자 색상을 주황색(orange)으로 변경하고, 조금 더 눈에 띄게 굵게(bold) 처리
            self.dirty_indicator.setStyleSheet("color: orange; font-weight: bold;")
        else:
            # 글자 색상을 투명하게(transparent) 만들어서 안 보이게 처리
            self.dirty_indicator.setStyleSheet("color: transparent;")

        self.dirty_changed.emit()

    def update_ui_state(self):
        # 사용자에 의해 변경중이면 값을 갱신하지 않는다.
        if getattr(self, 'dirty', False) or self.value_widget.hasFocus():
            return

        remote_val = self.tag_model.RemoteValue
        comp_type = self.tag_model.DefaultComponent

        # 3. 값 갱신 중 원치 않는 이벤트 발생 차단
        self._is_internal_updating = True

        try:
            # 1. Null (None) 처리
            if remote_val is None:
                if comp_type == E_ComponentType.LABEL:
                    self.value_widget.setText("-")
                elif comp_type in (E_ComponentType.INPUT_NUM, E_ComponentType.INPUT_HEX, E_ComponentType.INPUT_FLOAT, E_ComponentType.INPUT_STR) :
                    self.value_widget.clear()
                elif comp_type == E_ComponentType.COMBO_BOX:
                    self.value_widget.setCurrentIndex(-1)
                elif comp_type == E_ComponentType.CHECK_BOX:
                    self.value_widget.setTristate(True)
                    self.value_widget.setCheckState(Qt.CheckState.PartiallyChecked)
                return  # Null 처리 완료 후 종료

            # 2. 컴포넌트 타입별 실제 값 설정
            if comp_type == E_ComponentType.LABEL:
                self.value_widget.setText(str(remote_val))

            elif comp_type == E_ComponentType.INPUT_STR:
                self.value_widget.setText(str(remote_val))

            elif comp_type == E_ComponentType.INPUT_NUM:
                self.value_widget.setText(str(remote_val))
                
            elif comp_type == E_ComponentType.INPUT_FLOAT:
                self.value_widget.setText(str(remote_val))
                
            elif comp_type == E_ComponentType.INPUT_HEX:
                # remote_val이 int 타입일 경우 Hex 문자열(대문자)로 포맷팅하여 표시
                try:
                    self.value_widget.setText(f"{int(remote_val):X}")
                except ValueError:
                    self.value_widget.setText(str(remote_val))
                
            elif comp_type == E_ComponentType.COMBO_BOX:
                idx = self.value_widget.findData(remote_val)
                if idx >= 0:
                    self.value_widget.setCurrentIndex(idx)
                    
            elif comp_type == E_ComponentType.CHECK_BOX:
                self.value_widget.setTristate(False)
                self.value_widget.setChecked(bool(remote_val))
                
        except (ValueError, TypeError) as e:
            # 타입 변환 실패 등의 에러를 대비
            print(f"UI 갱신 에러 ({self.tag_model.Name}): {e}")
            
        finally:
            # 5. 시그널 다시 활성화 (try-except와 관계없이 무조건 실행되도록 finally 사용)
            self._is_internal_updating = False

    def write_to_tag(self):
        self.tag_model.write_to_tag(self.get_current_ui_value())

    def set_enable_dirty(self, value : bool):
        self.enable_dirty = value
