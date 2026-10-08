from app.models.domain import AuditRecord, Case, Event, Evidence, Finding, Observation, User
from app.repositories.base import Repository


class InMemoryRepository(Repository):
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.cases: dict[str, Case] = {}
        self.evidence: dict[str, Evidence] = {}
        self.observations: dict[str, Observation] = {}
        self.events: dict[str, Event] = {}
        self.findings: dict[str, Finding] = {}
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

    def add_event(self, event: Event) -> Event:
        self.events[event.id] = event
        return event

    def list_case_events(self, case_id: str) -> list[Event]:
        return [item for item in self.events.values() if item.case_id == case_id]

    def replace_case_events(self, case_id: str, events: list[Event]) -> None:
        for event_id in [event.id for event in self.list_case_events(case_id)]:
            self.events.pop(event_id, None)
        for event in events:
            self.events[event.id] = event

    def add_finding(self, finding: Finding) -> Finding:
        self.findings[finding.id] = finding
        return finding

    def list_case_findings(self, case_id: str) -> list[Finding]:
        return [item for item in self.findings.values() if item.case_id == case_id]

    def replace_case_findings(self, case_id: str, findings: list[Finding]) -> None:
        for finding_id in [finding.id for finding in self.list_case_findings(case_id)]:
            self.findings.pop(finding_id, None)
        for finding in findings:
            self.findings[finding.id] = finding

    def add_audit_record(self, record: AuditRecord) -> AuditRecord:
        self.audit_records[record.id] = record
        return record

    def list_audit_records(self, case_id: str | None = None) -> list[AuditRecord]:
        if case_id is None:
            return list(self.audit_records.values())
        return [record for record in self.audit_records.values() if record.case_id == case_id]
