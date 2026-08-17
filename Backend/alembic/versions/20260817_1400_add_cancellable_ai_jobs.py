"""Add durable cancellable AI jobs."""

from alembic import op
import sqlalchemy as sa


revision = "20260817_1400"
down_revision = "20260815_1200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="queued"),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_jobs_owner_created", "ai_jobs", ["user_id", "created_at"])
    op.create_index("ix_ai_jobs_status", "ai_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_ai_jobs_status", table_name="ai_jobs")
    op.drop_index("ix_ai_jobs_owner_created", table_name="ai_jobs")
    op.drop_table("ai_jobs")
