"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    AdminCreate,
    LoginRequest,
    PasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate
)
from app.auth.models import User
from app.auth.services import (
    authenticate_user,
    change_password,
    create_access_token,
    create_admin,
    create_refresh_token,
    get_user_by_id,
    register_user,
    update_user
)
from app.roles.services import get_effective_permissions
from app.config import get_settings
from app.database import get_db
from app.utils.dependencies import get_current_user, validate_refresh_token
from app.utils.rate_limiter import check_rate_limit

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Register new university user")
async def register(
    request: Request,
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    await check_rate_limit(request, max_requests=3, window_seconds=3600, key_prefix="register")
    user = await register_user(user_data, session)
    return UserResponse(**user.model_dump())


@router.post("/create-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Create admin user")
async def create_admin_user(
    request: Request,
    admin_data: AdminCreate,
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    await check_rate_limit(request, max_requests=3, window_seconds=3600, key_prefix="create_admin")
    user = await create_admin(admin_data, session)
    return UserResponse(**user.model_dump())


@router.post("/login", response_model=TokenResponse, summary="Login")
async def login(
    request: Request,
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    await check_rate_limit(request, max_requests=5, window_seconds=60, key_prefix="login")
    user = await authenticate_user(credentials.email, credentials.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    settings = get_settings()
    permissions = await get_effective_permissions(role=str(user.role), university_id=None, session=session)
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        role=str(user.role),
        permissions=permissions,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(
    request: Request,
    user_id: str = Depends(validate_refresh_token),
    session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    await check_rate_limit(request, max_requests=10, window_seconds=60, key_prefix="refresh")
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    settings = get_settings()
    permissions = await get_effective_permissions(role=str(user.role), university_id=None, session=session)
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        role=str(user.role),
        permissions=permissions,
    )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**current_user.model_dump())


@router.put("/me", response_model=UserResponse, summary="Update current user")
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    updated_user = await update_user(str(current_user.id), update_data, session)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(**updated_user.model_dump())


@router.post("/change-password", status_code=status.HTTP_200_OK, summary="Change password")
async def update_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
) -> dict:
    await change_password(str(current_user.id), password_data.current_password, password_data.new_password, session)
    return {"message": "Password changed successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Logout")
async def logout() -> dict:
    return {"message": "Logout successful"}
