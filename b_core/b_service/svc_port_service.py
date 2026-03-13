from typing import Optional, Any, Callable
from PySide6.QtCore import Signal
from svc_port_datatype import E_SvcPortState, E_Command, ConnectionParams, PacketParams, SvcRequest, SvcResponse, CancelToken
from svc_port_worker import SvcPortWorker


class SvcPortService:
    connection_info_changed = Signal(object)
    port_state_changed = Signal(E_SvcPortState)
    is_error_changed = Signal(bool)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        """데이터 초기화를 담당하는 내부 메서드"""
        self.canceled_requests = set()

        self.worker = SvcPortWorker()
        self.worker.start()

        self.connection_info : str = ""
        self.port_state : E_SvcPortState = E_SvcPortState.IDLE
        self.is_error : bool = False

        self.worker.connection_info_changed.connect(self._set_connection_info)
        self.worker.state_changed.connect(self._set_state)
        self.worker.is_error_changed.connect(self._set_is_error)
        self.worker.request_command_finished.connect(self._on_request_command_finished)

    def _set_connection_info(self, info: object):
        if info is None:
            info = ""
        self.connection_info = info
        self.connection_info_changed.emit(info)

    def _set_state(self, state: E_SvcPortState):
        self.port_state = state
        self.port_state_changed.emit(state)

    def _set_is_error(self, is_error: bool):
        self.is_error = is_error
        self.is_error_changed.emit(is_error)

    def _on_request_command_finished(self, response: SvcResponse):
        if response.cancel_token and response.cancel_token.is_canceled:
            return

        if response.callback is not None:
            try:
                response.callback(response)
            except RuntimeError:
                pass  # UI 소멸 시 예외 방어

    def cancel_request(self, req_id: str):
        """UI에서 특정 요청의 결과를 받고 싶지 않을 때 호출합니다."""
        if req_id:
            self.canceled_requests.add(req_id)
            
    def set_connection_info(self, params: ConnectionParams, callback: Optional[Callable] = None, cancel_token: Optional[CancelToken] = None):
        request = SvcRequest(cmd=E_Command.SET_CONNECTION_INFO, params=params, callback=callback, cancel_token=cancel_token)
        self.worker.req_queue.put(request)

    def run(self, callback: Optional[Callable] = None, cancel_token: Optional[CancelToken] = None):
        request = SvcRequest(cmd=E_Command.RUN, callback=callback, cancel_token=cancel_token)
        self.worker.req_queue.put(request)

    def stop(self, callback: Optional[Callable] = None, cancel_token: Optional[CancelToken] = None):
        request = SvcRequest(cmd=E_Command.STOP, callback=callback, cancel_token=cancel_token)
        self.worker.req_queue.put(request)

    def pause(self, callback: Optional[Callable] = None, cancel_token: Optional[CancelToken] = None):
        request = SvcRequest(cmd=E_Command.PAUSE, callback=callback, cancel_token=cancel_token)
        self.worker.req_queue.put(request)

    def port_check(self, params: ConnectionParams, callback: Optional[Callable] = None, cancel_token: Optional[CancelToken] = None):
        request = SvcRequest(cmd=E_Command.PORT_CHECK, params=params, callback=callback, cancel_token=cancel_token)
        self.worker.req_queue.put(request)