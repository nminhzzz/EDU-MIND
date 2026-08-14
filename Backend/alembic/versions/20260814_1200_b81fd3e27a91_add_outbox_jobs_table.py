"""add outbox jobs table

Revision ID: b81fd3e27a91
Revises: ad7c470aaa20
Create Date: 2026-08-14 12:00:00+07:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b81fd3e27a91"
down_revision: Union[str, None] = "ad7c470aaa20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outbox_jobs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("task_name", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("unique_key", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("unique_key", name="uq_outbox_jobs_unique_key"),
    )
    op.create_index(
        "ix_outbox_jobs_dispatch",
        "outbox_jobs",
        ["status", "available_at", "id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_outbox_jobs_dispatch", table_name="outbox_jobs")
    op.drop_table("outbox_jobs")
