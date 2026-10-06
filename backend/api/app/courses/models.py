"""Course models."""
from datetime import datetime
from typing import Dict, Optional
import uuid

from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class Course(SQLModel, table=True):
    """Course model — 1:N from university."""
    __tablename__ = "courses"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), index=True)
    )
    name: str
    degree_type: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None
    duration: Optional[str] = None
    fee_structure: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    admission_requirements: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
