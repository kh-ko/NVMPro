from PySide6.QtWidgets import QWidget
from c_ui.a_global.ntheme import NTheme

class BaseWin(QWidget):
    def __init__(self):
        super().__init__()

        self.theme_manager = NTheme()  # 싱글톤이므로 어디서 호출하든 같은 객체입니다.
        self.theme_manager.theme_changed.connect(self._apply_theme_colors)

        self._apply_design()

    # 테마에 상관없이 일정하게 적용되는 디자인
    def _apply_design(self):
        # self.resize(1024, 710)
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_layout.setSpacing(0)
        # self.tool_splitter.setFixedHeight(300)

        self._apply_theme_colors()

    # 테마에 따라 적용되는 색상또는 색상과 함께 적용되어지는 속성들(sheet로 함께 적용되어지는 것들)
    def _apply_theme_colors(self, theme_name=None):
        """테마 색상을 UI에 적용합니다."""
        pass
