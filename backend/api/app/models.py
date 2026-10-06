"""Central model registry — import all models to ensure SQLModel registration."""
from sqlmodel import SQLModel

from app.auth.models import User  # noqa: F401
from app.roles.models import RolePermission  # noqa: F401
from app.university.models import University, AgentConfig  # noqa: F401
from app.courses.models import Course  # noqa: F401
from app.subjects.models import Subject  # noqa: F401
from app.admissions.models import AdmissionInfo  # noqa: F401
from app.scholarships.models import Scholarship  # noqa: F401
from app.faqs.models import FAQ  # noqa: F401
from app.calls.models import CallSession, CallMessage  # noqa: F401

# Export Base for Alembic
Base = SQLModel

__all__ = [
    "User", "RolePermission", "University", "AgentConfig", "Course", "Subject",
    "AdmissionInfo", "Scholarship", "FAQ", "CallSession", "CallMessage", "Base",
]
