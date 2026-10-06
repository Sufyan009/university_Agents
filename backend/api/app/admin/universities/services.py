"""Admin university management services (platform-admin scope, cross-tenant)."""
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.university.models import University
from app.university.schemas import UniversityCreate, UniversityUpdate


async def admin_create_university(data: UniversityCreate, admin_id: uuid.UUID, session: AsyncSession) -> University:
    existing = await session.execute(select(University).where(University.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A university with this name already exists")

    if data.phone:
        phone_clash = await session.execute(select(University).where(University.phone == data.phone))
        if phone_clash.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This phone number is already assigned to another university")

    now = datetime.utcnow()
    d = data.model_dump()
    university = University(id=uuid.uuid4(), admin_id=admin_id, created_at=now, updated_at=now, **d)
    session.add(university)
    await session.flush()
    await session.refresh(university)
    return university


async def admin_list_universities(
    session: AsyncSession, search: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Tuple[List[University], int]:
    statement = select(University)
    if search:
        statement = statement.where(University.name.ilike(f"%{search}%"))
    count_result = await session.execute(select(func.count()).select_from(statement.subquery()))
    total = count_result.scalar() or 0
    statement = statement.order_by(University.name).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(statement)
    return list(result.scalars().all()), total


async def admin_get_university(university_id: str, session: AsyncSession) -> Optional[University]:
    try:
        return await session.get(University, uuid.UUID(university_id))
    except (ValueError, TypeError):
        return None


async def admin_update_university(university_id: str, data: UniversityUpdate, session: AsyncSession) -> Optional[University]:
    university = await admin_get_university(university_id, session)
    if not university:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(university, field, value)
    university.updated_at = datetime.utcnow()
    session.add(university)
    await session.flush()
    await session.refresh(university)
    return university


async def admin_delete_university(university_id: str, session: AsyncSession) -> bool:
    university = await admin_get_university(university_id, session)
    if not university:
        return False
    await session.delete(university)
    await session.flush()
    return True
