"""FAQ services — all operations scoped to a university_id."""
from datetime import datetime
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.faqs.models import FAQ
from app.faqs.schemas import FAQCreate, FAQUpdate


async def create_faq(university_id: str, data: FAQCreate, session: AsyncSession) -> FAQ:
    faq = FAQ(university_id=uuid.UUID(university_id), **data.model_dump())
    session.add(faq)
    await session.flush()
    await session.refresh(faq)
    return faq


async def get_faq_by_id(faq_id: str, university_id: str, session: AsyncSession) -> Optional[FAQ]:
    try:
        fid = uuid.UUID(faq_id)
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return None
    result = await session.execute(
        select(FAQ).where(FAQ.id == fid, FAQ.university_id == uid)
    )
    return result.scalar_one_or_none()


async def list_faqs(
    university_id: str,
    session: AsyncSession,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[FAQ], int]:
    try:
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return [], 0

    statement = select(FAQ).where(FAQ.university_id == uid)
    if category:
        statement = statement.where(FAQ.category == category)
    if is_active is not None:
        statement = statement.where(FAQ.is_active == is_active)
    if search:
        statement = statement.where(FAQ.question.ilike(f"%{search}%"))

    count_result = await session.execute(select(func.count()).select_from(statement.subquery()))
    total = count_result.scalar() or 0

    statement = statement.order_by(FAQ.question).offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(statement)
    return list(result.scalars().all()), total


async def update_faq(faq_id: str, university_id: str, data: FAQUpdate, session: AsyncSession) -> Optional[FAQ]:
    faq = await get_faq_by_id(faq_id, university_id, session)
    if not faq:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        return faq
    for field, value in update_dict.items():
        setattr(faq, field, value)
    faq.updated_at = datetime.utcnow()
    session.add(faq)
    await session.flush()
    await session.refresh(faq)
    return faq


async def delete_faq(faq_id: str, university_id: str, session: AsyncSession) -> bool:
    faq = await get_faq_by_id(faq_id, university_id, session)
    if not faq:
        return False
    await session.delete(faq)
    await session.flush()
    return True
