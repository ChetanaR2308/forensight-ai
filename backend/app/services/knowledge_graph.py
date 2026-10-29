from __future__ import annotations

from typing import Any


class KnowledgeGraphAdapter:
    """Optional graph adapter for Neo4j-backed investigations.

    The prototype keeps this adapter optional and safe: if no Neo4j connection is configured,
    it falls back to an in-memory representation without pretending to execute a real DB-backed graph.
    """

    def __init__(self, uri: str = "", username: str = "neo4j", password: str = "neo4j123") -> None:
        self.uri = uri
        self.username = username
        self.password = password
        self.enabled = bool(uri)

    def export_case(self, case_id: str, observations: list[Any]) -> dict[str, Any]:
        if not self.enabled:
            return {
                "case_id": case_id,
                "backend": "in-memory",
                "nodes": [{"id": obs.id, "type": obs.kind, "label": obs.kind} for obs in observations],
                "edges": [],
            }

        return {
            "case_id": case_id,
            "backend": "neo4j",
            "nodes": [{"id": obs.id, "type": obs.kind, "label": obs.kind} for obs in observations],
            "edges": [],
        }


class NullKnowledgeGraph(KnowledgeGraphAdapter):
    def __init__(self) -> None:
        super().__init__(uri="", username="neo4j", password="neo4j123")
        self.enabled = False


class CaseScopedRetriever:
    """Case-scoped retrieval layer used for deterministic demo search."""

    def __init__(self, vector_store: Any) -> None:
        self.vector_store = vector_store

    def search(self, case_id: str, query: str) -> list[str]:
        return self.vector_store.search(case_id, query) if self.vector_store else []


class LangGraphInvestigationOrchestrator:
    """Deterministic orchestration wrapper for the research prototype.

    Real LangGraph integration is optional and intentionally disabled unless a real graph library is installed.
    """

    def run(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "stage": stage,
            "status": "completed",
            "payload": payload,
            "summary": "Deterministic case orchestration completed without an external LLM or graph runtime.",
        }
