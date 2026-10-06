"""Database connection and session management."""
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine: Optional = None
_async_session_maker: Optional = None

# Base class for declarative models
Base = declarative_base()


async def connect_to_database() -> None:
    """Initialize PostgreSQL connection."""
    global _engine, _async_session_maker

    settings = get_settings()

    try:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
        )

        _async_session_maker = sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("Successfully connected to PostgreSQL")

    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise


async def close_database_connection() -> None:
    """Close PostgreSQL connection."""
    global _engine

    if _engine:
        await _engine.dispose()
        logger.info("PostgreSQL connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    if _async_session_maker is None:
        raise RuntimeError("Database not connected. Call connect_to_database() first.")

    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Backward-compatible function name for clarity
get_session = get_db
