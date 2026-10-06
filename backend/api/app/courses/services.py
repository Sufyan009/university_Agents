"""Course services — all operations scoped to a university_id."""
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.courses.models import Course
from app.courses.schemas import CourseCreate, CourseUpdate


async def create_course(university_id: str, data: CourseCreate, session: AsyncSession) -> Course:
    course = Course(university_id=uuid.UUID(university_id), **data.model_dump())
    session.add(course)
    await session.flush()
    await session.refresh(course)
    return course


async def get_course_by_id(course_id: str, university_id: str, session: AsyncSession) -> Optional[Course]:
    try:
        cid = uuid.UUID(course_id)
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return None
    result = await session.execute(
        select(Course).where(Course.id == cid, Course.university_id == uid)
    )
    return result.scalar_one_or_none()


async def list_courses(
    university_id: str,
    session: AsyncSession,
    degree_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Course], int]:
    try:
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return [], 0

    statement = select(Course).where(Course.university_id == uid)
    if degree_type:
        statement = statement.where(Course.degree_type == degree_type)
    if search:
        statement = statement.where(Course.name.ilike(f"%{search}%"))

    count_result = await session.execute(select(func.count()).select_from(statement.subquery()))
    total = count_result.scalar() or 0

    statement = statement.order_by(Course.name).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(statement)
    return list(result.scalars().all()), total


async def get_courses_for_university(university_id: str, session: AsyncSession) -> List[Course]:
    """Unpaginated fetch — used by prompt generation."""
    items, _ = await list_courses(university_id, session, page=1, page_size=1000)
    return items


async def update_course(course_id: str, university_id: str, data: CourseUpdate, session: AsyncSession) -> Optional[Course]:
    course = await get_course_by_id(course_id, university_id, session)
    if not course:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        return course
    for field, value in update_dict.items():
        setattr(course, field, value)
    course.updated_at = datetime.utcnow()
    session.add(course)
    await session.flush()
    await session.refresh(course)
    return course


async def delete_course(course_id: str, university_id: str, session: AsyncSession) -> bool:
    course = await get_course_by_id(course_id, university_id, session)
    if not course:
        return False
    await session.delete(course)
    await session.flush()
    return True
