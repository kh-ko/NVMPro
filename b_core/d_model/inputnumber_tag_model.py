from pydantic import ConfigDict
from b_core.d_model.tag_model import TagModel

class InputNumberTagModel(TagModel):
    # JSON 파일에 "Min": 0, "Max": 100 등의 형태로 있으면 자동으로 파싱됩니다.
    # JSON에 해당 키가 생략되어 있으면 기본값인 None이 들어갑니다.
    Min: int | None = None
    Max: int | None = None

    model_config = ConfigDict(validate_assignment=True)

    @property
    def rangeChanged(self):
        return self._signals.rangeChanged

    def set_range(self, min_val: int | None, max_val: int | None):
        """런타임에 Min, Max 값을 변경하고 UI에 알립니다."""
        changed = False
        if self.Min != min_val:
            self.Min = min_val
            changed = True
        if self.Max != max_val:
            self.Max = max_val
            changed = True
            
        if changed:
            self.rangeChanged.emit() # 값이 실제로 바뀌었을 때만 시그널 발생    