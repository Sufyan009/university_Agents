"""FAQ models."""
from datetime import datetime
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import sqlalchemy as sa


class FAQ(SQLModel, table=True):
    """FAQ model — 1:N from university."""
    __tablename__ = "faqs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True)
    )
    university_id: uuid.UUID = Field(
        sa_column=Column(PG_UUID(as_uuid=True), sa.ForeignKey("universities.id"), index=True)
    )
    question: str
    answer: str
    category: Optional[str] = Field(default=None, index=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
