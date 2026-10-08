from typing import Any

from pydantic import BaseModel, Field

from app.models.domain import (
    Case,
    Citation,
    CorrelationRelationship,
    EvidenceGap,
    Evidence,
    Event,
    InvestigationAnswer,
    InvestigationRun,
    Observation,
    ProcessingStatus,
    Report,
    Role,
)


class HealthResponse(BaseModel):
    status: str


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class UserSummary(BaseModel):
    id: str
    username: str
    role: Role


class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class CaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class EvidenceUploadResponse(BaseModel):
    evidence: Evidence
    observations: list[Observation]


class IntegrityCheckResponse(BaseModel):
    evidence_id: str
    expected_sha256: str
    actual_sha256: str
    matches: bool


class TimelineResponse(BaseModel):
    case_id: str
    events: list[Event]


class ProcessingStatusResponse(BaseModel):
    evidence_id: str
    status: ProcessingStatus
    version: str
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class InvestigationQueryRequest(BaseModel):
    question: str = Field(min_length=3)


class InvestigationQueryResponse(BaseModel):
    result: InvestigationAnswer


class ReportResponse(BaseModel):
    report: Report


class CorrelationResponse(BaseModel):
    case_id: str
    relationships: list[CorrelationRelationship]


class GapResponse(BaseModel):
    case_id: str
    gaps: list[EvidenceGap]


class WorkflowRunResponse(BaseModel):
    run: InvestigationRun


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]


class CaseWithEvidence(BaseModel):
    case: Case
    evidence: list[Evidence]
    observations: list[Observation]
    citations: list[Citation]
