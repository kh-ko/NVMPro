from c_ui.b_components.b_composite.app_statusbar_widget import AppStatusBarWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QSplitter, QHBoxLayout, QSizePolicy, QFrame
from c_ui.a_global.ntheme import NTheme
from c_ui.b_components.a_custom.custom_pushbutton import CustomButton
from c_ui.b_components.a_custom.custom_toolbar import CustomToolBar
from c_ui.c_windows.a_main.main_win_model import MainWinModel

class MainWin(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NVMPro")
        self.resize(1024, 710)

        self.model = MainWinModel(self)

        self.theme_manager = NTheme()
        self.theme_manager.theme_changed.connect(self.__color_design)

        self.__layout_design()
        self.__color_design()
        
        self.__init_components()

    def __layout_design(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # 메인 윈도우 여백 제거 (필요시 조정)
        self.main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # 1. 타이틀바 영역
        # ---------------------------------------------------------
        # 스타일(테두리)을 적용하기 위해 QWidget으로 감쌈
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setObjectName("TitleBar") # QSS 적용을 위한 ID
        
        self.title_bar_layout = QHBoxLayout(self.title_bar_widget)
        self.title_bar_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.addWidget(self.title_bar_widget)

        # ---------------------------------------------------------
        # 2. 바디 영역 (차트 영역 + 컨트롤 Splitter 영역)
        # ---------------------------------------------------------
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0) # 차트와 컨트롤 영역 사이의 빈틈 제거
        
        # 2-1. 상단 차트 영역
        self.chart_area_widget = QWidget()
        self.chart_area_widget.setObjectName("ChartArea")
        
        self.chart_area_layout = QHBoxLayout(self.chart_area_widget)
        self.chart_area_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.addWidget(self.chart_area_widget, stretch=1)

        # 2-2. 하단 컨트롤 영역 (Splitter)
        self.control_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.control_splitter.setHandleWidth(10) # 투명하지만 마우스로 잡을 수 있는 넓이는 10 유지
        self.control_splitter.setSizePolicy(
            QSizePolicy.Policy.Expanding,  
            QSizePolicy.Policy.Preferred   
        )
        self.body_layout.addWidget(self.control_splitter)

        self.main_layout.addLayout(self.body_layout, stretch=1)

        # ---------------------------------------------------------
        # 3. 앱 상태바 영역
        # ---------------------------------------------------------
        self.status_bar_widget = AppStatusBarWidget(self)
        self.status_bar_widget.setObjectName("StatusBar")
        self.main_layout.addWidget(self.status_bar_widget)

    def __color_design(self, theme_name=None):
        # 테마 매니저에서 현재 테마에 맞는 색상값을 꺼내옵니다.
        frame_bg_color = self.theme_manager.get_color("frame_bg_color")
        border_color = self.theme_manager.get_color("border_color")

        # f-string(f""")을 사용하고, CSS 블록의 중괄호는 {{ }}로 이스케이프 처리합니다.
        self.setStyleSheet(f"""
            /* 1. 타이틀바 하단: 1px 회색 선 */
            QWidget#TitleBar {{
                border-bottom: 1px solid {border_color};
            }}

            /* 2. 차트 영역 하단: 1px 회색 선 (하단 컨트롤 영역과의 경계) */
            QWidget#ChartArea {{
                border-bottom: 1px solid {border_color};
            }}

            /* 3. 상태바 상단: 1px 회색 선 */
            QWidget#StatusBar {{
                border-top: 1px solid {border_color};
            }}

            /* 4. 스플리터 핸들: 눈에 보이지 않도록 투명 처리 */
            QSplitter::handle {{
                background-color: transparent;
            }}

            /* 5. 타이틀바 버튼과 툴바 사이 구분선 */
            QFrame#TitleSeparator {{
                background-color: {border_color};
                max-width: 1px;
                min-width: 1px;
                margin-top: 4px;
                margin-bottom: 4px;
                margin-left: 5px;
                margin-right: 5px;
            }}
        """)   

    def __init_components(self):
        # 1. Local 토글 버튼 생성 및 추가
        self.btn_local = CustomButton("Local")
        self.btn_local.setFlat(True)  
        self.btn_local.setCheckable(True)               # 토글(Checkable) 기능 켜기
        self.title_bar_layout.addWidget(self.btn_local)
        self.btn_local.toggled.connect(self.model.on_local_toggled)

        # 2. Remote 토글 버튼 생성 및 추가
        self.btn_remote = CustomButton("Remote")
        self.btn_remote.setFlat(True)  
        self.btn_remote.setCheckable(True)
        self.title_bar_layout.addWidget(self.btn_remote)
        self.btn_remote.toggled.connect(self.model.on_remote_toggled)

        # 3. 구분선 (Separator)
        self.title_separator = QFrame()
        self.title_separator.setObjectName("TitleSeparator")
        self.title_bar_layout.addWidget(self.title_separator)

        # 4. 툴바 (ToolBar) 추가
        self.toolbox = CustomToolBar()
        self.toolbox.addAction("Connection")
        self.toolbox.addAction("Parameter")  # 오타(Paramter) 수정해 두었습니다.
        self.toolbox.addAction("LogView")
        self.toolbox.addAction("Help")
        self.title_bar_layout.addWidget(self.toolbox)
        self.toolbox.actionTriggered.connect(self.model.on_toolbar_action)

        # 💡 [핵심] 버튼들이 왼쪽에 예쁘게 모여있도록 우측에 빈 공간(스프링) 밀어 넣기
        # (이 코드가 없으면 두 버튼이 타이틀바 가로 전체를 50:50으로 무식하게 꽉 채워버립니다)
        self.title_bar_layout.addStretch()

        # --- 이벤트 시그널 연결 ---
        
        
        