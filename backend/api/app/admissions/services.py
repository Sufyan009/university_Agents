"""Admission services — all operations scoped to a university_id (1:1 record)."""
from datetime import datetime
from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.admissions.models import AdmissionInfo
from app.admissions.schemas import AdmissionCreate, AdmissionUpdate


async def get_admission_info_by_university(university_id: str, session: AsyncSession) -> Optional[AdmissionInfo]:
    try:
        uid = uuid.UUID(university_id)
    except (ValueError, TypeError):
        return None
    result = await session.execute(
        select(AdmissionInfo).where(AdmissionInfo.university_id == uid)
    )
    return result.scalar_one_or_none()


async def create_admission_info(university_id: str, data: AdmissionCreate, session: AsyncSession) -> AdmissionInfo:
    existing = await get_admission_info_by_university(university_id, session)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admission info already exists. Use PUT to update.",
        )
    info = AdmissionInfo(university_id=uuid.UUID(university_id), **data.model_dump())
    session.add(info)
    await session.flush()
    await session.refresh(info)
    return info


async def update_admission_info(university_id: str, data: AdmissionUpdate, session: AsyncSession) -> AdmissionInfo:
    info = await get_admission_info_by_university(university_id, session)
    if not info:
        info = AdmissionInfo(university_id=uuid.UUID(university_id), **data.model_dump())
        session.add(info)
        await session.flush()
        await session.refresh(info)
        return info
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(info, field, value)
    info.updated_at = datetime.utcnow()
    session.add(info)
    await session.flush()
    await session.refresh(info)
    return info


async def delete_admission_info(university_id: str, session: AsyncSession) -> bool:
    info = await get_admission_info_by_university(university_id, session)
    if not info:
        return False
    await session.delete(info)
    await session.flush()
    return True
