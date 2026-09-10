from r360.common.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NoveltyDecision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOVELTY_DECISION_UNSPECIFIED: _ClassVar[NoveltyDecision]
    NOVELTY_KNOWN: _ClassVar[NoveltyDecision]
    NOVELTY_UNCERTAIN: _ClassVar[NoveltyDecision]
    NOVELTY_UNKNOWN: _ClassVar[NoveltyDecision]

class EvidenceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVIDENCE_TYPE_UNSPECIFIED: _ClassVar[EvidenceType]
    SIGNAL_DETECTION: _ClassVar[EvidenceType]
    PULSE_DETECTION: _ClassVar[EvidenceType]
    RF_FEATURE_SET: _ClassVar[EvidenceType]
    WAVEFORM_CLASSIFICATION: _ClassVar[EvidenceType]
    RADAR_BEHAVIOR: _ClassVar[EvidenceType]
    EW_BEHAVIOR: _ClassVar[EvidenceType]
    NOVEL_RF_BEHAVIOR: _ClassVar[EvidenceType]
NOVELTY_DECISION_UNSPECIFIED: NoveltyDecision
NOVELTY_KNOWN: NoveltyDecision
NOVELTY_UNCERTAIN: NoveltyDecision
NOVELTY_UNKNOWN: NoveltyDecision
EVIDENCE_TYPE_UNSPECIFIED: EvidenceType
SIGNAL_DETECTION: EvidenceType
PULSE_DETECTION: EvidenceType
RF_FEATURE_SET: EvidenceType
WAVEFORM_CLASSIFICATION: EvidenceType
RADAR_BEHAVIOR: EvidenceType
EW_BEHAVIOR: EvidenceType
NOVEL_RF_BEHAVIOR: EvidenceType

class Feature(_message.Message):
    __slots__ = ("name", "numeric_value", "string_value", "bool_value", "integer_value", "unit", "confidence", "method", "source_detection_ids")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NUMERIC_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    INTEGER_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DETECTION_IDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    numeric_value: float
    string_value: str
    bool_value: bool
    integer_value: int
    unit: str
    confidence: float
    method: str
    source_detection_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., numeric_value: _Optional[float] = ..., string_value: _Optional[str] = ..., bool_value: bool = ..., integer_value: _Optional[int] = ..., unit: _Optional[str] = ..., confidence: _Optional[float] = ..., method: _Optional[str] = ..., source_detection_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class Classification(_message.Message):
    __slots__ = ("classification_id", "taxonomy", "class_path", "confidence", "model_id", "model_version")
    CLASSIFICATION_ID_FIELD_NUMBER: _ClassVar[int]
    TAXONOMY_FIELD_NUMBER: _ClassVar[int]
    CLASS_PATH_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_VERSION_FIELD_NUMBER: _ClassVar[int]
    classification_id: str
    taxonomy: str
    class_path: str
    confidence: float
    model_id: str
    model_version: str
    def __init__(self, classification_id: _Optional[str] = ..., taxonomy: _Optional[str] = ..., class_path: _Optional[str] = ..., confidence: _Optional[float] = ..., model_id: _Optional[str] = ..., model_version: _Optional[str] = ...) -> None: ...

class NoveltyAssessment(_message.Message):
    __slots__ = ("known_class_confidence", "novelty_score", "decision", "nearest_known_class", "nearest_known_similarity", "cluster_candidate_id")
    KNOWN_CLASS_CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    NOVELTY_SCORE_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    NEAREST_KNOWN_CLASS_FIELD_NUMBER: _ClassVar[int]
    NEAREST_KNOWN_SIMILARITY_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    known_class_confidence: float
    novelty_score: float
    decision: NoveltyDecision
    nearest_known_class: str
    nearest_known_similarity: float
    cluster_candidate_id: str
    def __init__(self, known_class_confidence: _Optional[float] = ..., novelty_score: _Optional[float] = ..., decision: _Optional[_Union[NoveltyDecision, str]] = ..., nearest_known_class: _Optional[str] = ..., nearest_known_similarity: _Optional[float] = ..., cluster_candidate_id: _Optional[str] = ...) -> None: ...

class DerivedEvidence(_message.Message):
    __slots__ = ("evidence_id", "observation", "evidence_type", "features", "classifications", "novelty", "confidence", "provenance", "related_evidence_ids", "sample_range")
    EVIDENCE_ID_FIELD_NUMBER: _ClassVar[int]
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    CLASSIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    NOVELTY_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    PROVENANCE_FIELD_NUMBER: _ClassVar[int]
    RELATED_EVIDENCE_IDS_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_RANGE_FIELD_NUMBER: _ClassVar[int]
    evidence_id: str
    observation: _common_pb2.ObservationReference
    evidence_type: EvidenceType
    features: _containers.RepeatedCompositeFieldContainer[Feature]
    classifications: _containers.RepeatedCompositeFieldContainer[Classification]
    novelty: NoveltyAssessment
    confidence: float
    provenance: _common_pb2.ProvenanceReference
    related_evidence_ids: _containers.RepeatedScalarFieldContainer[str]
    sample_range: _common_pb2.SampleRange
    def __init__(self, evidence_id: _Optional[str] = ..., observation: _Optional[_Union[_common_pb2.ObservationReference, _Mapping]] = ..., evidence_type: _Optional[_Union[EvidenceType, str]] = ..., features: _Optional[_Iterable[_Union[Feature, _Mapping]]] = ..., classifications: _Optional[_Iterable[_Union[Classification, _Mapping]]] = ..., novelty: _Optional[_Union[NoveltyAssessment, _Mapping]] = ..., confidence: _Optional[float] = ..., provenance: _Optional[_Union[_common_pb2.ProvenanceReference, _Mapping]] = ..., related_evidence_ids: _Optional[_Iterable[str]] = ..., sample_range: _Optional[_Union[_common_pb2.SampleRange, _Mapping]] = ...) -> None: ...
