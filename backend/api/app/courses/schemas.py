"""Course schemas."""
from datetime import datetime
from typing import Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    degree_type: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=4000)
    duration: Optional[str] = Field(default=None, max_length=100)
    fee_structure: Optional[Dict] = None
    admission_requirements: Optional[str] = Field(default=None, max_length=4000)


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    degree_type: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=4000)
    duration: Optional[str] = Field(default=None, max_length=100)
    fee_structure: Optional[Dict] = None
    admission_requirements: Optional[str] = Field(default=None, max_length=4000)


class CourseResponse(BaseModel):
    id: uuid.UUID
    university_id: uuid.UUID
    name: str
    degree_type: Optional[str]
    description: Optional[str]
    duration: Optional[str]
    fee_structure: Optional[Dict]
    admission_requirements: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourseListResponse(BaseModel):
    items: List[CourseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
