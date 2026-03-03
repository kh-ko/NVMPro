from pydantic import BaseModel, Field, ConfigDict
from b_core.d_model.tag_model import TagModel

class ComboItem(BaseModel):
    Label: str
    Value: int | float | str

class ComboBoxTagModel(TagModel):
    Options: list[ComboItem] = Field(default_factory=list)

    # (선택 사항) Pydantic V2 기능: 할당할 때도 자동으로 타입 검사 및 객체 변환을 수행하도록 설정
    model_config = ConfigDict(validate_assignment=True)

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

        self._signals.optionsChanged.emit()

    # 3. 외부(Widget)에서 접근하기 쉽도록 property로 시그널 노출
    @property
    def optionsChanged(self):
        return self._signals.optionsChanged        
    # 3. 외부(Widget)에서 접근하기 쉽도록 property로 시그널 노출
    
    def add_option(self, label: str, value: int | float | str) -> None:
        """
        콤보박스의 맨 끝에 새로운 항목을 하나 추가합니다.
        """
        self.Options.append(ComboItem(Label=label, Value=value))

        self._signals.optionsChanged.emit()

    def clear_options(self) -> None:
        """
        콤보박스의 모든 항목을 비웁니다.
        """
        self.Options.clear()

        self._signals.optionsChanged.emit()