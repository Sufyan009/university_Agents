"""Call tracking routes — internal (agent) + frontend (JWT) + WebSocket."""
import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.services import decode_token, get_user_by_id
from app.calls.models import CallSession
from app.calls.schemas import (
    CallEndRequest,
    CallMessageRequest,
    CallMessageResponse,
    CallSessionDetail,
    CallSessionResponse,
    CallStartRequest,
)
from app.calls import services
from app.config import get_settings
from app.database import get_db
from app.utils.dependencies import get_current_user
from app.auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/calls", tags=["Calls"])


class _ConnectionManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, university_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(university_id, set()).add(ws)

    def disconnect(self, university_id: str, ws: WebSocket) -> None:
        bucket = self._connections.get(university_id)
        if bucket:
            bucket.discard(ws)

    async def broadcast(self, university_id: str, payload: dict) -> None:
        dead: set[WebSocket] = set()
        for ws in list(self._connections.get(university_id, set())):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections.get(university_id, set()).discard(ws)


manager = _ConnectionManager()


async def _verify_agent_key(x_agent_api_key: str = Header(default="")) -> None:
    settings = get_settings()
    key = settings.agent_internal_api_key
    if not key or x_agent_api_key != key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent API key")


# ── Internal endpoints (called by the LiveKit agent process) ─────────────────
@router.post("/internal/start", response_model=CallSessionResponse, dependencies=[Depends(_verify_agent_key)])
async def internal_start_call(body: CallStartRequest, session: AsyncSession = Depends(get_db)):
    call = await services.create_call_session(
        university_id=body.university_id,
        livekit_room_id=body.livekit_room_id,
        agent_type=body.agent_type,
        caller_identity=body.caller_identity,
        session=session,
    )
    await manager.broadcast(
        str(body.university_id),
        {"type": "call_started", "data": CallSessionResponse.model_validate(call).model_dump(mode="json")},
    )
    return call


@router.post("/internal/{call_id}/message", response_model=CallMessageResponse, dependencies=[Depends(_verify_agent_key)])
async def internal_add_message(call_id: uuid.UUID, body: CallMessageRequest, session: AsyncSession = Depends(get_db)):
    call = await session.get(CallSession, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call session not found")
    msg = await services.add_call_message(
        call_session_id=call_id, role=body.role, content=body.content, sequence=body.sequence, session=session
    )
    await manager.broadcast(
        str(call.university_id),
        {"type": "message_added", "data": {"call_session_id": str(call_id), **CallMessageResponse.model_validate(msg).model_dump(mode="json")}},
    )
    return msg


@router.patch("/internal/{call_id}/end", response_model=CallSessionResponse, dependencies=[Depends(_verify_agent_key)])
async def internal_end_call(call_id: uuid.UUID, body: CallEndRequest, session: AsyncSession = Depends(get_db)):
    call = await services.end_call_session(call_id, body.status, session)
    if not call:
        raise HTTPException(status_code=404, detail="Call session not found")
    await manager.broadcast(
        str(call.university_id),
        {"type": "call_ended", "data": {"call_session_id": str(call_id), "status": body.status}},
    )
    return call


# ── Frontend endpoints (JWT auth, scoped by university) ──────────────────────
@router.get("/", response_model=List[CallSessionResponse])
async def list_calls(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    if not current_user.university_id:
        return []
    if status_filter == "active":
        return await services.get_active_calls(current_user.university_id, session)
    return await services.get_recent_calls(current_user.university_id, session)


@router.get("/{call_id}", response_model=CallSessionDetail)
async def get_call(
    call_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    if not current_user.university_id:
        raise HTTPException(status_code=404, detail="Call not found")
    call = await services.get_call_with_messages(call_id, current_user.university_id, session)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    messages = await services.get_messages_for_call(call_id, session)
    return CallSessionDetail(
        **CallSessionResponse.model_validate(call).model_dump(),
        messages=[CallMessageResponse.model_validate(m) for m in messages],
    )


# ── WebSocket — real-time events scoped to university ────────────────────────
@router.websocket("/ws")
async def calls_websocket(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload or payload.type != "access":
        await websocket.close(code=4001)
        return

    from app.database import _async_session_maker  # noqa: PLC0415
    if _async_session_maker is None:
        await websocket.close(code=4003)
        return

    async with _async_session_maker() as db:
        user = await get_user_by_id(payload.sub, db)

    if not user or not user.is_active or not user.university_id:
        await websocket.close(code=4001)
        return

    university_id = str(user.university_id)
    await manager.connect(university_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(university_id, websocket)
