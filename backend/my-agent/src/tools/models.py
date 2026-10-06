"""Lightweight SQLModel mirrors the agent reads at runtime (read-only).

extend_existing avoids clashes if the same table is mapped twice in-process.
"""
import uuid

from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class University(SQLModel, table=True):
    __tablename__ = "universities"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    name: str
    description: str | None = None
    location: dict | None = Field(default=None, sa_column=Column(JSON))
    contact_info: dict | None = Field(default=None, sa_column=Column(JSON))
    admission_office: dict | None = Field(default=None, sa_column=Column(JSON))
    phone: str | None = None
    website: str | None = None


class AgentConfig(SQLModel, table=True):
    __tablename__ = "agent_configs"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), unique=True)
    )
    agent_name: str = Field(default="Assistant")
    personality: str = Field(default="friendly")
    greeting_message: str = Field(default="Hello! Thanks for calling.")
    special_instructions: str | None = None
    voice_config: dict = Field(default={}, sa_column=Column(JSON))
    context_text: str | None = None
    enable_admissions: bool = Field(default=True)
    enable_courses: bool = Field(default=True)
    enable_scholarships: bool = Field(default=True)
    enable_faq: bool = Field(default=True)


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"))
    )
    name: str
    degree_type: str | None = None
    description: str | None = None
    duration: str | None = None
    fee_structure: dict | None = Field(default=None, sa_column=Column(JSON))
    admission_requirements: str | None = None


class Subject(SQLModel, table=True):
    __tablename__ = "subjects"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    course_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("courses.id"))
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"))
    )
    name: str
    description: str | None = None
    credits: int | None = None
    prerequisites: str | None = None
    additional_info: str | None = None


class AdmissionInfo(SQLModel, table=True):
    __tablename__ = "admission_info"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), unique=True)
    )
    criteria: str | None = None
    eligibility: str | None = None
    deadlines: list | None = Field(default=None, sa_column=Column(JSON))
    application_process: str | None = None
    required_documents: list | None = Field(default=None, sa_column=Column(JSON))
    scholarship_info: str | None = None


class Scholarship(SQLModel, table=True):
    __tablename__ = "scholarships"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"))
    )
    course_id: uuid.UUID | None = Field(
        default=None, sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True)
    )
    name: str
    amount: str | None = None
    eligibility: str | None = None
    deadline: str | None = None
    is_active: bool = Field(default=True)


class FAQ(SQLModel, table=True):
    __tablename__ = "faqs"
    __table_args__ = {"extend_existing": True}

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"))
    )
    question: str
    answer: str
    category: str | None = None
    is_active: bool = Field(default=True)
