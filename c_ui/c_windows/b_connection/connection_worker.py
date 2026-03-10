import re
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker, QByteArray, QIODevice
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from b_core.d_model.tag_model import ComboItem  # 사용 중인 ComboItem 경로에 맞게 수정

class ConnectionWorker(QThread):
    # 쓰레드에서 UI(메인 쓰레드)로 데이터를 안전하게 전달하기 위한 Signal 정의
    progress_signal = Signal(list)
    finished_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False
        self._mutex = QMutex()

    def start_scan(self, protocol, network, address, baudrate, databits, parity, stopbits, termination):
        """스캔 작업을 초기화하고 쓰레드를 시작합니다."""
        with QMutexLocker(self._mutex):
            self._is_cancelled = False
        
        self.protocol    = protocol
        self.network     = network
        self.address     = address
        self.baudrate    = baudrate
        self.databits    = databits
        self.parity      = parity
        self.stopbits    = stopbits
        self.termination = termination

        self.start()

    def cancel(self):
        """스레드 내부 루프를 중단하도록 플래그를 설정합니다."""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True

    def is_running(self):
        return self.isRunning()

    def run(self):
        """QThread가 시작되면 백그라운드에서 실행되는 메인 로직입니다."""
        available_ports = QSerialPortInfo.availablePorts()
        valid_combo_items = []

        for port_info in available_ports:
            port_name = port_info.portName() + " : Not Checked"

            match = re.search(r'\d+', port_name)
            
            if match:
                port_value = int(match.group())
            else:
                port_value = port_name
                
            item = ComboItem(
                Label=port_name,
                Value=port_value,
                IsEnable=True
            )
            valid_combo_items.append(item)

            self.progress_signal.emit(valid_combo_items)
        
        for item in valid_combo_items:
            with QMutexLocker(self._mutex):
                if self._is_cancelled:
                    break
            # 추후 SerialPortManager 안에서 Send Receive 동작을 수행하자! 일단 보류
            resp_str = ""
            # resp_str = SerialPortManager().scan(item.Value, self.baudrate, self.databits, self.parity, self.stopbits, self.protocol.request)

            if resp_str and getattr(self.protocol, "response", None) and resp_str.startswith(self.protocol.response):
                item.Label = f"COM{item.Value} : {resp_str}" # (예시) 응답 내용으로 라벨 변경
            else:
                item.Label = f"COM{item.Value} : Unknown Device"

            self.progress_signal.emit(valid_combo_items)

        self.finished_signal.emit()