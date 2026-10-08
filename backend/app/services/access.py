from fastapi import HTTPException, status

from app.models.domain import Case, Role, User


def ensure_case_access(user: User, case: Case) -> None:
    if user.role == Role.admin:
        return
    if case.owner_id == user.id or user.id in case.collaborators:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Case access denied")
