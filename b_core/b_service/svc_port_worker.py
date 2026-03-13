import time
import queue
from typing import Optional, Any
from PySide6.QtCore import QThread, Signal, QIODevice
from PySide6.QtSerialPort import QSerialPort 
from b_core.a_manager.log_manager import LogManager
from c_ui.b_components.b_composite.console_widget import MsgType
from svc_port_datatype import SvcRequest, SvcResponse, ConnectionParams, PacketParams, E_Command, E_SvcPortState, E_SvcPortCmdResult


# ==========================================
# Worker Thread 클래스 (실제 통신 담당)
# ==========================================
class SvcPortWorker(QThread):    
    # [Service 통신용 시그널]
    connection_info_changed = Signal(object)
    state_changed = Signal(E_SvcPortState)
    is_error_changed = Signal(bool)
    request_command_finished = Signal(object) 

    def __init__(self, req_queue: queue.Queue, parent=None):
        super().__init__(parent)
        self.req_queue = req_queue
        self._is_running = True
        self.state = E_SvcPortState.IDLE
        self.error_count = 0
        self.connection_info: Optional[ConnectionParams] = None
        self.termination_bytes = b'\r\n'
        self.rx_bytes = bytearray()
        self.serial_port = None 

    def set_state(self, new_state: E_SvcPortState):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(self.state)

    def _increment_error_count(self):
        # 상위 레이어는 구체적인 누적 횟수보다 에러 발생 여부 자체가 중요함
        if self.error_count == 0:
            self.is_error_changed.emit(True)
        self.error_count += 1
        
    def _reset_error_count(self):
        if self.error_count > 0: 
            self.error_count = 0
            self.is_error_changed.emit(False)        

    def _set_connection_info(self, params: Optional[ConnectionParams]):
        if params is None:
            self.connection_info = None
            self.connection_info_changed.emit("")
        else:
            self.connection_info = params
            self.termination_bytes = self._get_termination_bytes(params.termination)

            # 통신 설정값을 UI 표시용 직관적인 문자열로 변환
            parity_map = {0: 'N', 2: 'E', 3: 'O', 4: 'S', 5: 'M'}
            stop_map = {1: '1', 2: '2', 3: '1.5'}
            
            port = params.port  
            baud = params.baudrate
            data = params.databits
            p_str = parity_map.get(params.parity, '?')
            s_str = stop_map.get(params.stopbits, '?')
            
            info_str = f"{port}-{baud}-{data}-{p_str}-{s_str}"
            self.connection_info_changed.emit(info_str)

    def run(self):                        
        while self._is_running:
            try:
                # --------------------------------------------------
                # 1. 자동 모드 처리 (GUI 인터랙션 없이 주기적으로 동작)
                # --------------------------------------------------
                if self.state in (E_SvcPortState.RUN, E_SvcPortState.TRACE):
                    # 누적 에러 10회 초과 시 포트 재연결 (0.1초 대기로 GUI 블로킹 최소화)
                    if self.error_count > 10:
                        self._close_port()
                        self._open_port()
                        time.sleep(0.1)

                    if self.state == E_SvcPortState.RUN:
                        if self._proc_monitor_packet():
                            self._reset_error_count()
                        else:
                            self._increment_error_count()
                
                    else:
                        if self._proc_trace_packet():
                            self._reset_error_count()
                        else:
                            self._increment_error_count()

                # --------------------------------------------------
                # 2. Command Queue 확인 및 대기
                # --------------------------------------------------
                if self.req_queue.empty():
                    if self.state not in (E_SvcPortState.RUN, E_SvcPortState.TRACE):
                        time.sleep(0.1) 
                    continue

                # --------------------------------------------------
                # 3. Queue 명령 처리
                # --------------------------------------------------
                request: SvcRequest = self.req_queue.get(block=False) 

                while request.cancel_token and request.cancel_token.is_canceled:
                    self.req_queue.task_done()

                    if self.req_queue.empty():
                        request = None
                        break

                    request = self.req_queue.get(block=False) 
                    continue

                if request is None:
                    continue

                params = None
                cmd = None

                try:    
                    params   = request.params
                    cmd      = request.cmd
                    response = SvcResponse(
                        cmd_result = E_SvcPortCmdResult.SUCCESS,
                        rcv_str = "",
                        error_msg = "",
                        callback = request.callback
                    )

                    if cmd == E_Command.SET_CONNECTION_INFO:
                        if isinstance(params, ConnectionParams):
                            self.set_state(E_SvcPortState.RUN)
                            self._close_port()
                            self._set_connection_info(params)
                            self._open_port()  
                        else:
                            response.cmd_result = E_SvcPortCmdResult.PARAM_ERROR
                            response.error_msg = "Invalid parameters for SET_CONNECTION_INFO"                
                        
                    elif cmd == E_Command.RUN:
                        self.set_state(E_SvcPortState.RUN)
                        if self.serial_port is None or not self.serial_port.isOpen():
                            self._open_port()

                    elif cmd == E_Command.STOP:
                        self.set_state(E_SvcPortState.STOP)
                        self._close_port()
                        self._set_connection_info(None)
                        
                    elif cmd == E_Command.PAUSE:
                        self.set_state(E_SvcPortState.PAUSE)
                        self._close_port()
                        
                    elif cmd == E_Command.TRACE:
                        self.set_state(E_SvcPortState.TRACE)
                        
                    elif cmd == E_Command.REQUEST_PACKET:
                        if isinstance(params, PacketParams):
                            if self.state == E_SvcPortState.RUN:
                                result, rcv_str, err_msg = self._proc_request_packet(params.request)
                                
                                response.cmd_result = result
                                response.rcv_str = rcv_str
                                response.error_msg = err_msg

                                if result == E_SvcPortCmdResult.PORT_ERROR:
                                    self._increment_error_count()
                                else:
                                    self._reset_error_count()
                            else:
                                response.cmd_result = E_SvcPortCmdResult.CMD_ERROR
                                response.error_msg = "Port is not running"
                        else:
                            response.cmd_result = E_SvcPortCmdResult.PARAM_ERROR
                            response.error_msg = "Invalid parameters for RequestPacket" 

                    elif cmd == E_Command.PORT_CHECK:
                        if isinstance(params, ConnectionParams):
                            result, rcv_str, err_msg = self._proc_port_check(params)
                            response.cmd_result = result
                            response.rcv_str = rcv_str
                            response.error_msg = err_msg
                        else:
                            response.cmd_result = E_SvcPortCmdResult.PARAM_ERROR
                            response.error_msg = "Invalid parameters for PortCheck"
                    else:
                        response.cmd_result = E_SvcPortCmdResult.CMD_ERROR
                        response.error_msg = "Unknown command"

                except Exception as e:
                    response.cmd_result = E_SvcPortCmdResult.SYS_ERROR
                    response.error_msg = str(e)

                finally:
                    self.req_queue.task_done()
                    self.request_command_finished.emit(response)

            except queue.Empty:
                pass 

            except Exception as e:
                LogManager().log("SvcPortWorker", f"Exception in run loop: {e}", MsgType.ERROR)
                self._increment_error_count()
                
        # 스레드 종료 시 자원 안전하게 정리
        self._close_port()

    # ==========================================
    # 통신 제어 (Open / Close)
    # ==========================================
    def _open_port(self, config : ConnectionParams | None = None) -> bool:
        """QSerialPort 객체를 생성하고 GUI에서 설정한 Enum 값을 그대로 적용합니다."""
        self._close_port()

        # 인자로 받은 config가 있으면 그것을, 없으면 기존 멤버 변수 사용
        target_info = config if config else self.connection_info

        if not target_info:
            return False

        port = target_info.port
        if not port:
            return False

        try:
            self.serial_port = QSerialPort()
            self.serial_port.setPortName(port)
            self.serial_port.setBaudRate(target_info.baudrate)
            self.serial_port.setDataBits(target_info.databits)
            self.serial_port.setParity(target_info.parity) 
            self.serial_port.setStopBits(target_info.stopbits) 

            # 포트 열기 (읽기/쓰기 모드)
            if self.serial_port.open(QIODevice.OpenModeFlag.ReadWrite):
                return True
            else:
                self.serial_port = None
                return False
                
        except Exception:
            self.serial_port = None
            return False

    def _close_port(self):
        if self.serial_port and self.serial_port.isOpen():
            try:
                self.serial_port.close()
            except Exception:
                pass 
        
        self.serial_port = None

    # ==========================================
    # 패킷 처리 로직 (송수신)
    # ==========================================
    def _proc_port_check(self, params : ConnectionParams) -> tuple[E_SvcPortCmdResult, str, str]:
        # 1. 현재 상태 백업 (기존 연결 정보, 종료 문자, 포트 열림 여부)
        backup_info = self.connection_info
        backup_term = self.termination_bytes
        was_open = (self.serial_port is not None and self.serial_port.isOpen())

        # 2. 현재 포트 닫기
        self._close_port()

        # 3. 테스트용 임시 파라미터 및 종료 문자 적용
        self.termination_bytes = self._get_termination_bytes(params.termination)

        # 4. 테스트 파라미터로 포트 열기 시도
        is_opened = self._open_port(params)

        if is_opened:
            # 5. 기존 패킷 요청 함수를 그대로 재사용하여 송수신 테스트
            result, resp, error_msg = self._proc_request_packet(params.request)
        else:
            result, resp, error_msg = E_SvcPortCmdResult.PORT_OPEN_ERROR, "", ""

        self._close_port()  
        self.termination_bytes = backup_term
        if was_open and backup_info:
            self._open_port(backup_info)

        return result, resp, error_msg


    def _proc_request_packet(self, request) -> tuple[E_SvcPortCmdResult, str, str]:
        """문자열 패킷을 전송하고 응답 문자열을 반환합니다."""

        if self.serial_port is None or not self.serial_port.isOpen():
            return E_SvcPortCmdResult.PORT_ERROR, "", "Service Port Not Opened"

        try:
            # 1. 송신 데이터 인코딩 및 종료 문자 추가
            tx_data = request.encode('utf-8')
            tx_data += self.termination_bytes

            # 2. 패킷 전송
            if not self._send_packet(tx_data):
                return E_SvcPortCmdResult.PORT_ERROR, "", "Service Port Write Error"
            
            # 3. 패킷 수신
            result, rcv_str = self._receive_packet()
            if not result:
                return E_SvcPortCmdResult.PORT_ERROR, "", "Service Port Read Error"

            return E_SvcPortCmdResult.SUCCESS, rcv_str, ""

        except Exception as e:
            return E_SvcPortCmdResult.SYS_ERROR, "", f"Exception: {str(e)}"

    def _proc_monitor_packet(self) -> bool:
        if self.serial_port is None:
            return False
        
        # TODO: 고정 패킷으로 _send_packet() / _receive_packet() 수행 예정
        return True

    def _proc_trace_packet(self) -> bool:
        if self.serial_port is None:
            return False
        
        # TODO: _receive_trace_packet() 만 수행 예정 (수신 전용 특수 상황)
        return True
    
    def _send_packet(self, tx_data: bytes) -> bool:
        """바이트 데이터를 전송하고 완료될 때까지 대기합니다."""
        if self.serial_port is None or not self.serial_port.isOpen():
            return False
            
        # 송신 전 수신 버퍼 내 찌꺼기 데이터(노이즈 등) 확실하게 초기화
        self.serial_port.clear(QSerialPort.Direction.Input) 
        
        self.serial_port.write(tx_data)
        
        # 전송 완료 대기 (최대 50ms 타임아웃)
        if not self.serial_port.waitForBytesWritten(50):
            return False
        
        return True

    def _receive_packet(self) -> tuple[bool, str]:
        """응답을 대기하고 종료 문자가 오면 디코딩하여 문자열로 반환합니다."""
        if self.serial_port is None or not self.serial_port.isOpen():
            return False, ""

        self.rx_bytes.clear() 

        start_time = time.time()
        # 최초 100ms 대기
        if self.serial_port.waitForReadyRead(100):
            
            # 데이터가 들어오기 시작하면 루프를 돌며 끝을 확인
            while True:
                if self.serial_port.bytesAvailable() > 0:
                    self.rx_bytes.extend(self.serial_port.readAll().data())
                    
                    # 수신된 버퍼에 종료 문자가 포함되어 있는지 확인!
                    if self.termination_bytes in self.rx_bytes:
                        break # 프레임 수신 완료 -> 루프 탈출
                        
                # 아직 종료 문자가 안 왔다면, 나머지 데이터가 들어올 때까지 짧게(예: 10ms) 대기
                self.serial_port.waitForReadyRead(30)                

                if (time.time() - start_time) > 0.1:
                    return False, ""
            
            # 디코딩 전에 Bytes 상태에서 길이만큼 날려버리기
            term_len = len(self.termination_bytes)
            
            valid_bytes = self.rx_bytes
            
            # 가장 이상적인 경우: 정확히 끝에 종료 문자가 있는 경우
            if self.rx_bytes.endswith(self.termination_bytes):
                valid_bytes = self.rx_bytes[:-term_len] # 뒤에서부터 길이만큼 싹둑 자름
            else:
                # 안전장치: 혹시라도 종료 문자 뒤에 노이즈(쓰레기값)가 찰나의 순간 더 들어온 경우
                idx = self.rx_bytes.find(self.termination_bytes)
                if idx != -1:
                    valid_bytes = self.rx_bytes[:idx] # 종료 문자 이전까지만 취함
                else:
                    return False, ""

            # 종료 문자가 완벽히 제거된 순수 데이터만 문자열로 디코딩
            rcv_str = valid_bytes.decode('utf-8', errors='ignore')
            
            return True, rcv_str
        else:
            # 100ms 이내에 응답 없음
            return False, ""
    
    def stop(self):
        self._is_running = False

    def _get_termination_bytes(self, term_val: int) -> bytes:
        if term_val == 1:
            return b'\n'
        elif term_val == 2:
            return b'\r'
        else:
            return b'\r\n'

    