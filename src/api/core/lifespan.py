"""Application lifespan management for FastAPI."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api.core.logger import get_logger

logger = get_logger(__name__)


def _convert_to_async_url(database_url: str) -> str:
    """
    Convert sync database URL to async driver URL.

    Args:
        database_url: Sync database URL

    Returns:
        Async database URL with appropriate driver
    """
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("mysql://"):
        return database_url.replace("mysql://", "mysql+aiomysql://")
    elif database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://")
    return database_url


class ResourceManager:
    """Manages application resources (database connections, etc.)."""

    def __init__(self) -> None:
        self._async_session_factory: async_sessionmaker | None = None
        self._async_engine: AsyncEngine | None = None

    def get_async_session_factory(self) -> async_sessionmaker | None:
        """Get the async database session factory."""
        return self._async_session_factory

    async def init_resources(self) -> None:
        """Initialize application resources (database, etc.)."""
        logger.info("Initializing resources...")

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "sqlite:///./data/synth.db")
        async_database_url = _convert_to_async_url(database_url)
        logger.info(f"Initializing async database connection: {async_database_url}")

        # Create async engine
        self._async_engine = create_async_engine(
            async_database_url,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using
        )

        # Create async session factory
        self._async_session_factory = async_sessionmaker(
            self._async_engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        logger.info("Async database connection initialized")

    async def close_resources(self) -> None:
        """Close and cleanup application resources."""
        logger.info("Closing resources...")

        if self._async_engine:
            await self._async_engine.dispose()
            logger.info("Async database connections closed")

        self._async_session_factory = None
        self._async_engine = None

        logger.info("All resources closed")


resource_manager = ResourceManager()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Manages initialization and cleanup of resources.
    """
    await resource_manager.init_resources()

    yield

    await resource_manager.close_resources()


def get_async_session_factory() -> async_sessionmaker:
    """
    Get the async session factory.

    Returns:
        Async session factory

    Raises:
        RuntimeError: If database not initialized
    """
    session_factory = resource_manager.get_async_session_factory()

    if session_factory is None:
        raise RuntimeError("Database not initialized. Ensure lifespan is configured.")

    return session_factory
