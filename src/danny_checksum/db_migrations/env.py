from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

from danny_checksum.connectors.database.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Build sqlite URL pointing to localdev.db in the project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "localdev.db"
SQLALCHEMY_URL = f"sqlite:///{DB_PATH}"


def run_migrations_offline() -> None:
    context.configure(
        url=SQLALCHEMY_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": SQLALCHEMY_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
