from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.deps import get_current_user
from app.container import get_container
from app.models.domain import User
from app.models.schemas import InvestigationQueryRequest, InvestigationQueryResponse, ReportResponse
from app.services.access import ensure_case_access

router = APIRouter(prefix="/cases/{case_id}/investigation", tags=["investigation"])


@router.post("/query", response_model=InvestigationQueryResponse)
def query_case(
    case_id: str,
    payload: InvestigationQueryRequest,
    user: User = Depends(get_current_user),
) -> InvestigationQueryResponse:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    observations = repository.list_case_observations(case_id)
    if settings.enable_llm:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LLM mode is optional and disabled for this MVP build",
        )

    result = get_container().query.answer(payload.question, observations)
    get_container().audit.log(user.id, "investigation.query", case_id=case_id, details={"question": payload.question})
    return InvestigationQueryResponse(result=result)


@router.get("/report", response_model=ReportResponse)
def get_report(case_id: str, user: User = Depends(get_current_user)) -> ReportResponse:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    observations = repository.list_case_observations(case_id)
    report = get_container().reporting.build_report(case_id, observations)
    get_container().audit.log(user.id, "investigation.report", case_id=case_id)
    return ReportResponse(report=report)
