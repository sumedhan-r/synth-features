import os
from logging.config import fileConfig
from typing import Final

from alembic import context
from sqlalchemy import create_engine, engine_from_config, pool
from sqlalchemy.exc import OperationalError

from src.api.core.logger import get_logger
from src.db.client_db.models.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

Base.registry.configure()
target_metadata = Base.metadata

logger = get_logger(__name__)

DB_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT: Final[str] = os.getenv("POSTGRES_PORT", "5432")
DB_USER: Final[str] = os.getenv("POSTGRES_USER", "dummy")
DB_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "dummy")
DB_NAME: Final[str] = os.getenv("POSTGRES_DB", "admin_db")

postgres_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

config.set_main_option("sqlalchemy.url", postgres_url)

engine = create_engine(config.get_main_option("sqlalchemy.url", "dummy_sqlalchemy_url"))



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    logger.info("Migrating admin database offline")
    try:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()
        logger.info("Success.")
    except OperationalError as err:
        error_message = err.orig
        logger.warning(f"Failed. Details : {error_message}")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    logger.info("Migrating admin database online")
    try:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
        logger.info("Success.")
    except OperationalError as err:
        error_message = err.orig
        logger.warning(f"Failed. Details : {error_message}")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
