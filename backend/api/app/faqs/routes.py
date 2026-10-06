"""FAQ routes — tenant-scoped CRUD."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.faqs.schemas import FAQCreate, FAQListResponse, FAQResponse, FAQUpdate
from app.faqs.services import (
    create_faq,
    delete_faq,
    get_faq_by_id,
    list_faqs,
    update_faq,
)
from app.database import get_db
from app.auth.models import User
from app.roles.dependencies import require_permission, require_write_access
from app.roles.models import Permission
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/faqs", tags=["FAQs"])


def _require_university_id(current_user: User) -> str:
    if not current_user.university_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No university profile found.")
    return str(current_user.university_id)


@router.get("/", response_model=FAQListResponse)
async def list_all(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FAQListResponse:
    university_id = _require_university_id(current_user)
    items, total = await list_faqs(university_id, session, category=category, is_active=is_active, search=search, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size
    return FAQListResponse(
        items=[FAQResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages,
    )


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: FAQCreate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    session: AsyncSession = Depends(get_db),
) -> FAQResponse:
    university_id = _require_university_id(current_user)
    faq = await create_faq(university_id, data, session)
    return FAQResponse.model_validate(faq)


@router.get("/{faq_id}", response_model=FAQResponse)
async def get_one(
    faq_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FAQResponse:
    university_id = _require_university_id(current_user)
    faq = await get_faq_by_id(faq_id, university_id, session)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return FAQResponse.model_validate(faq)


@router.put("/{faq_id}", response_model=FAQResponse)
async def update(
    faq_id: str,
    data: FAQUpdate,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    session: AsyncSession = Depends(get_db),
) -> FAQResponse:
    university_id = _require_university_id(current_user)
    faq = await update_faq(faq_id, university_id, data, session)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return FAQResponse.model_validate(faq)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    faq_id: str,
    _write: User = Depends(require_write_access),
    current_user: User = Depends(require_permission(Permission.MANAGE_KNOWLEDGE)),
    session: AsyncSession = Depends(get_db),
) -> None:
    university_id = _require_university_id(current_user)
    deleted = await delete_faq(faq_id, university_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
