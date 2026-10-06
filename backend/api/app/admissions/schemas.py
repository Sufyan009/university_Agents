"""Admission schemas."""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class AdmissionCreate(BaseModel):
    criteria: Optional[str] = Field(default=None, max_length=4000)
    eligibility: Optional[str] = Field(default=None, max_length=4000)
    deadlines: Optional[List[dict]] = None
    application_process: Optional[str] = Field(default=None, max_length=4000)
    required_documents: Optional[List[str]] = None
    scholarship_info: Optional[str] = Field(default=None, max_length=4000)


class AdmissionUpdate(BaseModel):
    criteria: Optional[str] = Field(default=None, max_length=4000)
    eligibility: Optional[str] = Field(default=None, max_length=4000)
    deadlines: Optional[List[dict]] = None
    application_process: Optional[str] = Field(default=None, max_length=4000)
    required_documents: Optional[List[str]] = None
    scholarship_info: Optional[str] = Field(default=None, max_length=4000)


class AdmissionResponse(BaseModel):
    id: uuid.UUID
    university_id: uuid.UUID
    criteria: Optional[str]
    eligibility: Optional[str]
    deadlines: Optional[List[dict]]
    application_process: Optional[str]
    required_documents: Optional[List[str]]
    scholarship_info: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
