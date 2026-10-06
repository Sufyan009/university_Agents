"""Scholarship schemas."""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class ScholarshipCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    course_id: Optional[uuid.UUID] = None
    amount: Optional[str] = Field(default=None, max_length=100)
    eligibility: Optional[str] = Field(default=None, max_length=4000)
    deadline: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = True


class ScholarshipUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    course_id: Optional[uuid.UUID] = None
    amount: Optional[str] = Field(default=None, max_length=100)
    eligibility: Optional[str] = Field(default=None, max_length=4000)
    deadline: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None


class ScholarshipResponse(BaseModel):
    id: uuid.UUID
    university_id: uuid.UUID
    course_id: Optional[uuid.UUID]
    name: str
    amount: Optional[str]
    eligibility: Optional[str]
    deadline: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScholarshipListResponse(BaseModel):
    items: List[ScholarshipResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
