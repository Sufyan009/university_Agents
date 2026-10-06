"""Subject schemas."""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    course_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=4000)
    credits: Optional[int] = None
    prerequisites: Optional[str] = Field(default=None, max_length=4000)
    additional_info: Optional[str] = Field(default=None, max_length=4000)


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=4000)
    credits: Optional[int] = None
    prerequisites: Optional[str] = Field(default=None, max_length=4000)
    additional_info: Optional[str] = Field(default=None, max_length=4000)


class SubjectResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    university_id: uuid.UUID
    name: str
    description: Optional[str]
    credits: Optional[int]
    prerequisites: Optional[str]
    additional_info: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SubjectListResponse(BaseModel):
    items: List[SubjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
