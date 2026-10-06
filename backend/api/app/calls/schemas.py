"""Call tracking schemas."""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel


class CallStartRequest(BaseModel):
    livekit_room_id: str
    university_id: uuid.UUID
    agent_type: str = "main"
    caller_identity: Optional[str] = None


class CallMessageRequest(BaseModel):
    role: str
    content: str
    sequence: int = 0


class CallEndRequest(BaseModel):
    status: str = "ended"


class CallMessageResponse(BaseModel):
    id: uuid.UUID
    call_session_id: uuid.UUID
    role: str
    content: str
    sequence: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CallSessionResponse(BaseModel):
    id: uuid.UUID
    university_id: uuid.UUID
    livekit_room_id: str
    agent_type: str
    status: str
    caller_identity: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class CallSessionDetail(CallSessionResponse):
    messages: List[CallMessageResponse] = []
