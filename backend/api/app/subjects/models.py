"""Subject models."""
from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class Subject(SQLModel, table=True):
    """Subject model — 1:N from course."""
    __tablename__ = "subjects"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    course_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("courses.id"), index=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), index=True)
    )
    name: str
    description: Optional[str] = None
    credits: Optional[int] = None
    prerequisites: Optional[str] = None
    additional_info: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
