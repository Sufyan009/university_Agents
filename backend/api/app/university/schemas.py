"""University and agent config API schemas."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid

from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    address: Optional[str] = Field(default=None, max_length=300)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postcode: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="UK", max_length=50)


class ContactInfo(BaseModel):
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[str] = Field(default=None, max_length=120)
    fax: Optional[str] = Field(default=None, max_length=30)


class AdmissionOffice(BaseModel):
    name: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, max_length=120)
    phone: Optional[str] = Field(default=None, max_length=30)
    hours: Optional[str] = Field(default=None, max_length=200)


class UniversityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, max_length=4000)
    location: Optional[Location] = None
    contact_info: Optional[ContactInfo] = None
    admission_office: Optional[AdmissionOffice] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=200)


class UniversityCreate(UniversityBase):
    pass


class UniversityUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, max_length=4000)
    location: Optional[Location] = None
    contact_info: Optional[ContactInfo] = None
    admission_office: Optional[AdmissionOffice] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    website: Optional[str] = Field(default=None, max_length=200)


class UniversityResponse(UniversityBase):
    id: uuid.UUID
    admin_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VoiceConfig(BaseModel):
    voice_id: str = Field(default="gemma", max_length=50)
    speed: float = Field(default=1.1, ge=0.5, le=2.0)
    language: str = Field(default="en", max_length=10)

    @field_validator("voice_id")
    @classmethod
    def validate_voice_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("voice_id cannot be empty")
        return v.strip()


class AgentPersonality(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    ENTHUSIASTIC = "enthusiastic"


class AgentConfigBase(BaseModel):
    agent_name: str = Field(default="Assistant", min_length=1, max_length=50)
    personality: str = Field(default="friendly", max_length=20)
    greeting_message: str = Field(
        default="Hello! Thanks for calling. How can I help with admissions, courses, or fees?",
        max_length=500
    )
    special_instructions: Optional[str] = Field(default=None, max_length=2000)
    voice_config: VoiceConfig = Field(default_factory=VoiceConfig)
    enable_admissions: bool = True
    enable_courses: bool = True
    enable_scholarships: bool = True
    enable_faq: bool = True


class AgentConfigCreate(AgentConfigBase):
    university_id: Optional[uuid.UUID] = Field(default=None)


class AgentConfigUpdate(BaseModel):
    agent_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    personality: Optional[str] = Field(default=None, max_length=20)
    greeting_message: Optional[str] = Field(default=None, max_length=500)
    special_instructions: Optional[str] = Field(default=None, max_length=2000)
    voice_config: Optional[VoiceConfig] = None
    context_text: Optional[str] = None
    enable_admissions: Optional[bool] = None
    enable_courses: Optional[bool] = None
    enable_scholarships: Optional[bool] = None
    enable_faq: Optional[bool] = None

    @field_validator("personality")
    @classmethod
    def validate_personality(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid = {p.value for p in AgentPersonality}
            if v not in valid:
                raise ValueError(f"personality must be one of {valid}")
        return v


class AgentConfigResponse(AgentConfigBase):
    id: uuid.UUID
    university_id: uuid.UUID
    context_text: Optional[str] = None
    updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class GeneratedPromptResponse(BaseModel):
    prompt: str
    university_name: Optional[str] = None
    courses_count: int = 0
    generated_at: datetime
