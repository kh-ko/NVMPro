from PySide6.QtCore import QObject
from b_core.a_manager.log_manager import LogManager
from c_ui.c_windows.b_connection.connection_win import ConnectionWin
from c_ui.d_helpers.win_helper import WinHelper

class MainWinModel(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view

    def on_local_toggled(self, checked):
        if not checked:
            # 꺼지는 이벤트 무시하고 다시 켜기 상태 유지
            self.view.btn_local.blockSignals(True)
            self.view.btn_local.setChecked(True)
            self.view.btn_local.blockSignals(False)
            return

        print("Local 토글 켜짐")
        # 다른 버튼은 끄기 (시그널 발생 방지)
        self.view.btn_remote.blockSignals(True)
        self.view.btn_remote.setChecked(False)
        self.view.btn_remote.blockSignals(False)

    def on_remote_toggled(self, checked):
        if not checked:
            # 꺼지는 이벤트 무시하고 다시 켜기 상태 유지
            self.view.btn_remote.blockSignals(True)
            self.view.btn_remote.setChecked(True)
            self.view.btn_remote.blockSignals(False)
            return

        print("Remote 토글 켜짐")
        # 다른 버튼은 끄기 (시그널 발생 방지)
        self.view.btn_local.blockSignals(True)
        self.view.btn_local.setChecked(False)
        self.view.btn_local.blockSignals(False)

    def on_toolbar_action(self, action):
        action_text = action.text()
        
        if action_text == "Connection":
            self.on_connection_clicked()
        elif action_text == "Parameter":
            self.on_parameter_clicked()
        elif action_text == "LogView":
            self.on_logview_clicked()
        elif action_text == "Help":
            self.on_help_clicked()

    def on_connection_clicked(self):
        print("Connection 메뉴 클릭됨")
        
        # WinHelper를 통해 싱글톤 패턴으로 창을 열거나 가져옵니다.
        WinHelper().show_window(ConnectionWin)

    def on_parameter_clicked(self):
        print("Parameter 메뉴 클릭됨")

    def on_logview_clicked(self):
        print("LogView 메뉴 클릭됨")
        LogManager().show_log_window()

    def on_help_clicked(self):
        print("Help 메뉴 클릭됨")
