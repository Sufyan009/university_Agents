"""Admission models."""
from datetime import datetime
from typing import List, Optional
import uuid

from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class AdmissionInfo(SQLModel, table=True):
    """Admission info model — 1:1 from university."""
    __tablename__ = "admission_info"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), unique=True)
    )
    criteria: Optional[str] = None
    eligibility: Optional[str] = None
    deadlines: Optional[List] = Field(default=None, sa_column=Column(JSON))
    application_process: Optional[str] = None
    required_documents: Optional[List] = Field(default=None, sa_column=Column(JSON))
    scholarship_info: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
