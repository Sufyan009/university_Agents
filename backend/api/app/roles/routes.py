"""Roles — user management and permissions endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import get_db
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.roles.schemas import (
    InviteUserRequest,
    PermissionsMatrixResponse,
    UniversityUserResponse,
    UpdatePermissionsRequest,
    UpdateUserRoleRequest,
    UserListResponse,
)
from app.roles import services
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


def _assert_university(user: User) -> uuid.UUID:
    if not user.university_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No university associated with this account",
        )
    return user.university_id


def _role_value(user: User) -> str:
    return user.role.value if hasattr(user.role, "value") else str(user.role)


@router.get("/users/", response_model=UserListResponse)
async def list_users(
    current_user: User = Depends(require_permission(Permission.VIEW_DASHBOARD)),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    users, total = await services.list_users(university_id, session)
    return UserListResponse(items=[services._to_user_response(u) for u in users], total=total)


@router.post("/users/invite", response_model=UniversityUserResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    body: InviteUserRequest,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    user = await services.invite_user(university_id, body.email, body.role, _role_value(current_user), session)
    return services._to_user_response(user)


@router.patch("/users/{user_id}", response_model=UniversityUserResponse)
async def update_user_role(
    user_id: uuid.UUID,
    body: UpdateUserRoleRequest,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    user = await services.update_user_role(user_id, university_id, body.role, _role_value(current_user), session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found in this university")
    return services._to_user_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: uuid.UUID,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    removed = await services.remove_user(user_id, university_id, current_user.id, session)
    if not removed:
        raise HTTPException(status_code=404, detail="User not found in this university")


@router.get("/permissions/", response_model=PermissionsMatrixResponse)
async def get_permissions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    entries = await services.get_permissions_matrix(university_id, session)
    return PermissionsMatrixResponse(permissions=entries)


@router.put("/permissions/", response_model=PermissionsMatrixResponse)
async def update_permissions(
    body: UpdatePermissionsRequest,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    session: AsyncSession = Depends(get_db),
):
    university_id = _assert_university(current_user)
    entries = await services.update_permissions(university_id, body.updates, session)
    return PermissionsMatrixResponse(permissions=entries)
