from b_core.a_manager.log_manager import LogManager
from b_core.a_manager.main_model_manager import MainModelManager
from ..b_connection.connection_win import ConnectionWin

class MainViewModel:
    def __init__(self, view):
        """
        MainWindow (view) 인스턴스를 주입받아 이벤트와 데이터 로직을 연결합니다.
        """
        self.view = view
        """View의 시그널을 ViewModel의 핸들러에 연결합니다."""
        self.view.top_menu_frame.action_connection.triggered.connect(self.on_connection_clicked)
        self.view.top_menu_frame.acc_switch.mode_requested.connect(self.on_mode_changed)

        self.main_model_manager = MainModelManager()

    def on_mode_changed(self, route_key: int):
        """
        SegmentedWidget의 선택이 바뀔 때마다 호출됩니다.
        route_key 파라미터로 현재 선택된 아이템의 키값('local' 또는 'remote')이 넘어옵니다.
        """
        if route_key == 0:
            print("현재 모드: Local (수동 제어 활성화)")
            LogManager().log("수동 제어(Local) 모드로 변경되었습니다.")
            # 향후 로직 구현
        elif route_key == 1:
            print("현재 모드: Remote (원격 제어 활성화)")
            LogManager().log("원격 제어(Remote) 모드로 변경되었습니다.")
            # 향후 로직 구현
        self.view.top_menu_frame.acc_switch.set_check(route_key)

    def on_logview_clicked(self):
        """Show Log 버튼 클릭 시 호출됩니다."""
        print("Show Log 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")
        LogManager().show_log_window()

    def on_connection_clicked(self):
        """Show Connection 버튼 클릭 시 호출됩니다."""
        print("Show Connection 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")
        
        # 윈도우 인스턴스가 가비지 컬렉터(GC)에 의해 삭제되는 것을 방지하기 위해 
        # 클래스 멤버 변수(self)에 참조를 유지시킵니다.
        if not hasattr(self, 'connection_win') or not self.connection_win.isVisible():
            self.connection_win = ConnectionWin()
            
        self.connection_win.show()
        self.connection_win.raise_()
        self.connection_win.activateWindow()
