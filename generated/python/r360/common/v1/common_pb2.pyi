from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DualTime(_message.Message):
    __slots__ = ("event_time", "ingest_time", "logical_time_ns")
    EVENT_TIME_FIELD_NUMBER: _ClassVar[int]
    INGEST_TIME_FIELD_NUMBER: _ClassVar[int]
    LOGICAL_TIME_NS_FIELD_NUMBER: _ClassVar[int]
    event_time: _timestamp_pb2.Timestamp
    ingest_time: _timestamp_pb2.Timestamp
    logical_time_ns: int
    def __init__(self, event_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ingest_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., logical_time_ns: _Optional[int] = ...) -> None: ...

class ObservationReference(_message.Message):
    __slots__ = ("observation_id", "source_id", "sensor_id", "time", "capture_id", "correlation_id", "scenario_id", "session_id", "entity_id")
    OBSERVATION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    SENSOR_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    CAPTURE_ID_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    SCENARIO_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    observation_id: str
    source_id: str
    sensor_id: str
    time: DualTime
    capture_id: str
    correlation_id: str
    scenario_id: str
    session_id: str
    entity_id: str
    def __init__(self, observation_id: _Optional[str] = ..., source_id: _Optional[str] = ..., sensor_id: _Optional[str] = ..., time: _Optional[_Union[DualTime, _Mapping]] = ..., capture_id: _Optional[str] = ..., correlation_id: _Optional[str] = ..., scenario_id: _Optional[str] = ..., session_id: _Optional[str] = ..., entity_id: _Optional[str] = ...) -> None: ...

class ProvenanceReference(_message.Message):
    __slots__ = ("processor_name", "processor_version", "model_id", "model_version", "signature_library_version", "configuration_sha256", "producer_git_sha", "container_image_digest")
    PROCESSOR_NAME_FIELD_NUMBER: _ClassVar[int]
    PROCESSOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_LIBRARY_VERSION_FIELD_NUMBER: _ClassVar[int]
    CONFIGURATION_SHA256_FIELD_NUMBER: _ClassVar[int]
    PRODUCER_GIT_SHA_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_IMAGE_DIGEST_FIELD_NUMBER: _ClassVar[int]
    processor_name: str
    processor_version: str
    model_id: str
    model_version: str
    signature_library_version: str
    configuration_sha256: str
    producer_git_sha: str
    container_image_digest: str
    def __init__(self, processor_name: _Optional[str] = ..., processor_version: _Optional[str] = ..., model_id: _Optional[str] = ..., model_version: _Optional[str] = ..., signature_library_version: _Optional[str] = ..., configuration_sha256: _Optional[str] = ..., producer_git_sha: _Optional[str] = ..., container_image_digest: _Optional[str] = ...) -> None: ...

class EntityReference(_message.Message):
    __slots__ = ("entity_id", "source_namespace")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    entity_id: str
    source_namespace: str
    def __init__(self, entity_id: _Optional[str] = ..., source_namespace: _Optional[str] = ...) -> None: ...

class SampleRange(_message.Message):
    __slots__ = ("first_sample_index", "last_sample_index")
    FIRST_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_SAMPLE_INDEX_FIELD_NUMBER: _ClassVar[int]
    first_sample_index: int
    last_sample_index: int
    def __init__(self, first_sample_index: _Optional[int] = ..., last_sample_index: _Optional[int] = ...) -> None: ...
