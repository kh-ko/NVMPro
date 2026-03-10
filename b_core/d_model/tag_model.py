#{
#  "Name": "", // 초기값은 "" 이고, UI 만들때 해당 Tag값의 라벨로 사용된다.
#  "IsUsed": true, // 초기값은 true 이고 true일 경우에만 UI에 표시됨
#  "IsProtocolError": false, // 초기값은 false 이고 true일 경우 UI에 관련된 컴포넌트는 Not Supported 상태로 표시됨
#  "IsOnlyLocalAccess": false, // 초기값은 false 이고 true일 경우 값 변경 시도가 포착될 경우 UI에서 밸브 접근 모드를 Local로 변경하도록 유도함
#  "IsSettingValue": false, // 초기값은 false 이고, 백업기능 구현시 SettingValue 인것만 백업하도록 구현할 예정
#  "AccType": "RW", // 초기값은 "RW" 이고, 읽기/쓰기 관련한 속성을 지정함 ("RW", "RO", "WO")
#  "DefaultComponent": "", // 초기값은 "" 이고, UI 만들때 기본적으로 매칭될 Custom 컴포넌트 클래스를 지정함.
#  "DisplayValue": "", // 초기값은 "" 이고, UI Component와 연결되때 화면에 표시되어야할 문구(DataType이 Enum일 경우 Options의 Label을 사용하기 위해 사용될 예정).
#  "DataType": "Base10", // 초기값은 "Base10" 이고, Value가 어떤 포멧의 데이터인지 지정함("Base10", "Base16", "Base36", "Base16_Float" ... 등등)
#  "RemoteValue": null, // 패킷에서 읽어온 값이 설정, 패킷의 데이타 타입을 보고 변환해서 알맞은 값으로 설정된다.(예 패킷에서 Hex 코드로 오지만 RemoteValue에서는 int값으로 저장할 수 있다.)
#  "LocalWriteValue": null, // UI에서 사용자에 의해 지정된 값
#  "MinMaxRange": null, float 이나 int 타입일 경우 min max값이 지정될 때가 있는데 이를 표현하기 위해 필요. min-max 제한이 없는 경우 null
#  "Options": [], // data type 이 enum일 경우 UI의 Combobox와 연계될 정보
#  "EnableCondition": TagModel로 만들어진 TagWidget간에 활성화 조건 정보(조건의 영향력은 해당 Window에 한정된다.)
#}

from enum import StrEnum
from pydantic import BaseModel, ConfigDict, PrivateAttr, Field
from PySide6.QtCore import QObject, Signal
from typing import Optional, Dict, Any

# Python 3.11+ 전용: 내장 StrEnum 사용 (문자열과 완벽 호환)
class E_AccType(StrEnum):
    RW = "RW"
    RO = "RO"
    WO = "WO"

class E_DataType(StrEnum):
    STR          = "Str"
    NUMBER       = "Number"
    FLOAT        = "Float"
    ENUM         = "Enum"
    BOOL         = "Bool"    

class E_ComponentType(StrEnum):
    LABEL           = "Label"
    INPUT_STR       = "InputText"
    INPUT_NUM       = "InputNumber"
    INPUT_HEX       = "InputHex"
    INPUT_FLOAT     = "InputFloat"
    COMBO_BOX       = "ComboBox"
    CHECK_BOX       = "CheckBox"    

class ComboItem(BaseModel):
    Label: str
    Value: int | float | str
    IsEnable: bool = True

class TagSignals(QObject):
    isUsedChanged = Signal()
    isProtocolErrorChanged = Signal()
    remoteValueChanged = Signal()
    displayValueChanged = Signal()
    optionsChanged = Signal()
    rangeChanged = Signal()

class TagModel(BaseModel):
    Path: str
    Name: str
    IsUsed: bool = True
    IsProtocolError: bool = False
    IsOnlyLocalAccess: bool = False
    IsSettingValue: bool = False
    
    # 스키마가 모델에 맞춰질 예정이므로 깔끔하게 Enum 타입 적용
    AccType: E_AccType = E_AccType.RW 
    DefaultComponent: E_ComponentType = E_ComponentType.LABEL 
    DataType: E_DataType = E_DataType.NUMBER 
    
    DisplayValue: str = ""
    RemoteValue: int | float | bool | str | None = None
    LocalWriteValue: int | float | bool | str | None = None
    MinMaxRange: tuple[int | float | None, int | float | None] | None = None
    Options: list[ComboItem] = Field(default_factory=list)

    EnableCondition: Optional[Dict[str, Any]] = None

    # Pydantic V2: 값 할당 시 유효성 검사 수행
    model_config = ConfigDict(validate_assignment=True)

    # 2. Pydantic 모델 필드에서 제외되는 Private 속성으로 시그널 객체 생성
    # (이렇게 하면 json() 변환이나 딕셔너리 변환 시 시그널 객체가 방해하지 않습니다)
    _signals: TagSignals = PrivateAttr(default_factory=TagSignals)

    # 3. 외부(Widget)에서 접근하기 쉽도록 property로 시그널 노출
    @property
    def isUsedChanged(self):
        return self._signals.isUsedChanged
    
    @property
    def isProtocolErrorChanged(self):
        return self._signals.isProtocolErrorChanged
    
    @property
    def remoteValueChanged(self):
        return self._signals.remoteValueChanged

    @property
    def displayValueChanged(self):
        return self._signals.displayValueChanged        

    @property
    def optionsChanged(self):
        return self._signals.optionsChanged

    @property
    def rangeChanged(self):
        return self._signals.rangeChanged

    # 4. 속성 할당(대입) 이벤트 가로채기
    def update_remote_value(self, new_value: int | float | bool | str | None):
        """통신 스레드 등에서 RemoteValue 갱신할 때 이 메서드를 사용하세요."""
        if self.RemoteValue == new_value:
            return

        self.RemoteValue = new_value        
        self.remoteValueChanged.emit() # 값이 진짜 바뀌었을 때만 시그널 발생

        # DataType이 ENUM일 경우 Options에서 대응하는 Label을 찾아 DisplayValue 업데이트
        # 최적화: '==' 대신 'is' 사용
        if self.DataType is E_DataType.ENUM and self.Options:
            matched_label = next((item.Label for item in self.Options if item.Value == new_value), str(new_value))
            if self.DisplayValue != matched_label:
                self.DisplayValue = matched_label
                self.displayValueChanged.emit()
        else:
            # 일반 값일 경우 단순 문자열 변환 (None 방지 처리)
            new_display = str(new_value) if new_value is not None else ""
            if self.DisplayValue != new_display:
                self.DisplayValue = new_display
                self.displayValueChanged.emit()
    
    def write_to_tag(self, value: int | float | bool | str | None):
        self.LocalWriteValue = value

    def set_options(self, new_options: list[dict | ComboItem]) -> None:
        """
        콤보박스의 전체 항목을 새로운 리스트로 교체합니다.
        dict 형태의 리스트나 ComboItem 객체 리스트 모두 처리 가능합니다.
        """
        parsed_options = []
        for opt in new_options:
            if isinstance(opt, dict):
                parsed_options.append(ComboItem(**opt))
            elif isinstance(opt, ComboItem):
                parsed_options.append(opt)
            else:
                raise ValueError("항목은 dict 또는 ComboItem 객체여야 합니다.")
        
        self.Options = parsed_options

        self.optionsChanged.emit()    

    def set_range(self, min_val: int | float | None, max_val: int | float | None):
        """
        런타임에 Min, Max 값을 변경하고 UI에 알립니다.
        (min_val 또는 max_val에 None을 넣으면 해당 방향은 무한대/제한없음을 의미합니다.)
        """
        # 둘 다 None으로 들어오면 범위 제한 자체를 없애는 것으로 간주
        if min_val is None and max_val is None:
            new_range = None
        else:
            new_range = (min_val, max_val)

        # 기존 범위와 다를 때만 업데이트 및 시그널 발생
        if self.MinMaxRange != new_range:
            self.MinMaxRange = new_range
            self.rangeChanged.emit()               

    def reset_remote_value(self):
        self.RemoteValue = None
        self.remoteValueChanged.emit()

    def reset_local_write_value(self):
        self.LocalWriteValue = None
