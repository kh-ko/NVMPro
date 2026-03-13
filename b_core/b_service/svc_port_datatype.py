import uuid
from dataclasses import dataclass
from typing import Optional, Callable
from enum import StrEnum

# ==========================================
# 0. CancelToken
# ==========================================
class CancelToken:
    def __init__(self):
        self.is_canceled = False
        
    def cancel(self):
        self.is_canceled = True

# ==========================================
# 1. Enums
# ==========================================
class E_Command(StrEnum):
    SET_CONNECTION_INFO = "SET_CONNECTION_INFO"
    RUN = "RUN"
    STOP = "STOP"
    PAUSE = "PAUSE"
    TRACE = "TRACE"
    REQUEST_PACKET = "RequestPacket"
    PORT_CHECK = "PortCheck"

class E_SvcPortState(StrEnum):
    IDLE         = "Idle"
    RUN          = "Run"
    PAUSE        = "Pause"
    STOP         = "Stop"
    TRACE        = "Trace" 

class E_SvcPortCmdResult(StrEnum):
    SUCCESS         = "Success"
    PORT_ERROR      = "PortError"
    PORT_OPEN_ERROR = "PortOpenError"
    CMD_ERROR       = "CmdError"
    PARAM_ERROR     = "ParamError"
    SYS_ERROR       = "SysError"
    

# ==========================================
# 2. Dataclasses (Type-Safe Data Transfer)
# ==========================================
# 1) 통신 설정 전용
@dataclass(slots=True)
class ConnectionParams:
    port: str
    network: int = 1
    address: str = ""
    baudrate: int = 9600
    databits: int = 8
    parity: int = 0
    stopbits: int = 1
    termination: int = 0
    request: str = ""

# 2) 패킷 요청 전용
@dataclass(slots=True)
class PacketParams:
    request: str = ""
    termination: int = 0

@dataclass(slots=True)
class PortCheckRespParams:
    port: str = ""
    

# [입력용] 3. Queue 전달 객체
@dataclass(slots=True)
class SvcRequest:
    cmd: E_Command
    params: ConnectionParams | PacketParams | None = None    
    callback: Optional[Callable] = None
    cancel_token: Optional[CancelToken] = None  # ★ 토큰 추가

# [출력용] 4. UI로 쏘아올릴 결과 객체
@dataclass(slots=True)
class SvcResponse:
    cmd_result: E_SvcPortCmdResult = E_SvcPortCmdResult.SUCCESS
    rcv_str: str = ""
    error_msg: str = ""
    params: PortCheckRespParams | None = None    
    callback: Optional[Callable] = None
    cancel_token: Optional[CancelToken] = None  # ★ 토큰 추가