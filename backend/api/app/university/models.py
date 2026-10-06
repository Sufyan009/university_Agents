"""University and agent configuration models."""
from datetime import datetime
from typing import Dict, Optional
import uuid

from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class University(SQLModel, table=True):
    """University model — the tenant root. `phone` is the unique tenant key."""
    __tablename__ = "universities"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    admin_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True)
    )
    name: str = Field(unique=True)
    description: Optional[str] = None
    location: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    contact_info: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    admission_office: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    phone: Optional[str] = Field(default=None, unique=True)
    website: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentConfig(SQLModel, table=True):
    """Voice agent configuration — 1:1 with university."""
    __tablename__ = "agent_configs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), unique=True)
    )
    agent_name: str = Field(default="Assistant")
    personality: str = Field(default="friendly")
    greeting_message: str = Field(default="Hello! Thanks for calling. How can I help with admissions, courses, or fees?")
    special_instructions: Optional[str] = None
    voice_config: Dict = Field(default={}, sa_column=Column(JSON))
    context_text: Optional[str] = None
    enable_admissions: bool = Field(default=True)
    enable_courses: bool = Field(default=True)
    enable_scholarships: bool = Field(default=True)
    enable_faq: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
