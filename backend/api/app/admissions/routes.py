"""Admission routes — tenant-scoped 1:1 record."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.admissions.schemas import AdmissionCreate, AdmissionResponse, AdmissionUpdate
from app.admissions.services import (
    create_admission_info,
    delete_admission_info,
    get_admission_info_by_university,
    update_admission_info,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/admissions", tags=["Admissions"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found.")
    return str(current_user.university_id)


@router.get("/", response_model=AdmissionResponse)
async def get_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AdmissionResponse:
    university_id = _require_university_id(current_user)
    info = await get_admission_info_by_university(university_id, session)
    if not info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission info not found")
    return AdmissionResponse.model_validate(info)


@router.post("/", response_model=AdmissionResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: AdmissionCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> AdmissionResponse:
    university_id = _require_university_id(current_user)
    info = await create_admission_info(university_id, data, session)
    return AdmissionResponse.model_validate(info)


@router.put("/", response_model=AdmissionResponse)
async def update(
    data: AdmissionUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> AdmissionResponse:
    university_id = _require_university_id(current_user)
    info = await update_admission_info(university_id, data, session)
    return AdmissionResponse.model_validate(info)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_ADMISSIONS)),
    session: AsyncSession = Depends(get_db),
) -> None:
    university_id = _require_university_id(current_user)
    deleted = await delete_admission_info(university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admission info not found")
