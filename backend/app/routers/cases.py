from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user, require_roles
from app.container import get_container
from app.models.domain import Case, Role, User
from app.models.schemas import CaseCreate, CaseUpdate
from app.services.access import ensure_case_access

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
def list_cases(user: User = Depends(get_current_user)) -> list[Case]:
    repository = get_container().repository
    cases = repository.list_cases()
    if user.role == Role.admin:
        return cases
    return [case for case in cases if case.owner_id == user.id or user.id in case.collaborators]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, user: User = Depends(require_roles(Role.investigator, Role.admin))) -> Case:
    repository = get_container().repository
    case = Case(title=payload.title, description=payload.description, owner_id=user.id)
    repository.create_case(case)
    get_container().audit.log(user.id, "case.create", case_id=case.id)
    return case


@router.get("/{case_id}")
def get_case(case_id: str, user: User = Depends(get_current_user)) -> Case:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)
    return case


@router.patch("/{case_id}")
def update_case(case_id: str, payload: CaseUpdate, user: User = Depends(get_current_user)) -> Case:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)

    data = case.model_dump()
    if payload.title is not None:
        data["title"] = payload.title
    if payload.description is not None:
        data["description"] = payload.description
    data["updated_at"] = datetime.now(timezone.utc)
    updated = Case(**data)
    repository.update_case(updated)
    get_container().audit.log(user.id, "case.update", case_id=case_id)
    return updated


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: str, user: User = Depends(require_roles(Role.investigator, Role.admin))) -> None:
    repository = get_container().repository
    case = repository.get_case(case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    ensure_case_access(user, case)
    repository.delete_case(case_id)
    get_container().audit.log(user.id, "case.delete", case_id=case_id)
