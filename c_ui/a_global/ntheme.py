import qdarktheme
from PySide6.QtCore import QObject, Signal, Qt          # Qt 추가
from PySide6.QtGui import QGuiApplication               # QGuiApplication 추가

class NTheme(QObject):
    _instance = None
    
    # 테마가 변경될 때 다른 위젯들에 알리기 위한 시그널
    theme_changed = Signal(str)

    def __new__(cls, *args, **kwargs):
        # 싱글톤 패턴 적용: 인스턴스가 없으면 만들고, 있으면 기존 것을 반환
        if not cls._instance:
            cls._instance = super(NTheme, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # __init__이 여러 번 호출되는 것을 방지
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        
        # 2. 커스텀 색상 팔레트 정의 (Light / Dark 모드별)
        self._custom_palettes = {
            "light": {
                "border_color": "#E0E0E0",
                "frame_bg_color": "#F3F3F3",
                "chart_bg_color": "#FFFFFF",
                "btn_hover_color": "#14000000",
                "separator_color": "#CCCCCC"
            },
            "dark": {
                "border_color": "#E0E0E0",
                "frame_bg_color": "#F3F3F3",
                "chart_bg_color": "#FFFFFF",
                "btn_hover_color": "#14FFFFFF",
                "separator_color": "#CCCCCC"
            }
        }

        # 1. 초기 테마 설정
        self.set_theme("light")

    def set_theme(self, theme_name: str):
        """테마를 변경하고 qdarktheme 및 커스텀 색상을 업데이트합니다."""
        if theme_name not in ["light", "dark", "auto"]:
            return

        self._theme = theme_name
        actual_theme = theme_name

        # --- 수정된 부분: auto일 경우 OS 테마 확인 ---
        if theme_name == "auto":
            # OS의 현재 컬러 스킴(테마) 상태를 읽어옵니다. (PySide6 6.5 이상 지원)
            scheme = QGuiApplication.styleHints().colorScheme()
            
            # OS가 다크 모드면 "dark", 아니면 "light"로 설정합니다.
            if scheme == Qt.ColorScheme.Dark:
                actual_theme = "dark"
            else:
                actual_theme = "light"
        # ----------------------------------------------

        # 알아낸 actual_theme("light" 또는 "dark")에 맞춰 커스텀 색상표를 가져옵니다.
        self.colors = self._custom_palettes.get(actual_theme, self._custom_palettes["light"])

        # qdarktheme 패키지에 테마 적용 (qdarktheme은 자체적으로 "auto"를 인식합니다)
        qdarktheme.setup_theme(theme_name)

        # 테마 변경 시그널 발생
        self.theme_changed.emit(actual_theme)

    def get_theme(self) -> str:
        """현재 테마 이름을 반환합니다."""
        return self._theme

    def get_color(self, color_key: str) -> str:
        """현재 테마에 맞는 특정 커스텀 색상을 반환합니다."""
        return self.colors.get(color_key, "#000000") # 키가 없으면 기본값 블랙 반환