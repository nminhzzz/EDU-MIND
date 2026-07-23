"""
Alembic environment configuration.

- Reads DATABASE_URL from .env via app.core.config (Pydantic BaseSettings).
- Imports all SQLAlchemy models so Alembic can detect schema changes automatically.
- Supports both offline (SQL dump) and online (live connection) migration modes.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Load app settings (reads .env automatically) ─────────────────────────────
from app.core.config import settings

# ── Import Base so Alembic sees target_metadata ───────────────────────────────
from app.models.base import Base  # noqa: F401

# Import every model module so their tables are registered on Base.metadata.
# Add new model files here as the schema grows.
import app.models.user                        # noqa: F401
import app.models.student_preference          # noqa: F401
import app.models.subject                     # noqa: F401
import app.models.classroom                   # noqa: F401
import app.models.classroom_student           # noqa: F401
import app.models.study_document              # noqa: F401
import app.models.study_goal                  # noqa: F401
import app.models.study_plan                  # noqa: F401
import app.models.study_plan_progress         # noqa: F401
import app.models.quiz                        # noqa: F401
import app.models.quiz_attempt                # noqa: F401
import app.models.learning_analytic           # noqa: F401
import app.models.classroom_chat_read_cursor   # noqa: F401
import app.models.notification                # noqa: F401

# ── Alembic config ────────────────────────────────────────────────────────────
config = context.config

# Wire Python logging to alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata object Alembic uses for --autogenerate
target_metadata = Base.metadata

# Inject DATABASE_URL from .env into Alembic config at runtime
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


# ── Migration runners ─────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Run migrations without a live database connection (generates raw SQL).
    Useful for reviewing SQL before applying, or for environments without
    direct DB access.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,          # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations against a live database connection.
    Uses a connection pool to avoid long-held locks during migration.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # NullPool: no persistent connection after migration
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
