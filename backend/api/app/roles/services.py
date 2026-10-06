"""Roles and user management services."""
import secrets
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.models import Role, User
from app.auth.services import hash_password
from app.roles.models import OPERATOR_LOCKED_PERMISSIONS, Permission
from app.roles.schemas import PermissionEntry, UniversityUserResponse

UNIVERSITY_ROLES = {"owner", "manager", "operator"}

# Default permission matrix — used as fallback when no DB row exists
DEFAULT_PERMISSIONS: dict[str, dict] = {
    "owner": {
        Permission.VIEW_DASHBOARD: True,
        Permission.MANAGE_COURSES: True,
        Permission.MANAGE_ADMISSIONS: True,
        Permission.CONFIGURE_VOICE_AGENT: True,
        Permission.MANAGE_USERS: True,
        Permission.MANAGE_KNOWLEDGE: True,
    },
    "manager": {
        Permission.VIEW_DASHBOARD: True,
        Permission.MANAGE_COURSES: True,
        Permission.MANAGE_ADMISSIONS: True,
        Permission.CONFIGURE_VOICE_AGENT: True,
        Permission.MANAGE_USERS: True,
        Permission.MANAGE_KNOWLEDGE: False,
    },
    "operator": {
        Permission.VIEW_DASHBOARD: True,
        Permission.MANAGE_COURSES: False,
        Permission.MANAGE_ADMISSIONS: False,
        Permission.CONFIGURE_VOICE_AGENT: False,
        Permission.MANAGE_USERS: False,
        Permission.MANAGE_KNOWLEDGE: False,
    },
}


def _default_permission_value(role: str, permission_key: str) -> bool:
    for permission, enabled in DEFAULT_PERMISSIONS.get(role, {}).items():
        if permission.value == permission_key:
            return enabled
    return False


def _to_user_response(user: User) -> UniversityUserResponse:
    full_name = user.name or user.email.split("@")[0].replace(".", " ").replace("_", " ").title()
    return UniversityUserResponse(
        id=user.id,
        email=user.email,
        full_name=full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


async def list_users(university_id: uuid.UUID, session: AsyncSession) -> Tuple[List[User], int]:
    result = await session.execute(
        select(User).where(
            User.university_id == university_id,
            User.role.in_(UNIVERSITY_ROLES),
        )
    )
    users = list(result.scalars().all())
    return users, len(users)


async def invite_user(
    university_id: uuid.UUID, email: str, role: str, inviter_role: str, session: AsyncSession
) -> User:
    if inviter_role == "manager" and role != "operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only invite operators")

    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")

    now = datetime.utcnow()
    user = User(
        email=email,
        password_hash=hash_password(secrets.token_urlsafe(32)),
        role=Role(role),
        university_id=university_id,
        is_active=False,
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def update_user_role(
    user_id: uuid.UUID, university_id: uuid.UUID, new_role: str, inviter_role: str, session: AsyncSession
) -> Optional[User]:
    if inviter_role == "manager" and new_role != "operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Managers can only assign the operator role")

    result = await session.execute(
        select(User).where(User.id == user_id, User.university_id == university_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    user.role = Role(new_role)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def remove_user(
    user_id: uuid.UUID, university_id: uuid.UUID, current_user_id: uuid.UUID, session: AsyncSession
) -> bool:
    result = await session.execute(
        select(User).where(User.id == user_id, User.university_id == university_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return False
    if user.id == current_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself")
    if user.role == Role.OWNER:
        owner_count_result = await session.execute(
            select(func.count(User.id)).where(
                User.university_id == university_id, User.role == Role.OWNER
            )
        )
        if (owner_count_result.scalar() or 0) <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the last owner")
    await session.delete(user)
    return True


async def check_permission(
    university_id: uuid.UUID, role: str, permission: Permission, session: AsyncSession
) -> bool:
    if role == "operator" and permission in OPERATOR_LOCKED_PERMISSIONS:
        return False

    result = await session.execute(
        text(
            """
            SELECT enabled FROM role_permissions
            WHERE university_id = :uid AND role = :role AND permission = :permission
            LIMIT 1
            """
        ),
        {"uid": str(university_id), "role": role, "permission": permission.value},
    )
    row = result.first()
    if row is not None:
        return bool(row[0])
    return _default_permission_value(role, permission.value)


async def get_permissions_matrix(university_id: uuid.UUID, session: AsyncSession) -> List[PermissionEntry]:
    db_rows: dict = {}
    try:
        result = await session.execute(
            text("SELECT role, permission, enabled FROM role_permissions WHERE university_id = :uid"),
            {"uid": str(university_id)},
        )
        db_rows = {(r[0], r[1]): r[2] for r in result.fetchall()}
    except Exception:
        db_rows = {}

    entries: List[PermissionEntry] = []
    for permission in Permission:
        def _get(role: str) -> bool:
            key = (role, permission.value)
            if key in db_rows:
                return bool(db_rows[key])
            return _default_permission_value(role, permission.value)

        entries.append(
            PermissionEntry(
                permission=permission.value,
                owner=_get("owner"),
                manager=_get("manager"),
                operator=_get("operator"),
            )
        )
    return entries


async def update_permissions(university_id: uuid.UUID, updates: list, session: AsyncSession) -> List[PermissionEntry]:
    for upd in updates:
        if upd.role == "operator" and upd.enabled:
            try:
                perm_enum = Permission(upd.permission)
            except ValueError:
                perm_enum = None
            if perm_enum is not None and perm_enum in OPERATOR_LOCKED_PERMISSIONS:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{upd.permission}' cannot be granted to operators",
                )

        result = await session.execute(
            text(
                """
                UPDATE role_permissions SET enabled = :enabled
                WHERE university_id = :uid AND role = :role AND permission = :permission
                """
            ),
            {"uid": str(university_id), "role": upd.role, "permission": upd.permission, "enabled": upd.enabled},
        )
        if result.rowcount == 0:
            await session.execute(
                text(
                    """
                    INSERT INTO role_permissions (id, university_id, role, permission, enabled)
                    VALUES (gen_random_uuid(), :uid, :role, :permission, :enabled)
                    """
                ),
                {"uid": str(university_id), "role": upd.role, "permission": upd.permission, "enabled": upd.enabled},
            )
    await session.flush()
    return await get_permissions_matrix(university_id, session)


async def get_effective_permissions(
    role: str, university_id: Optional[uuid.UUID], session: AsyncSession
) -> list[str]:
    """Return effective permission keys for a role (DB overrides, else code defaults)."""
    if role == "admin":
        return [perm.value for perm in Permission]

    if university_id is not None:
        try:
            result = await session.execute(
                text(
                    """
                    SELECT permission FROM role_permissions
                    WHERE university_id = :uid AND role = :role AND enabled = true
                    """
                ),
                {"uid": str(university_id), "role": role},
            )
            permissions = [row[0] for row in result.fetchall()]
            if permissions:
                return permissions
        except Exception:
            pass

    return [perm.value for perm, enabled in DEFAULT_PERMISSIONS.get(role, {}).items() if enabled]
