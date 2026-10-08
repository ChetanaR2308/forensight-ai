from app.models.domain import AuditRecord
from app.repositories.base import Repository


class AuditService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def log(
        self,
        actor_id: str,
        action: str,
        case_id: str | None = None,
        evidence_id: str | None = None,
        details: dict | None = None,
    ) -> AuditRecord:
        record = AuditRecord(
            actor_id=actor_id,
            action=action,
            case_id=case_id,
            evidence_id=evidence_id,
            details=details or {},
        )
        return self.repository.add_audit_record(record)
