"""Call tracking models."""
from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class CallSession(SQLModel, table=True):
    __tablename__ = "call_sessions"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False, index=True)
    )
    livekit_room_id: str = Field(index=True)
    agent_type: str = Field(default="main")
    status: str = Field(default="active")  # active, ended, failed
    caller_identity: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CallMessage(SQLModel, table=True):
    __tablename__ = "call_messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    call_session_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=False, index=True)
    )
    role: str  # user, agent
    content: str
    sequence: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
