"""Authentication API schemas."""
from datetime import datetime
import re
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.auth.models import Role


PLACEHOLDER_VALUES = {
    "string", "stringst", "test", "demo", "example", "default",
    "password", "qwerty123", "user@example.com",
}

BLOCKED_EMAIL_DOMAINS = {"example.com", "test.com", "sample.com"}
BLOCKED_EMAIL_LOCALS = {"user", "test", "demo", "admin", "string"}


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    university_name: str = Field(..., min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: Role = Field(default=Role.OPERATOR)
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email_not_placeholder(cls, value: EmailStr) -> EmailStr:
        email = str(value).strip().lower()
        if email in PLACEHOLDER_VALUES:
            raise ValueError("Please provide a real email address")
        local_part, domain = email.rsplit("@", 1)
        if domain in BLOCKED_EMAIL_DOMAINS:
            raise ValueError("Please provide a real email address")
        if local_part in BLOCKED_EMAIL_LOCALS:
            raise ValueError("Please provide a real email address")
        return value

    @field_validator("university_name")
    @classmethod
    def validate_university_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("University name is required")
        if name.lower() in PLACEHOLDER_VALUES:
            raise ValueError("University name cannot be a placeholder value")
        if len(re.sub(r"[^A-Za-z0-9]", "", name)) < 2:
            raise ValueError("University name must be meaningful")
        return value

    @field_validator("role", mode="before")
    @classmethod
    def normalise_role(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        phone = value.strip()
        if phone.lower() in PLACEHOLDER_VALUES:
            raise ValueError("Phone cannot be a placeholder value")
        if not re.fullmatch(r"^\+?[0-9\s\-()]{7,20}$", phone):
            raise ValueError("Invalid phone format")
        if len(re.sub(r"\D", "", phone)) < 7:
            raise ValueError("Phone must contain at least 7 digits")
        return phone


class UserCreate(UserBase):
    """User creation schema."""
    role: Role = Field(..., description="User role: admin, owner, manager, or operator")
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        password = value.strip()
        lowered = password.lower()
        if lowered in PLACEHOLDER_VALUES or "string" in lowered:
            raise ValueError("Password cannot be a placeholder value")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        return password


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        name = value.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        if name.lower() in PLACEHOLDER_VALUES:
            raise ValueError("Name cannot be a placeholder value")
        return name

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        phone = value.strip()
        if phone.lower() in PLACEHOLDER_VALUES:
            raise ValueError("Phone cannot be a placeholder value")
        if not re.fullmatch(r"^\+?[0-9\s\-()]{7,20}$", phone):
            raise ValueError("Invalid phone format")
        if len(re.sub(r"\D", "", phone)) < 7:
            raise ValueError("Phone must contain at least 7 digits")
        return phone


class UserResponse(BaseModel):
    """User response schema (excludes sensitive data)."""
    id: uuid.UUID
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Role
    is_active: bool
    university_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    permissions: list[str] = Field(default_factory=list)


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime
    type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AdminCreate(BaseModel):
    """Admin creation schema — email and password only."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email_not_placeholder(cls, value: EmailStr) -> EmailStr:
        email = str(value).strip().lower()
        if email in PLACEHOLDER_VALUES:
            raise ValueError("Please provide a real email address")
        local_part, domain = email.rsplit("@", 1)
        if domain in BLOCKED_EMAIL_DOMAINS:
            raise ValueError("Please provide a real email address")
        if local_part in BLOCKED_EMAIL_LOCALS:
            raise ValueError("Please provide a real email address")
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        password = value.strip()
        lowered = password.lower()
        if lowered in PLACEHOLDER_VALUES or "string" in lowered:
            raise ValueError("Password cannot be a placeholder value")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        return password


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        return value
