"""Add-on call tracking hook — fires HTTP events to the backend API.

Never raises; all failures are logged as warnings so the agent is unaffected.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger("call_tracker")

_API_URL = os.getenv("API_URL", "http://localhost:8000")
_AGENT_KEY = os.getenv("AGENT_INTERNAL_API_KEY", "")


class CallTracker:
    def __init__(self) -> None:
        self._call_id: Optional[str] = None
        self._seq: int = 0
        self._client = None

    async def start(
        self,
        room_name: str,
        university_id: Optional[str],
        agent_type: str = "main",
        caller_identity: Optional[str] = None,
    ) -> None:
        if not university_id:
            logger.warning("CallTracker.start: no university_id — skipping")
            return
        try:
            import httpx  # noqa: PLC0415

            self._client = httpx.AsyncClient(base_url=_API_URL, timeout=5.0)
            resp = await self._client.post(
                "/api/v1/calls/internal/start",
                json={
                    "livekit_room_id": room_name,
                    "university_id": str(university_id),
                    "agent_type": agent_type,
                    "caller_identity": caller_identity,
                },
                headers={"X-Agent-API-Key": _AGENT_KEY},
            )
            resp.raise_for_status()
            self._call_id = resp.json().get("id")
            logger.info(f"Call session created: {self._call_id}")
        except Exception as exc:
            logger.warning(f"CallTracker.start failed: {exc}")

    async def log_message(self, role: str, content: str) -> None:
        if not self._call_id or not self._client or not content.strip():
            return
        try:
            self._seq += 1
            await self._client.post(
                f"/api/v1/calls/internal/{self._call_id}/message",
                json={"role": role, "content": content, "sequence": self._seq},
                headers={"X-Agent-API-Key": _AGENT_KEY},
            )
        except Exception as exc:
            logger.warning(f"CallTracker.log_message failed: {exc}")

    async def end(self, call_status: str = "ended") -> None:
        if not self._call_id or not self._client:
            return
        try:
            await self._client.patch(
                f"/api/v1/calls/internal/{self._call_id}/end",
                json={"status": call_status},
                headers={"X-Agent-API-Key": _AGENT_KEY},
            )
            logger.info(f"Call session ended: {self._call_id}")
        except Exception as exc:
            logger.warning(f"CallTracker.end failed: {exc}")
        finally:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
