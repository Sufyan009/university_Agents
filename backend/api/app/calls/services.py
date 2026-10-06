"""Call tracking services."""
from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.calls.models import CallMessage, CallSession


async def create_call_session(
    university_id: uuid.UUID,
    livekit_room_id: str,
    agent_type: str,
    caller_identity: Optional[str],
    session: AsyncSession,
) -> CallSession:
    call = CallSession(
        university_id=university_id,
        livekit_room_id=livekit_room_id,
        agent_type=agent_type,
        caller_identity=caller_identity,
        status="active",
        started_at=datetime.utcnow(),
    )
    session.add(call)
    await session.commit()
    await session.refresh(call)
    return call


async def add_call_message(
    call_session_id: uuid.UUID, role: str, content: str, sequence: int, session: AsyncSession
) -> CallMessage:
    msg = CallMessage(call_session_id=call_session_id, role=role, content=content, sequence=sequence)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg


async def end_call_session(call_session_id: uuid.UUID, status: str, session: AsyncSession) -> Optional[CallSession]:
    result = await session.execute(select(CallSession).where(CallSession.id == call_session_id))
    call = result.scalars().first()
    if not call:
        return None
    call.status = status
    call.ended_at = datetime.utcnow()
    call.updated_at = datetime.utcnow()
    session.add(call)
    await session.commit()
    await session.refresh(call)
    return call


async def get_active_calls(university_id: uuid.UUID, session: AsyncSession) -> List[CallSession]:
    result = await session.execute(
        select(CallSession)
        .where(CallSession.university_id == university_id, CallSession.status == "active")
        .order_by(CallSession.started_at.desc())
    )
    return list(result.scalars().all())


async def get_recent_calls(university_id: uuid.UUID, session: AsyncSession, limit: int = 50) -> List[CallSession]:
    result = await session.execute(
        select(CallSession)
        .where(CallSession.university_id == university_id)
        .order_by(CallSession.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_call_with_messages(
    call_id: uuid.UUID, university_id: uuid.UUID, session: AsyncSession
) -> Optional[CallSession]:
    result = await session.execute(
        select(CallSession).where(CallSession.id == call_id, CallSession.university_id == university_id)
    )
    return result.scalars().first()


async def get_messages_for_call(call_session_id: uuid.UUID, session: AsyncSession) -> List[CallMessage]:
    result = await session.execute(
        select(CallMessage).where(CallMessage.call_session_id == call_session_id).order_by(CallMessage.sequence)
    )
    return list(result.scalars().all())
