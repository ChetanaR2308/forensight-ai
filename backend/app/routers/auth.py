from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token, verify_password
from app.container import get_container
from app.models.schemas import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def token(payload: TokenRequest) -> TokenResponse:
    container = get_container()
    user = container.repository.get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.username)
    return TokenResponse(access_token=access_token, role=user.role)
