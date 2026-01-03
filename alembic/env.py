from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import sys
import db.models  # 👈 THIS LINE IS THE FIX

from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from db.base import Base
from core.config import settings

target_metadata = Base.metadata

# Get the database URL from settings
def get_db_url():
    try:
        # db_url = settings.DATABASE_URL or "sqlite:///./test.db"
        # # Convert async driver to sync for Alembic
        # if "asyncpg://" in db_url:
        #     db_url = db_url.replace("asyncpg://", "postgresql://")
        # if "asyncmy://" in db_url:
        #     db_url = db_url.replace("asyncmy://", "mysql+pymysql://")
        return "postgresql://postgres:Diagnopet#55@db.qvgnhzuqchglxwhhspnr.supabase.co:5432/postgres"
    except Exception:
        return "postgresql://postgres:Diagnopet#55@db.qvgnhzuqchglxwhhspnr.supabase.co:5432/postgres"

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()



def run_migrations_online() -> None:
    """Run migrations in 'online' mode using Supabase PostgreSQL."""

    # Get DB URL (force sync driver for Alembic)
    db_url = get_db_url()

    # If someone accidentally passed async URL, fix it
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = db_url

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
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
