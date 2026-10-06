"""Admin university management routes (platform-admin only)."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.universities.schemas import UniversityListResponse
from app.admin.universities.services import (
    admin_create_university,
    admin_delete_university,
    admin_get_university,
    admin_list_universities,
    admin_update_university,
)
from app.database import get_db
from app.auth.models import User
from app.university.schemas import UniversityCreate, UniversityResponse, UniversityUpdate
from app.utils.dependencies import require_admin

router = APIRouter(prefix="/api/v1/admin/universities", tags=["Admin: Universities"])


@router.post("/", response_model=UniversityResponse, status_code=status.HTTP_201_CREATED)
async def create_university(
    data: UniversityCreate,
    current_admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await admin_create_university(data, current_admin.id, session)
    return UniversityResponse.model_validate(university)


@router.get("/", response_model=UniversityListResponse)
async def list_universities(
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> UniversityListResponse:
    items, total = await admin_list_universities(session, search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size
    return UniversityListResponse(
        items=[UniversityResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@router.get("/{university_id}", response_model=UniversityResponse)
async def get_university(
    university_id: str,
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await admin_get_university(university_id, session)
    if not university:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University not found")
    return UniversityResponse.model_validate(university)


@router.put("/{university_id}", response_model=UniversityResponse)
async def update_university(
    university_id: str,
    data: UniversityUpdate,
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await admin_update_university(university_id, data, session)
    if not university:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University not found")
    return UniversityResponse.model_validate(university)


@router.delete("/{university_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_university(
    university_id: str,
    _admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> None:
    deleted = await admin_delete_university(university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University not found")
