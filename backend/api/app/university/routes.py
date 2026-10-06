"""University profile + agent config routes (tenant owner scope)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.university.schemas import (
    AgentConfigCreate,
    AgentConfigResponse,
    AgentConfigUpdate,
    GeneratedPromptResponse,
    UniversityCreate,
    UniversityResponse,
    UniversityUpdate,
)
from app.university.services import (
    create_agent_config,
    create_university,
    generate_system_prompt,
    get_agent_config,
    get_university_by_user,
    update_agent_config,
    update_university,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/university", tags=["University"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found. Create one first.")
    return str(current_user.university_id)


# ── Profile ──────────────────────────────────────────────────────────────────
@router.post("/profile", response_model=UniversityResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: UniversityCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await create_university(str(current_user.id), data, session)
    return UniversityResponse.model_validate(university)


@router.get("/profile", response_model=UniversityResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await get_university_by_user(str(current_user.id), session)
    if not university:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University profile not found. Create one first.")
    return UniversityResponse.model_validate(university)


@router.put("/profile", response_model=UniversityResponse)
async def update_profile(
    data: UniversityUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UniversityResponse:
    university = await update_university(str(current_user.id), data, session)
    if not university:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University profile not found")
    return UniversityResponse.model_validate(university)


# ── Agent config ───────────────────────────────────────────────────────────
@router.post("/config", response_model=AgentConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_config(
    data: AgentConfigCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.CONFIGURE_VOICE_AGENT)),
    session: AsyncSession = Depends(get_db),
) -> AgentConfigResponse:
    university_id = str(data.university_id) if data.university_id else _require_university_id(current_user)
    config = await create_agent_config(university_id, data, session)
    return AgentConfigResponse.model_validate(config)


@router.get("/config", response_model=AgentConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AgentConfigResponse:
    university_id = _require_university_id(current_user)
    config = await get_agent_config(university_id, session)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent configuration not found. Create one first.")
    return AgentConfigResponse.model_validate(config)


@router.put("/config", response_model=AgentConfigResponse)
async def update_config(
    data: AgentConfigUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.CONFIGURE_VOICE_AGENT)),
    session: AsyncSession = Depends(get_db),
) -> AgentConfigResponse:
    university_id = _require_university_id(current_user)
    config = await update_agent_config(university_id, data, session)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to update agent configuration")
    return AgentConfigResponse.model_validate(config)


@router.get("/prompt", response_model=GeneratedPromptResponse)
async def get_prompt(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GeneratedPromptResponse:
    result = await generate_system_prompt(str(current_user.id), session)
    return GeneratedPromptResponse(**result)
