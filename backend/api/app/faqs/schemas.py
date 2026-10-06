"""FAQ schemas."""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class FAQCreate(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1, max_length=4000)
    category: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = True


class FAQUpdate(BaseModel):
    question: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    answer: Optional[str] = Field(default=None, min_length=1, max_length=4000)
    category: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None


class FAQResponse(BaseModel):
    id: uuid.UUID
    university_id: uuid.UUID
    question: str
    answer: str
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FAQListResponse(BaseModel):
    items: List[FAQResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
