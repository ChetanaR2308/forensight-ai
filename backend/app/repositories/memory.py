from app.models.domain import AuditRecord, Case, Evidence, Observation, User
from app.repositories.base import Repository


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.cases: dict[str, Case] = {}
        self.evidence: dict[str, Evidence] = {}
        self.observations: dict[str, Observation] = {}
        self.audit_records: dict[str, AuditRecord] = {}

    def list_users(self) -> list[User]:
        return list(self.users.values())

    def upsert_user(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def get_user_by_username(self, username: str) -> User | None:
        return next((user for user in self.users.values() if user.username == username), None)

    def create_case(self, case: Case) -> Case:
        self.cases[case.id] = case
        return case

    def get_case(self, case_id: str) -> Case | None:
        return self.cases.get(case_id)

    def list_cases(self) -> list[Case]:
        return list(self.cases.values())

    def update_case(self, case: Case) -> Case:
        self.cases[case.id] = case
        return case

    def delete_case(self, case_id: str) -> None:
        self.cases.pop(case_id, None)

    def add_evidence(self, evidence: Evidence) -> Evidence:
        self.evidence[evidence.id] = evidence
        return evidence

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        return self.evidence.get(evidence_id)

    def list_case_evidence(self, case_id: str) -> list[Evidence]:
        return [item for item in self.evidence.values() if item.case_id == case_id]

    def update_evidence(self, evidence: Evidence) -> Evidence:
        self.evidence[evidence.id] = evidence
        return evidence

    def add_observation(self, observation: Observation) -> Observation:
        self.observations[observation.id] = observation
        return observation

    def list_case_observations(self, case_id: str) -> list[Observation]:
        return [item for item in self.observations.values() if item.case_id == case_id]

    def list_evidence_observations(self, evidence_id: str) -> list[Observation]:
        return [item for item in self.observations.values() if item.evidence_id == evidence_id]

    def add_audit_record(self, record: AuditRecord) -> AuditRecord:
        self.audit_records[record.id] = record
        return record

    def list_audit_records(self, case_id: str | None = None) -> list[AuditRecord]:
        if case_id is None:
            return list(self.audit_records.values())
        return [record for record in self.audit_records.values() if record.case_id == case_id]
