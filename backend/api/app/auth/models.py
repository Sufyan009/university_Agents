"""Auth models."""
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class Role(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    OWNER = "owner"
    MANAGER = "manager"
    OPERATOR = "operator"


class User(SQLModel, table=True):
    """User model — self-contained auth for the university platform."""
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    email: str = Field(unique=True, index=True)
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Role = Field(default=Role.OPERATOR, sa_column=Column(sa.String(20)))
    is_active: bool = Field(default=True)
    password_hash: str
    university_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
