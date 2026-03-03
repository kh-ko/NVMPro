#{
#  "Name": "", // 초기값은 "" 이고, UI 만들때 해당 Tag값의 라벨로 사용된다.
#  "IsUsed": true, // 초기값은 true 이고 true일 경우에만 UI에 표시됨
#  "IsProtocolError": false, // 초기값은 false 이고 true일 경우 UI에 관련된 컴포넌트는 Not Supported 상태로 표시됨
#  "IsOnlyLocalAccess": false, // 초기값은 false 이고 true일 경우 값 변경 시도가 포착될 경우 UI에서 밸브 접근 모드를 Local로 변경하도록 유도함
#  "IsSettingValue": false, // 초기값은 false 이고, 백업기능 구현시 SettingValue 인것만 백업하도록 구현할 예정
#  "AccType": "RW", // 초기값은 "RW" 이고, 읽기/쓰기 관련한 속성을 지정함 ("RW", "RO", "WO")
#  "DefaultComponent": "", // 초기값은 "" 이고, UI 만들때 기본적으로 매칭될 Custom 컴포넌트 클래스를 지정함.
#  "DataType": "Base10", // 초기값은 "Base10" 이고, Value가 어떤 포멧의 데이터인지 지정함("Base10", "Base16", "Base36", "Base16_Float" ... 등등)
#  "ReadValue": ??, // 패킷에서 읽어온 값이 설정되며... DataType에 따라 int, float, string 등이 될수 있다. 파이썬에서 이럴경우 데이터 타입을 어떻게 지정하지?
#  "WriteValue": ??, // UI에서 사용자에 의해 지정된 값이며, DataType에 따라 int, float, string 등이 될수 있다. 파이썬에서 이럴경우 데이터 타입을 어떻게 지정하지?
#}

from enum import StrEnum
from pydantic import BaseModel

# Python 3.11+ 전용: 내장 StrEnum 사용 (문자열과 완벽 호환)
class E_AccType(StrEnum):
    RW = "RW"
    RO = "RO"
    WO = "WO"

class E_DataType(StrEnum):
    STR          = "Str"
    BASE10       = "Base10"
    BASE16       = "Base16"
    BASE36       = "Base36"
    BASE10_FLOAT = "Base10_Float"
    BASE16_FLOAT = "Base16_Float"

class E_ComponentType(StrEnum):
    LABEL           = "Label"
    INPUT_NUM       = "InputNumber"
    INPUT_HEX       = "InputHex"
    INPUT_FLOAT     = "InputFloat"
    COMBO_BOX       = "ComboBox"
    CHECK_BOX       = "CheckBox"    

class TagModel(BaseModel):
    Name: str = ""
    IsUsed: bool = True
    IsProtocolError: bool = False
    IsOnlyLocalAccess: bool = False
    IsSettingValue: bool = False
    
    # 깔끔하게 Enum 타입 지정
    AccType: E_AccType = E_AccType.RW 
    DefaultComponent: str = ""
    DataType: E_DataType = E_DataType.BASE10 
    
    # Python 3.10+ 전용: Union 대신 | 기호 사용으로 가독성 극대화
    ReadValue: int | float | str | None = None
    WriteValue: int | float | str | None = None
