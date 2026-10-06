"""Course routes — tenant-scoped CRUD."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.courses.schemas import CourseCreate, CourseListResponse, CourseResponse, CourseUpdate
from app.courses.services import (
    create_course,
    delete_course,
    get_course_by_id,
    list_courses,
    update_course,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found.")
    return str(current_user.university_id)


@router.get("/", response_model=CourseListResponse)
async def list_all(
    degree_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CourseListResponse:
    university_id = _require_university_id(current_user)
    items, total = await list_courses(university_id, session, degree_type=degree_type, search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size
    return CourseListResponse(
        items=[CourseResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: CourseCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> CourseResponse:
    university_id = _require_university_id(current_user)
    course = await create_course(university_id, data, session)
    return CourseResponse.model_validate(course)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_one(
    course_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CourseResponse:
    university_id = _require_university_id(current_user)
    course = await get_course_by_id(course_id, university_id, session)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse.model_validate(course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update(
    course_id: str,
    data: CourseUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> CourseResponse:
    university_id = _require_university_id(current_user)
    course = await update_course(course_id, university_id, data, session)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    course_id: str,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_COURSES)),
    session: AsyncSession = Depends(get_db),
) -> None:
    university_id = _require_university_id(current_user)
    deleted = await delete_course(course_id, university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
