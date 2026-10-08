from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Role(str, Enum):
    investigator = "investigator"
    analyst = "analyst"
    admin = "admin"


class ProcessingStatus(str, Enum):
    uploaded = "uploaded"
    processed = "processed"
    failed = "failed"


class ObservationStatus(str, Enum):
    observed = "observed"
    inferred = "inferred"
    correlated = "correlated"
    uncertain = "uncertain"
    conflicting = "conflicting"
    inconclusive = "inconclusive"


class UncertaintyStatus(str, Enum):
    certain = "certain"
    uncertain = "uncertain"
    conflicting = "conflicting"
    inconclusive = "inconclusive"


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    password_hash: str
    role: Role


class Citation(BaseModel):
    evidence_id: str
    observation_id: str | None = None
    source: str
    timestamp: datetime | None = None


class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    actor_id: str
    action: str
    case_id: str | None = None
    evidence_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = Field(default_factory=dict)


class Case(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    owner_id: str
    collaborators: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    storage_path: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_status: ProcessingStatus = ProcessingStatus.uploaded
    metadata: dict = Field(default_factory=dict)


class Observation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    evidence_id: str
    kind: str
    value: str
    source: str
    source_timestamp: datetime | None = None
    location: str | None = None
    processing_stage: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: ObservationStatus
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    timestamp: datetime
    description: str
    evidence_id: str | None = None
    observation_ids: list[str] = Field(default_factory=list)
    status: ObservationStatus = ObservationStatus.correlated


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    case_id: str
    summary: str
    status: UncertaintyStatus
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)


class InvestigationAnswer(BaseModel):
    answer: str
    mode: Literal["deterministic", "llm"]
    status: UncertaintyStatus
    citations: list[Citation] = Field(default_factory=list)


class Report(BaseModel):
    case_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: str
    findings: list[Finding]
    conflicts: list[str]
    evidence_gaps: list[str]
    suggested_next_actions: list[str]
