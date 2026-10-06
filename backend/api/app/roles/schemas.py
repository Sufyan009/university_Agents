"""Roles and permissions schemas."""
import uuid
from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, EmailStr

from app.auth.models import Role


class UniversityUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime


class UserListResponse(BaseModel):
    items: List[UniversityUserResponse]
    total: int


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: Literal["owner", "manager", "operator"]


class UpdateUserRoleRequest(BaseModel):
    role: Literal["owner", "manager", "operator"]


class PermissionEntry(BaseModel):
    permission: str
    owner: bool
    manager: bool
    operator: bool


class PermissionsMatrixResponse(BaseModel):
    permissions: List[PermissionEntry]


class PermissionUpdate(BaseModel):
    permission: str
    role: Literal["owner", "manager", "operator"]
    enabled: bool


class UpdatePermissionsRequest(BaseModel):
    updates: List[PermissionUpdate]
