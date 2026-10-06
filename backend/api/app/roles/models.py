"""Role and permission models."""
import uuid
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel


class Permission(str, Enum):
    VIEW_DASHBOARD = "view_dashboard"
    MANAGE_COURSES = "manage_courses"
    MANAGE_ADMISSIONS = "manage_admissions"
    CONFIGURE_VOICE_AGENT = "configure_voice_agent"
    MANAGE_USERS = "manage_users"
    MANAGE_KNOWLEDGE = "manage_knowledge"


# Permissions operators can NEVER hold, regardless of DB state. Hard lock.
OPERATOR_LOCKED_PERMISSIONS: frozenset[Permission] = frozenset(
    p for p in Permission if p != Permission.VIEW_DASHBOARD
)


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"
    __table_args__ = (
        sa.UniqueConstraint("university_id", "role", "permission", name="uq_role_permissions"),
    )

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=sa.Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=sa.Column(
            PG_UUID(as_uuid=True),
            sa.ForeignKey("universities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    role: str = Field(max_length=20)
    permission: str = Field(max_length=50)
    enabled: bool = Field(default=True)
