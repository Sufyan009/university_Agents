"""Subject routes — tenant-scoped CRUD."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.subjects.schemas import SubjectCreate, SubjectListResponse, SubjectResponse, SubjectUpdate
from app.subjects.services import (
    create_subject,
    delete_subject,
    get_subject_by_id,
    list_subjects,
    update_subject,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/subjects", tags=["Subjects"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found.")
    return str(current_user.university_id)


@router.get("/", response_model=SubjectListResponse)
async def list_all(
    course_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SubjectListResponse:
    university_id = _require_university_id(current_user)
    items, total = await list_subjects(university_id, session, course_id=course_id, search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size
    return SubjectListResponse(
        items=[SubjectResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: SubjectCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    university_id = _require_university_id(current_user)
    subject = await create_subject(university_id, data, session)
    return SubjectResponse.model_validate(subject)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_one(
    subject_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    university_id = _require_university_id(current_user)
    subject = await get_subject_by_id(subject_id, university_id, session)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return SubjectResponse.model_validate(subject)


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update(
    subject_id: str,
    data: SubjectUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> SubjectResponse:
    university_id = _require_university_id(current_user)
    subject = await update_subject(subject_id, university_id, data, session)
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return SubjectResponse.model_validate(subject)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    subject_id: str,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> None:
    university_id = _require_university_id(current_user)
    deleted = await delete_subject(subject_id, university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
