from __future__ import annotations

from typing import Any


class LangGraphInvestigationOrchestrator:
    """Safe orchestration shell for workflow execution.

    This is a deterministic orchestration layer for the MVP. It does not require an external LangGraph installation.
    """

    def run(self, stage: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "stage": stage,
            "status": "completed",
            "payload": payload,
            "summary": "The prototype used deterministic workflow orchestration with human review. No external model executed the final conclusion.",
        }
