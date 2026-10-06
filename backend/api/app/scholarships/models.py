"""Scholarship models."""
from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class Scholarship(SQLModel, table=True):
    """Scholarship model — 1:N from university, optional link to course."""
    __tablename__ = "scholarships"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), index=True)
    )
    course_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True)
    )
    name: str
    amount: Optional[str] = None
    eligibility: Optional[str] = None
    deadline: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
