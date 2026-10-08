from abc import ABC, abstractmethod

from app.models.domain import Observation


class GraphStore(ABC):
    @abstractmethod
    def export_case(self, case_id: str, observations: list[Observation]) -> dict: ...


class InMemoryGraphStore(GraphStore):
    def export_case(self, case_id: str, observations: list[Observation]) -> dict:
        return {
            "case_id": case_id,
            "nodes": [{"id": obs.id, "type": obs.kind} for obs in observations],
            "edges": [],
        }


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, case_id: str, observations: list[Observation]) -> None: ...

    @abstractmethod
    def search(self, case_id: str, query: str) -> list[str]: ...


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._store: dict[str, list[str]] = {}

    def upsert(self, case_id: str, observations: list[Observation]) -> None:
        self._store.setdefault(case_id, [])
        self._store[case_id].extend(observation.value for observation in observations)

    def search(self, case_id: str, query: str) -> list[str]:
        values = self._store.get(case_id, [])
        return [value for value in values if query.lower() in value.lower()]


class LangGraphOrchestrator(ABC):
    @abstractmethod
    def run(self, stage: str, payload: dict) -> dict: ...


class DeterministicWorkflowOrchestrator(LangGraphOrchestrator):
    def run(self, stage: str, payload: dict) -> dict:
        return {"stage": stage, "status": "completed", "payload": payload}
