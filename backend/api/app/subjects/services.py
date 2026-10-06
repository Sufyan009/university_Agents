"""Subject services — all operations scoped to a university_id."""
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.courses.models import Course
from app.subjects.models import Subject
from app.subjects.schemas import SubjectCreate, SubjectUpdate


async def create_subject(university_id: str, data: SubjectCreate, session: AsyncSession) -> Subject:
    uid = uuid.UUID(university_id)
    course_result = await session.execute(
        select(Course).where(Course.id == data.course_id, Course.university_id == uid)
    )
    if not course_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found in this university")
    subject = Subject(university_id=uid, **data.model_dump())
    session.add(subject)
    await session.flush()
    await session.refresh(subject)
    return subject


async def get_subject_by_id(subject_id: str, university_id: str, session: AsyncSession) -> Optional[Subject]:
    try:
        sid = uuid.UUID(subject_id)
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return None
    result = await session.execute(
        select(Subject).where(Subject.id == sid, Subject.university_id == uid)
    )
    return result.scalar_one_or_none()


async def list_subjects(
    university_id: str,
    session: AsyncSession,
    course_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Subject], int]:
    try:
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return [], 0

    statement = select(Subject).where(Subject.university_id == uid)
    if course_id:
        try:
            statement = statement.where(Subject.course_id == uuid.UUID(course_id))
        except (ValueError, TypeError):
            return [], 0
    if search:
        statement = statement.where(Subject.name.ilike(f"%{search}%"))

    count_result = await session.execute(select(func.count()).select_from(statement.subquery()))
    total = count_result.scalar() or 0

    statement = statement.order_by(Subject.name).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(statement)
    return list(result.scalars().all()), total


async def update_subject(subject_id: str, university_id: str, data: SubjectUpdate, session: AsyncSession) -> Optional[Subject]:
    subject = await get_subject_by_id(subject_id, university_id, session)
    if not subject:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        return subject
    for field, value in update_dict.items():
        setattr(subject, field, value)
    subject.updated_at = datetime.utcnow()
    session.add(subject)
    await session.flush()
    await session.refresh(subject)
    return subject


async def delete_subject(subject_id: str, university_id: str, session: AsyncSession) -> bool:
    subject = await get_subject_by_id(subject_id, university_id, session)
    if not subject:
        return False
    await session.delete(subject)
    await session.flush()
    return True
