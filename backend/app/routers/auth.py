from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token, get_current_user, verify_password
from app.db.store import get_store
from app.schemas.auth import LoginRequest, LoginResponse, UserOut

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    store = get_store()
    user = store.get_user_by_username(payload.username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Username atau kata sandi salah.",
            },
        )

    settings = get_settings()
    token = create_access_token(user)
    return LoginResponse(
        access_token=token,
        expires_in_minutes=settings.jwt_expire_minutes,
        user=UserOut(
            id=user["id"],
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"],
        ),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: dict[str, Any] = Depends(get_current_user)) -> UserOut:
    return UserOut(**current_user)
