from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.container import get_container
from app.models.domain import User
from app.services.access import ensure_case_access

router = APIRouter(prefix="/cases/{case_id}/graph", tags=["graph"])


@router.get("/export")
def export_graph(case_id: str, user: User = Depends(get_current_user)) -> dict:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    observations = repository.list_case_observations(case_id)
    return get_container().graph.export_case(case_id, observations)
