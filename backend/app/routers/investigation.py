from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.deps import get_current_user
from app.models.domain import User
from app.services.access import ensure_case_access

router = APIRouter(prefix="/cases/{case_id}/investigation", tags=["investigation"])


@router.post("/query")
def query_case(
    case_id: str,
    payload: dict,
    user: User = Depends(get_current_user),
):
    repository = __import__("app.container", fromlist=["get_container"]).get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    if settings.enable_llm:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LLM mode is optional and disabled for this MVP build.",
        )

    observations = repository.list_case_observations(case_id)
    result = __import__("app.container", fromlist=["get_container"]).get_container().query.answer(payload.get("question", ""), observations)
    __import__("app.container", fromlist=["get_container"]).get_container().audit.log(
        user.id,
        "investigation.query",
        case_id=case_id,
        details={"question": payload.get("question", "")},
    )
    return {"result": result.model_dump()}


@router.get("/report")
def get_report(case_id: str, user: User = Depends(get_current_user)):
    repository = __import__("app.container", fromlist=["get_container"]).get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    observations = repository.list_case_observations(case_id)
    report = __import__("app.container", fromlist=["get_container"]).get_container().reporting.build_report(case_id, observations)
    return {"report": report.model_dump()}
