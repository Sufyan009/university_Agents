"""Authentication services."""
from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.schemas import AdminCreate, TokenPayload, UserCreate, UserUpdate
from app.config import get_settings
from app.auth.models import Role, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": user_id, "exp": expire, "iat": datetime.utcnow(), "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {"sub": user_id, "exp": expire, "iat": datetime.utcnow(), "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[TokenPayload]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if user_id is None or token_type is None:
            return None
        return TokenPayload(
            sub=user_id,
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
            type=token_type
        )
    except JWTError:
        return None


async def register_user(user_data: UserCreate, session: AsyncSession) -> User:
    """Register a new user, linking them to an existing university by name."""
    from app.university.models import University

    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    university_name = user_data.university_name
    university_result = await session.execute(
        select(University).where(University.name == university_name)
    )
    university = university_result.scalar_one_or_none()
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No university found with name '{university_name}'"
        )

    now = datetime.utcnow()
    user_dict = user_data.model_dump()
    user_dict.pop("password")
    user_dict.pop("university_name")

    new_user = User(
        **user_dict,
        university_id=university.id,
        password_hash=hash_password(user_data.password),
        created_at=now,
        updated_at=now
    )

    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    return new_user


async def create_admin(admin_data: AdminCreate, session: AsyncSession) -> User:
    """Create an admin user with email and password only."""
    statement = select(User).where(User.email == admin_data.email)
    result = await session.execute(statement)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    now = datetime.utcnow()
    new_user = User(
        email=admin_data.email,
        password_hash=hash_password(admin_data.password),
        role=Role.ADMIN,
        phone=None,
        university_id=None,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    session.add(new_user)
    await session.flush()
    await session.refresh(new_user)
    return new_user


async def authenticate_user(email: str, password: str, session: AsyncSession) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user_by_id(user_id: str, session: AsyncSession) -> Optional[User]:
    try:
        uuid_id = uuid.UUID(user_id)
        statement = select(User).where(User.id == uuid_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    except (ValueError, TypeError):
        return None


async def update_user(user_id: str, update_data: UserUpdate, session: AsyncSession) -> Optional[User]:
    try:
        uuid_id = uuid.UUID(user_id)
    except (ValueError, TypeError):
        return None

    statement = select(User).where(User.id == uuid_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        return user

    allowed_fields = {"name", "phone"}
    for field, value in update_dict.items():
        if field in allowed_fields:
            setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def change_password(user_id: str, current_password: str, new_password: str, session: AsyncSession) -> bool:
    try:
        uuid_id = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    statement = select(User).where(User.id == uuid_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.password_hash = hash_password(new_password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.flush()
    return True
