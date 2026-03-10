from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSizePolicy, QScrollArea, QSplitter, QFrame, QButtonGroup
from PySide6.QtCore import Qt
from c_ui.a_global.ntheme import NTheme
from c_ui.b_components.a_custom.custom_toolbar import CustomToolBar
from c_ui.b_components.b_composite.app_statusbar_widget import AppStatusBarWidget
from c_ui.b_components.a_custom.custom_pushbutton import CustomButton
from b_core.a_manager.main_model_manager import MainModelManager
from c_ui.d_helpers.win_helper import WinHelper
from c_ui.c_windows.b_connection.connection_win_model import ConnectionWinModel


class ConnectionWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.setWindowTitle("Connection")
        self.resize(500, 600)

        self.model = ConnectionWinModel(self)

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
        # 2. 바디 영역 (전체 통 스크롤 적용)
        # ---------------------------------------------------------
        # 전체를 감싸는 스크롤 영역 생성
        self.body_scroll_area = QScrollArea()
        self.body_scroll_area.setObjectName("BodyScrollArea")
        self.body_scroll_area.setWidgetResizable(True) # 내부 컨테이너가 창 크기에 맞게 늘어나도록 설정
        self.body_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.body_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 스크롤 영역 안에 들어갈 거대한 바탕 컨테이너
        self.body_container = QWidget()
        self.body_layout = QVBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        # 좌우로 나누는 Splitter 생성
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.body_layout.addWidget(self.splitter)

        # --- 2-1. 스플릿터 왼쪽 ---
        self.left_pane = QFrame()
        self.left_pane.setObjectName("LeftPane")
        
        self.left_layout = QVBoxLayout(self.left_pane)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0) # 항목 사이 간격 제거
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- 2-2. 스플릿터 오른쪽 ---
        self.right_pane = QWidget()
        self.right_pane.setObjectName("RightPane")
        # 나중에 위젯 추가를 대비해 레이아웃 미리 세팅 (위에서부터 쌓이도록)
        self.right_layout = QVBoxLayout(self.right_pane)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 스플릿터에 양쪽 패널 추가
        self.splitter.addWidget(self.left_pane)
        self.splitter.addWidget(self.right_pane)
        
        # 스플릿터 초기 비율 설정 (예: 왼쪽 30%, 오른쪽 70%)
        self.splitter.setSizes([300, 700])

        # 스크롤 영역에 전체 바탕 컨테이너 세팅
        self.body_scroll_area.setWidget(self.body_container)

        # 메인 레이아웃에 '스크롤 영역'을 추가
        self.main_layout.addWidget(self.body_scroll_area, stretch=1)

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

            /* 3. 상태바 상단: 1px 회색 선 */
            QWidget#StatusBar {{
                border-top: 1px solid {border_color};
            }}
            QSplitter::handle {{ background-color: transparent; }}

            /* 왼쪽 패널 왼쪽 테두리 지정 (오른쪽이 낫다면 border-right로 변경) */
            QWidget#LeftPane {{ border-right: 1px solid {border_color}; }}
        """)   

    def __init_components(self):
        self.tag_list = MainModelManager().tag_manager.get_tags_in_folder("Connection")

        self.__init_toolbar()
        self.__init_edit_panel()
        self.init_connection_list()

    def __init_toolbar(self):
        # 4. 툴바 (ToolBar) 추가
        self.toolbox = CustomToolBar()
        self.toolbox.addAction("Scan Port")
        self.toolbox.addAction("Connect")
        self.toolbox.addAction("New")
        self.toolbox.addAction("Remove")
        self.toolbox.addAction("Save")
        self.title_bar_layout.addWidget(self.toolbox)
        self.title_bar_layout.addStretch()

        self.toolbox.actionTriggered.connect(self.model.on_toolbar_action)

    def __init_edit_panel(self):
        self.tag_comp_list = WinHelper().build_tag_defalut_components(self.right_layout, self.tag_list)

        for comp in self.tag_comp_list:
            if comp.tag_model.Name == "Name":
                self.name_tag_widget = comp
            elif comp.tag_model.Name == "Port":
                self.port_tag_widget = comp
                self.port_tag_widget.set_enable_dirty(False)
            elif comp.tag_model.Name == "Network":
                self.network_tag_widget = comp
            elif comp.tag_model.Name == "Address":
                self.address_tag_widget = comp
            elif comp.tag_model.Name == "Termination":
                self.termination_tag_widget = comp
            elif comp.tag_model.Name == "BaudRate":
                self.baudrate_tag_widget = comp
            elif comp.tag_model.Name == "Data Bits":
                self.databits_tag_widget = comp
            elif comp.tag_model.Name == "Parity":
                self.parity_tag_widget = comp
            elif comp.tag_model.Name == "Stop Bits":
                self.stopbits_tag_widget = comp

            comp.dirty_changed.connect(
                lambda: self.model.on_dirty_changed()
            )

    def init_connection_list(self):
        # 1. 기존 버튼 그룹 객체가 있다면 완전 해제 (메모리 누수 방지 및 시그널 해제)
        if hasattr(self, 'button_group') and self.button_group is not None:
            for btn in self.button_group.buttons():
                btn.deleteLater()
            self.button_group.deleteLater()

        self.button_group = QButtonGroup(self)
        self.button_group

        self.button_group.idToggled.connect(self.model.on_selected_connection)

        for index, conn in enumerate(self.model.connections_data):
            name = conn.get("name", "Unknown")
            
            # 리스트 항목 역할을 할 버튼 생성
            item_btn = CustomButton(name)
            item_btn.setFlat(True)
            item_btn.setObjectName("ListItemButton") # 스타일링을 위한 ID
            item_btn.setCheckable(True) # 선택된 상태를 유지할 수 있도록 설정

            self.left_layout.addWidget(item_btn)
            self.button_group.addButton(item_btn, id=index)

            # 만약 JSON에 "isSelect": true 가 있다면 초기 선택 상태로 만듦
            if conn.get("isSelect", False):
                item_btn.setChecked(True)      

    def closeEvent(self, event):
        # Model의 on_win_close 반환값이 True면 창 닫기 허용, False면 무시
        if self.model.on_win_close():
            event.accept()
        else:
            event.ignore()    
