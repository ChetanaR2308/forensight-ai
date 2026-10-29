from __future__ import annotations

from typing import Any


class CaseScopedRetriever:
    """Case-scoped retrieval using the in-memory vector store.

    This provides retrieval restricted to the case ID in the demo implementation and prevents
    cross-case leakage by design.
    """

    def __init__(self, vector_store: Any) -> None:
        self.vector_store = vector_store

    def retrieval(self, case_id: str, query: str) -> list[str]:
        if not self.vector_store:
            return []
        return self.vector_store.search(case_id, query)
