from r360.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STREAM_STATE_UNSPECIFIED: _ClassVar[StreamState]
    STREAM_CREATED: _ClassVar[StreamState]
    STREAM_INITIALIZING: _ClassVar[StreamState]
    STREAM_READY: _ClassVar[StreamState]
    STREAM_RUNNING: _ClassVar[StreamState]
    STREAM_STOPPING: _ClassVar[StreamState]
    STREAM_STOPPED: _ClassVar[StreamState]
    STREAM_FAILED: _ClassVar[StreamState]

class DiagnosticSeverity(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIAGNOSTIC_SEVERITY_UNSPECIFIED: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_INFO: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_WARNING: _ClassVar[DiagnosticSeverity]
    DIAGNOSTIC_ERROR: _ClassVar[DiagnosticSeverity]

class DiagnosticCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIAGNOSTIC_CODE_UNSPECIFIED: _ClassVar[DiagnosticCode]
    SAMPLE_GAP: _ClassVar[DiagnosticCode]
    QUEUE_OVERFLOW: _ClassVar[DiagnosticCode]
    MALFORMED_METADATA: _ClassVar[DiagnosticCode]
    TRUNCATED_DATA: _ClassVar[DiagnosticCode]
    SOURCE_UNAVAILABLE: _ClassVar[DiagnosticCode]
    CONFIGURATION_INVALID: _ClassVar[DiagnosticCode]
    INTERNAL_INVARIANT_VIOLATION: _ClassVar[DiagnosticCode]
    BACKEND_FALLBACK: _ClassVar[DiagnosticCode]
    UNSUPPORTED_SAMPLE_FORMAT: _ClassVar[DiagnosticCode]
STREAM_STATE_UNSPECIFIED: StreamState
STREAM_CREATED: StreamState
STREAM_INITIALIZING: StreamState
STREAM_READY: StreamState
STREAM_RUNNING: StreamState
STREAM_STOPPING: StreamState
STREAM_STOPPED: StreamState
STREAM_FAILED: StreamState
DIAGNOSTIC_SEVERITY_UNSPECIFIED: DiagnosticSeverity
DIAGNOSTIC_INFO: DiagnosticSeverity
DIAGNOSTIC_WARNING: DiagnosticSeverity
DIAGNOSTIC_ERROR: DiagnosticSeverity
DIAGNOSTIC_CODE_UNSPECIFIED: DiagnosticCode
SAMPLE_GAP: DiagnosticCode
QUEUE_OVERFLOW: DiagnosticCode
MALFORMED_METADATA: DiagnosticCode
TRUNCATED_DATA: DiagnosticCode
SOURCE_UNAVAILABLE: DiagnosticCode
CONFIGURATION_INVALID: DiagnosticCode
INTERNAL_INVARIANT_VIOLATION: DiagnosticCode
BACKEND_FALLBACK: DiagnosticCode
UNSUPPORTED_SAMPLE_FORMAT: DiagnosticCode

class StreamLifecycleEvent(_message.Message):
    __slots__ = ("event_id", "session_id", "stream_id", "capture_uri", "state", "previous_state", "time", "samples_processed", "samples_total", "failure_code", "failure_message", "provenance")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_URI_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STATE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_PROCESSED_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_TOTAL_FIELD_NUMBER: _ClassVar[int]
    FAILURE_CODE_FIELD_NUMBER: _ClassVar[int]
    FAILURE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    PROVENANCE_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    session_id: str
    stream_id: str
    capture_uri: str
    state: StreamState
    previous_state: StreamState
    time: _common_pb2.DualTime
    samples_processed: int
    samples_total: int
    failure_code: str
    failure_message: str
    provenance: _common_pb2.ProvenanceReference
    def __init__(self, event_id: _Optional[str] = ..., session_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., capture_uri: _Optional[str] = ..., state: _Optional[_Union[StreamState, str]] = ..., previous_state: _Optional[_Union[StreamState, str]] = ..., time: _Optional[_Union[_common_pb2.DualTime, _Mapping]] = ..., samples_processed: _Optional[int] = ..., samples_total: _Optional[int] = ..., failure_code: _Optional[str] = ..., failure_message: _Optional[str] = ..., provenance: _Optional[_Union[_common_pb2.ProvenanceReference, _Mapping]] = ...) -> None: ...

class StreamDiagnostic(_message.Message):
    __slots__ = ("diagnostic_id", "session_id", "stream_id", "source_id", "sensor_id", "code", "severity", "message", "sample_range", "time", "dropped_sample_count", "provenance")
    DIAGNOSTIC_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    SENSOR_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RANGE_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    DROPPED_SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    PROVENANCE_FIELD_NUMBER: _ClassVar[int]
    diagnostic_id: str
    session_id: str
    stream_id: str
    source_id: str
    sensor_id: str
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    sample_range: _common_pb2.SampleRange
    time: _common_pb2.DualTime
    dropped_sample_count: int
    provenance: _common_pb2.ProvenanceReference
    def __init__(self, diagnostic_id: _Optional[str] = ..., session_id: _Optional[str] = ..., stream_id: _Optional[str] = ..., source_id: _Optional[str] = ..., sensor_id: _Optional[str] = ..., code: _Optional[_Union[DiagnosticCode, str]] = ..., severity: _Optional[_Union[DiagnosticSeverity, str]] = ..., message: _Optional[str] = ..., sample_range: _Optional[_Union[_common_pb2.SampleRange, _Mapping]] = ..., time: _Optional[_Union[_common_pb2.DualTime, _Mapping]] = ..., dropped_sample_count: _Optional[int] = ..., provenance: _Optional[_Union[_common_pb2.ProvenanceReference, _Mapping]] = ...) -> None: ...
