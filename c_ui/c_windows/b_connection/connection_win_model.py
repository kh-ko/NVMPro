from b_core.a_manager.tag_manager import TagManager
import os
import json
import re
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox
from PySide6.QtSerialPort import QSerialPortInfo
from b_core.e_define.file_folder_define import CONNECTIONS_JSON_FILE
from b_core.a_manager.log_manager import LogManager
from b_core.d_model.tag_model import ComboItem
from b_core.b_service.svc_port_service import SvcPortService
from b_core.b_service.svc_port_datatype import CancelToken, ConnectionParams, SvcResponse, E_SvcPortCmdResult, PortCheckRespParams
from c_ui.b_components.a_custom.custom_pushbutton import CustomButton
from c_ui.d_helpers.tag_widget_helper import TagWidgetHelper
from c_ui.d_helpers.json_helper import JsonHelper
from c_ui.c_windows.b_connection.connection_worker import ConnectionWorker


class ConnectionWinModel(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view

        self.selected_data = None
        self.selected_index = -1
        self.connections_data = JsonHelper().load_json(CONNECTIONS_JSON_FILE)

        self.cancel_token = CancelToken()

    def on_win_close(self):
        self.cancel_token.cancel()
        return True

    def on_toolbar_action(self, action):
        self.view.clearFocus() 
        self.view.setFocus()

        action_text = action.text()
        
        if action_text == "Scan Port":
            self.on_scan_port_clicked()
        elif action_text == "Connect":
            self.on_connect_clicked()
        elif action_text == "Save":
            self.on_save_settings_clicked()
        elif action_text == "New":
            self.on_new_settings_clicked()
        elif action_text == "Remove":
            self.on_delete_settings_clicked()

    def on_selected_connection(self, index, checked):
        if not checked:
            return

        self.__set_connection_info(index)       
                    
    def on_scan_port_clicked(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Com Port Scan")
        msg_box.setText("Would you like to apply the changes and scan for ports?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        btn_apply_scan = msg_box.addButton("Apply and Scan", QMessageBox.ButtonRole.AcceptRole)
        btn_cancel = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()
        if msg_box.clickedButton() == btn_apply_scan:
            self.on_save_settings_clicked()

            params = ConnectionParams(
                port="",
                network=self.view.network_tag_widget.tag_model.RemoteValue,
                address=self.view.address_tag_widget.tag_model.RemoteValue,
                baudrate=self.view.baudrate_tag_widget.tag_model.RemoteValue,
                databits=self.view.databits_tag_widget.tag_model.RemoteValue,
                parity=self.view.parity_tag_widget.tag_model.RemoteValue,
                stopbits=self.view.stopbits_tag_widget.tag_model.RemoteValue,
                termination=self.view.termination_tag_widget.tag_model.RemoteValue,
                request="i:83"
            )
            SvcPortService().port_check(params, self.on_scan_result, self.cancel_token)
        elif msg_box.clickedButton() == btn_cancel:
            pass

    def on_scan_result(self, response: SvcResponse):
        if response.cancel_token and response.cancel_token.is_canceled:
            return

        if response.params is None:
            return

        port_name = response.params.port
        description = ""
        enable = False

        if response.cmd_result == E_SvcPortCmdResult.PORT_OPEN_ERROR:
            # already used device
            description = "already in use."
        elif response.cmd_result == E_SvcPortCmdResult.PORT_ERROR:
            # unknown device
            description = "unknown device."
        elif response.cmd_result == E_SvcPortCmdResult.CMD_ERROR:
            # unknown error
            description = "unknown error."
        elif response.cmd_result == E_SvcPortCmdResult.PARAM_ERROR:
            # unknown error
            description = "unknown error."
        elif response.cmd_result == E_SvcPortCmdResult.SYS_ERROR:
            # unknown error
            description = "unknown error."
        elif response.cmd_result == E_SvcPortCmdResult.SUCCESS:
            enable = True
            description = response.rcv_str
        

    def on_connect_clicked(self):
        pass

    def on_save_settings_clicked(self):
        self.__update_connection_data_by_ui(self.selected_data)


    def on_new_settings_clicked(self):
        new_data = {}
        new_data["isSelect"] = True
        if self.selected_data is not None:
            self.selected_data["isSelect"] = False

        self.connections_data.append(new_data)
        self.__update_connection_data_by_ui(new_data)
        
    def on_delete_settings_clicked(self):
        if self.selected_data is None or not hasattr(self, 'selected_index'):
            return
        
        if len(self.connections_data) <= 1:
            QMessageBox.warning(self.view, "Cannot Delete", "You must keep at least one connection setting.")
            return

        if 0 <= self.selected_index < len(self.connections_data):
            del self.connections_data[self.selected_index]

        self.connections_data[0]["isSelect"] = True
        self.__update_connection_data_by_ui(None)
        
    def on_dirty_changed(self):
        # UI에서 태그 값이 변경될 때마다 호출되는 함수입니다.
        has_dirty = any(getattr(comp, 'dirty', False) for comp in self.view.tag_comp_list)        
        self.view.toolbox.set_action_enabled("Save", has_dirty)

    def __set_connection_info(self, index):
        self.selected_index = index
        self.selected_data = self.connections_data[index]

        TagWidgetHelper().reset_tag_remote_value(self.view.tag_comp_list)

        for tag in self.view.tag_list:
            if tag.Name == "Name":
                tag.update_remote_value(self.selected_data.get("name", ""))
            elif tag.Name == "Network":
                tag.update_remote_value(self.selected_data.get("network", 1))
            elif tag.Name == "Address":
                tag.update_remote_value(self.selected_data.get("address", 0))
            elif tag.Name == "Termination":
                tag.update_remote_value(self.selected_data.get("termination", 0))
            elif tag.Name == "BaudRate":
                tag.update_remote_value(self.selected_data.get("baudrate", 38400))
            elif tag.Name == "Data Bits":
                tag.update_remote_value(self.selected_data.get("dataBits", 7))
            elif tag.Name == "Parity":
                tag.update_remote_value(self.selected_data.get("parity", 2))
            elif tag.Name == "Stop Bits":
                tag.update_remote_value(self.selected_data.get("stopBits", 1))

    def __update_connection_data_by_ui(self, selected_data):

        if selected_data is not None:
            TagWidgetHelper().update_tag_local_value(self.view.tag_comp_list)

            if self.view.name_tag_widget is not None:
                selected_data["name"] = self.view.name_tag_widget.tag_model.LocalWriteValue
            if self.view.network_tag_widget is not None:
                selected_data["network"] = self.view.network_tag_widget.tag_model.LocalWriteValue
            if self.view.address_tag_widget is not None:
                selected_data["address"] = self.view.address_tag_widget.tag_model.LocalWriteValue
            if self.view.termination_tag_widget is not None:
                selected_data["termination"] = self.view.termination_tag_widget.tag_model.LocalWriteValue
            if self.view.baudrate_tag_widget is not None:
                selected_data["baudrate"] = self.view.baudrate_tag_widget.tag_model.LocalWriteValue
            if self.view.databits_tag_widget is not None:
                selected_data["dataBits"] = self.view.databits_tag_widget.tag_model.LocalWriteValue
            if self.view.parity_tag_widget is not None:
                selected_data["parity"] = self.view.parity_tag_widget.tag_model.LocalWriteValue
            if self.view.stopbits_tag_widget is not None:
                selected_data["stopBits"] = self.view.stopbits_tag_widget.tag_model.LocalWriteValue

        TagWidgetHelper().reset_tag_local_value(self.view.tag_comp_list)

        JsonHelper().save_json(CONNECTIONS_JSON_FILE, self.connections_data)

        #view 쪽에서 리스트를 갱신하면서 자동으로 on_selected_connection 가 호출되어서 selected_data 가 업데이트됨
        self.view.init_connection_list()

    def __get_available_ports(self):
        available_ports = QSerialPortInfo.availablePorts()

        ports = []

        # 2. 포트 리스트를 순회하며 ComboItem 객체 생성
        for port in available_ports:
            port_name = port.portName() + " : Not Checked"  # 예: "COM1", "COM3"
            
            # 정규표현식을 사용하여 문자열에서 숫자만 추출
            match = re.search(r'\d+', port_name)
            
            if match:
                # 숫자가 발견되면 int형으로 변환 (예: "COM1" -> 1)
                port_value = int(match.group())
            else:
                # 만약 숫자가 없는 예외적인 이름이라면 문자열 그대로 사용 (에러 방지용)
                port_value = port_name
                
            # 3. ComboItem 인스턴스 생성
            item = ComboItem(
                Label=port_name,
                Value=port_value,
                IsEnable=True
            )
            ports.append(item)
        
        if self.view.port_tag_widget is not None and self.view.port_tag_widget.tag_model is not None:
            self.view.port_tag_widget.tag_model.set_options(ports)
            self.view.port_tag_widget.tag_model.reset_remote_value()
        
