"""Admin university management schemas."""
from typing import List

from pydantic import BaseModel

from app.university.schemas import UniversityResponse


class UniversityListResponse(BaseModel):
    items: List[UniversityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
