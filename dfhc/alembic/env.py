"""Alembic environment configuration for DFHC API.

This file is loaded by Alembic when running migrations.
DATABASE_URL is read from the environment — never hardcoded here.
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import Base and all models so Alembic can detect schema changes.
from dfhc.app.core.database import Base  # noqa: F401
import dfhc.app.models  # noqa: F401  # ensures all models are registered on Base

# Alembic Config object — gives access to .ini file values.
config = context.config

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def get_url() -> str:
    """Read DATABASE_URL from the environment.

    In TESTING mode, falls back to SQLite so CI can run without PostgreSQL.
    In production, DATABASE_URL must be set explicitly.
    """
    testing = os.getenv("TESTING", "").lower() in ("1", "true", "yes")
    if testing:
        return os.getenv("DATABASE_URL", "sqlite:///./test.db")
    return os.environ["DATABASE_URL"]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
