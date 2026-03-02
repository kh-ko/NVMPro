from core.manager.log_manager import LogManager

class HomeViewModel:
    def __init__(self, view):
        """
        HomeWindow (view) 인스턴스를 주입받아 이벤트와 데이터 로직을 연결합니다.
        """
        self.view = view
        """View의 시그널을 ViewModel의 핸들러에 연결합니다."""
        self.view.mainmenu_frame.action_logview.triggered.connect(self.on_logview_clicked)

    def on_mode_changed(self, route_key: str):
        """
        SegmentedWidget의 선택이 바뀔 때마다 호출됩니다.
        route_key 파라미터로 현재 선택된 아이템의 키값('local' 또는 'remote')이 넘어옵니다.
        """
        if route_key == 'local':
            print("현재 모드: Local (수동 제어 활성화)")
            LogManager().log("수동 제어(Local) 모드로 변경되었습니다.")
            # 향후 로직 구현
        elif route_key == 'remote':
            print("현재 모드: Remote (원격 제어 활성화)")
            LogManager().log("원격 제어(Remote) 모드로 변경되었습니다.")
            # 향후 로직 구현

    def on_logview_clicked(self):
        """Show Log 버튼 클릭 시 호출됩니다."""
        print("Show Log 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")
        LogManager().show_log_window()
