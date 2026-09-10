from google.protobuf import timestamp_pb2 as _timestamp_pb2
from r360.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MissionEvent(_message.Message):
    __slots__ = ("event_id", "event_type", "start_time", "end_time", "entities", "evidence_ids", "confidence", "attributes")
    class AttributesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    event_id: str
    event_type: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    entities: _containers.RepeatedCompositeFieldContainer[_common_pb2.EntityReference]
    evidence_ids: _containers.RepeatedScalarFieldContainer[str]
    confidence: float
    attributes: _containers.ScalarMap[str, str]
    def __init__(self, event_id: _Optional[str] = ..., event_type: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[_common_pb2.EntityReference, _Mapping]]] = ..., evidence_ids: _Optional[_Iterable[str]] = ..., confidence: _Optional[float] = ..., attributes: _Optional[_Mapping[str, str]] = ...) -> None: ...

class MissionEpisode(_message.Message):
    __slots__ = ("episode_id", "episode_type", "start_time", "end_time", "entities", "event_ids", "evidence_ids", "confidence")
    EPISODE_ID_FIELD_NUMBER: _ClassVar[int]
    EPISODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    EVENT_IDS_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    episode_id: str
    episode_type: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    entities: _containers.RepeatedCompositeFieldContainer[_common_pb2.EntityReference]
    event_ids: _containers.RepeatedScalarFieldContainer[str]
    evidence_ids: _containers.RepeatedScalarFieldContainer[str]
    confidence: float
    def __init__(self, episode_id: _Optional[str] = ..., episode_type: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[_common_pb2.EntityReference, _Mapping]]] = ..., event_ids: _Optional[_Iterable[str]] = ..., evidence_ids: _Optional[_Iterable[str]] = ..., confidence: _Optional[float] = ...) -> None: ...

class ReasoningOutcome(_message.Message):
    __slots__ = ("outcome_id", "outcome_type", "episode_id", "assessment", "confidence", "supporting_evidence_ids", "contradicting_evidence_ids", "provenance")
    OUTCOME_ID_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_TYPE_FIELD_NUMBER: _ClassVar[int]
    EPISODE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSESSMENT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SUPPORTING_EVIDENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    CONTRADICTING_EVIDENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    PROVENANCE_FIELD_NUMBER: _ClassVar[int]
    outcome_id: str
    outcome_type: str
    episode_id: str
    assessment: str
    confidence: float
    supporting_evidence_ids: _containers.RepeatedScalarFieldContainer[str]
    contradicting_evidence_ids: _containers.RepeatedScalarFieldContainer[str]
    provenance: _common_pb2.ProvenanceReference
    def __init__(self, outcome_id: _Optional[str] = ..., outcome_type: _Optional[str] = ..., episode_id: _Optional[str] = ..., assessment: _Optional[str] = ..., confidence: _Optional[float] = ..., supporting_evidence_ids: _Optional[_Iterable[str]] = ..., contradicting_evidence_ids: _Optional[_Iterable[str]] = ..., provenance: _Optional[_Union[_common_pb2.ProvenanceReference, _Mapping]] = ...) -> None: ...
