"""Scholarship routes — tenant-scoped CRUD."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.scholarships.schemas import (
    ScholarshipCreate,
    ScholarshipListResponse,
    ScholarshipResponse,
    ScholarshipUpdate,
)
from app.scholarships.services import (
    create_scholarship,
    delete_scholarship,
    get_scholarship_by_id,
    list_scholarships,
    update_scholarship,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/scholarships", tags=["Scholarships"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found.")
    return str(current_user.university_id)


@router.get("/", response_model=ScholarshipListResponse)
async def list_all(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ScholarshipListResponse:
    university_id = _require_university_id(current_user)
    items, total = await list_scholarships(university_id, session, is_active=is_active, search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size
    return ScholarshipListResponse(
        items=[ScholarshipResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@router.post("/", response_model=ScholarshipResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: ScholarshipCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> ScholarshipResponse:
    university_id = _require_university_id(current_user)
    scholarship = await create_scholarship(university_id, data, session)
    return ScholarshipResponse.model_validate(scholarship)


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_one(
    scholarship_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ScholarshipResponse:
    university_id = _require_university_id(current_user)
    scholarship = await get_scholarship_by_id(scholarship_id, university_id, session)
    if not scholarship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found")
    return ScholarshipResponse.model_validate(scholarship)


@router.put("/{scholarship_id}", response_model=ScholarshipResponse)
async def update(
    scholarship_id: str,
    data: ScholarshipUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> ScholarshipResponse:
    university_id = _require_university_id(current_user)
    scholarship = await update_scholarship(scholarship_id, university_id, data, session)
    if not scholarship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found")
    return ScholarshipResponse.model_validate(scholarship)


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    scholarship_id: str,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> None:
    university_id = _require_university_id(current_user)
    deleted = await delete_scholarship(scholarship_id, university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found")
