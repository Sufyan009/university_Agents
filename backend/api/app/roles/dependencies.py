"""Permission-checking FastAPI dependencies."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import Role, User
from app.database import get_db
from app.roles.models import Permission
from app.roles.services import check_permission
from app.utils.dependencies import get_current_user


def require_permission(permission: Permission):
    """Dependency factory — raises 403 if the current user lacks the given permission."""

    async def _guard(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> User:
        role_str = current_user.role.value if isinstance(current_user.role, Role) else str(current_user.role)
        if role_str == Role.ADMIN.value:
            return current_user
        if not current_user.university_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No university associated with this account",
            )
        allowed = await check_permission(current_user.university_id, role_str, permission, session)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )
        return current_user

    return _guard


async def require_write_access(current_user: User = Depends(get_current_user)) -> User:
    """Blocks operators from any state-mutating endpoint."""
    role_str = current_user.role.value if isinstance(current_user.role, Role) else str(current_user.role)
    if role_str == Role.OPERATOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operators are not permitted to save changes",
        )
    return current_user
