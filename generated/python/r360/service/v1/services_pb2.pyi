from r360.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("service_name", "status", "service_version", "contract_version", "producer_git_sha", "time", "session_id")
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_VERSION_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_VERSION_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_GIT_SHA_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    status: str
    service_version: str
    contract_version: str
    producer_git_sha: str
    time: _common_pb2.DualTime
    session_id: str
    def __init__(self, service_name: _Optional[str] = ..., status: _Optional[str] = ..., service_version: _Optional[str] = ..., contract_version: _Optional[str] = ..., producer_git_sha: _Optional[str] = ..., time: _Optional[_Union[_common_pb2.DualTime, _Mapping]] = ..., session_id: _Optional[str] = ...) -> None: ...

class ReplayRequest(_message.Message):
    __slots__ = ("capture_uri", "mode", "session_id")
    class ReplayMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REPLAY_MODE_UNSPECIFIED: _ClassVar[ReplayRequest.ReplayMode]
        REPLAY_FAST: _ClassVar[ReplayRequest.ReplayMode]
        REPLAY_PACED: _ClassVar[ReplayRequest.ReplayMode]
    REPLAY_MODE_UNSPECIFIED: ReplayRequest.ReplayMode
    REPLAY_FAST: ReplayRequest.ReplayMode
    REPLAY_PACED: ReplayRequest.ReplayMode
    CAPTURE_URI_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    capture_uri: str
    mode: ReplayRequest.ReplayMode
    session_id: str
    def __init__(self, capture_uri: _Optional[str] = ..., mode: _Optional[_Union[ReplayRequest.ReplayMode, str]] = ..., session_id: _Optional[str] = ...) -> None: ...

class ReplayStatus(_message.Message):
    __slots__ = ("session_id", "state", "samples_processed", "samples_total", "failure_code", "failure_message")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_TOTAL_FIELD_NUMBER: _ClassVar[int]
    FAILURE_CODE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    state: str
    samples_processed: int
    samples_total: int
    failure_code: str
    failure_message: str
    def __init__(self, session_id: _Optional[str] = ..., state: _Optional[str] = ..., samples_processed: _Optional[int] = ..., samples_total: _Optional[int] = ..., failure_code: _Optional[str] = ..., failure_message: _Optional[str] = ...) -> None: ...
