from __future__ import annotations

from app.models.domain import Observation


class GraphStore:
    def export_case(self, case_id: str, observations: list[Observation]) -> dict:
        raise NotImplementedError


class InMemoryGraphStore(GraphStore):
    def export_case(self, case_id: str, observations: list[Observation]) -> dict:
        nodes = []
        edges = []
        evidence_ids: set[str] = set()

        for obs in observations:
            evidence_ids.add(obs.evidence_id)
            nodes.append(
                {
                    "id": obs.id,
                    "type": obs.kind,
                    "label": obs.kind,
                    "status": obs.status.value,
                    "evidence_id": obs.evidence_id,
                    "source": obs.source,
                }
            )
            if obs.evidence_id:
                edges.append({"source": obs.evidence_id, "target": obs.id, "type": "observed_in"})

        for evidence_id in sorted(evidence_ids):
            nodes.append({"id": evidence_id, "type": "evidence", "label": "evidence", "status": "known"})
            edges.append({"source": case_id, "target": evidence_id, "type": "contains"})

        nodes.append({"id": case_id, "type": "case", "label": "case", "status": "active"})
        return {"case_id": case_id, "nodes": nodes, "edges": edges}


class VectorStore:
    def upsert(self, case_id: str, observations: list[Observation]) -> None:
        raise NotImplementedError

    def search(self, case_id: str, query: str) -> list[str]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, str]]] = {}

    def upsert(self, case_id: str, observations: list[Observation]) -> None:
        bucket = self._store.setdefault(case_id, [])
        for item in observations:
            bucket.append(
                {
                    "id": item.id,
                    "value": item.value,
                    "source": item.source,
                    "kind": item.kind,
                    "evidence_id": item.evidence_id,
                }
            )

    def search(self, case_id: str, query: str) -> list[str]:
        query_tokens = {token.lower() for token in query.split() if len(token) > 2}
        bucket = self._store.get(case_id, [])
        matches: list[tuple[int, str]] = []
        for item in bucket:
            text = " ".join([item.get("value", ""), item.get("source", ""), item.get("kind", "")]).lower()
            score = sum(1 for token in query_tokens if token in text)
            if score:
                matches.append((score, item["value"]))
        matches.sort(key=lambda pair: pair[0], reverse=True)
        return [value for _, value in matches[:10]]


class LangGraphOrchestrator:
    def run(self, stage: str, payload: dict) -> dict:
        raise NotImplementedError


class DeterministicWorkflowOrchestrator(LangGraphOrchestrator):
    def run(self, stage: str, payload: dict) -> dict:
        return {
            "stage": stage,
            "status": "completed",
            "payload": payload,
            "summary": "Deterministic workflow executed without external LLM or graph backend.",
        }
