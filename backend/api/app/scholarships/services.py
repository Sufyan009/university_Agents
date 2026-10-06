"""Scholarship services — all operations scoped to a university_id."""
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.scholarships.models import Scholarship
from app.scholarships.schemas import ScholarshipCreate, ScholarshipUpdate


async def create_scholarship(university_id: str, data: ScholarshipCreate, session: AsyncSession) -> Scholarship:
    scholarship = Scholarship(university_id=uuid.UUID(university_id), **data.model_dump())
    session.add(scholarship)
    await session.flush()
    await session.refresh(scholarship)
    return scholarship


async def get_scholarship_by_id(scholarship_id: str, university_id: str, session: AsyncSession) -> Optional[Scholarship]:
    try:
        sid = uuid.UUID(scholarship_id)
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return None
    result = await session.execute(
        select(Scholarship).where(Scholarship.id == sid, Scholarship.university_id == uid)
    )
    return result.scalar_one_or_none()


async def list_scholarships(
    university_id: str,
    session: AsyncSession,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Scholarship], int]:
    try:
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return [], 0

    statement = select(Scholarship).where(Scholarship.university_id == uid)
    if is_active is not None:
        statement = statement.where(Scholarship.is_active == is_active)
    if search:
        statement = statement.where(Scholarship.name.ilike(f"%{search}%"))

    count_result = await session.execute(select(func.count()).select_from(statement.subquery()))
    total = count_result.scalar() or 0

    statement = statement.order_by(Scholarship.name).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(statement)
    return list(result.scalars().all()), total


async def update_scholarship(scholarship_id: str, university_id: str, data: ScholarshipUpdate, session: AsyncSession) -> Optional[Scholarship]:
    scholarship = await get_scholarship_by_id(scholarship_id, university_id, session)
    if not scholarship:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        return scholarship
    for field, value in update_dict.items():
        setattr(scholarship, field, value)
    scholarship.updated_at = datetime.utcnow()
    session.add(scholarship)
    await session.flush()
    await session.refresh(scholarship)
    return scholarship


async def delete_scholarship(scholarship_id: str, university_id: str, session: AsyncSession) -> bool:
    scholarship = await get_scholarship_by_id(scholarship_id, university_id, session)
    if not scholarship:
        return False
    await session.delete(scholarship)
    await session.flush()
    return True
