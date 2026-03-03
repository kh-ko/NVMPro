from c_ui.b_components.b_composite.base_win import BaseWin
from c_ui.d_helpers.TagComponentHelper import TagComponentHelper
from b_core.a_manager.tag_manager import TagManager

class ConnectionWin(BaseWin):
    def __init__(self):
        super().__init__()
        self.tag_manager = TagManager()

        self.setWindowTitle("Connection Settings")
        self.resize(600, 600)

        self.add_action("Port Scan" , self.on_port_scan_clicked )     
        self.add_action("Save"      , self.on_save_clicked      )
        self.add_action("Connection", self.on_connection_clicked)
        
        self.form_layout, self.ui_widgets = TagComponentHelper.build_tag_frame(self.tag_manager, "Connection")

        self.body_layout.addLayout(self.form_layout)
        
    def on_port_scan_clicked(self):
        print("Port Scan 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")

    def on_save_clicked(self):
        print("Save 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")

    def on_connection_clicked(self):
        print("Connection 버튼이 클릭되었습니다. (ViewModel에서 이벤트 처리)")