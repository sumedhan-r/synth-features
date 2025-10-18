"""Application lifespan management for FastAPI."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Generator

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.core.logger import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """Manages application resources (database connections, etc.)."""

    def __init__(self) -> None:
        self._session_factory: sessionmaker | None = None
        self._engine: Engine | None = None

    def get_session_factory(self) -> sessionmaker | None:
        """Get the database session factory."""
        return self._session_factory

    async def init_resources(self) -> None:
        """Initialize application resources (database, etc.)."""
        logger.info("Initializing resources...")

        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "sqlite:///./data/synth.db")
        logger.info(f"Initializing database connection: {database_url}")

        # Create engine with appropriate settings
        connect_args = (
            {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        self._engine = create_engine(database_url, connect_args=connect_args)

        # Create session factory
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

        logger.info("Database connection initialized")

    async def close_resources(self) -> None:
        """Close and cleanup application resources."""
        logger.info("Closing resources...")

        if self._engine:
            self._engine.dispose()
            logger.info("Database connections closed")

        self._session_factory = None
        self._engine = None

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


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Database session

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session_factory = resource_manager.get_session_factory()

    if session_factory is None:
        raise RuntimeError("Database not initialized. Ensure lifespan is configured.")

    db = session_factory()
    try:
        yield db
    finally:
        db.close()
