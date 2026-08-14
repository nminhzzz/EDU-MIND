"""add plan generation state and ai usage

Revision ID: c29e4a6d817b
Revises: b81fd3e27a91
Create Date: 2026-08-14 17:30:00+07:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c29e4a6d817b"
down_revision: Union[str, None] = "b81fd3e27a91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("study_plans", sa.Column("lesson_summary", sa.Text(), nullable=True))
    op.add_column("study_plans", sa.Column("generation_status", sa.String(length=20), nullable=False, server_default="not_started"))
    op.add_column("study_plans", sa.Column("generation_error", sa.Text(), nullable=True))
    op.add_column("study_plans", sa.Column("generation_attempts", sa.BigInteger(), nullable=False, server_default="0"))
    op.add_column("study_plans", sa.Column("generation_started_at", sa.DateTime(), nullable=True))
    op.add_column("study_plans", sa.Column("generation_finished_at", sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE study_plans sp SET generation_status = 'ready' "
        "WHERE sp.rag_content IS NOT NULL AND EXISTS "
        "(SELECT 1 FROM quizzes q WHERE q.study_plan_id = sp.id)"
    )
    op.create_index("ix_study_plans_generation_status", "study_plans", ["generation_status"], unique=False)

    op.create_table(
        "ai_usage",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_type", sa.String(length=40), nullable=False),
        sa.Column("goal_id", sa.BigInteger(), nullable=True),
        sa.Column("plan_id", sa.BigInteger(), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cached_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_usage_request_created", "ai_usage", ["request_type", "created_at"], unique=False)
    op.create_index("ix_ai_usage_goal_plan", "ai_usage", ["goal_id", "plan_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_usage_goal_plan", table_name="ai_usage")
    op.drop_index("ix_ai_usage_request_created", table_name="ai_usage")
    op.drop_table("ai_usage")
    op.drop_index("ix_study_plans_generation_status", table_name="study_plans")
    op.drop_column("study_plans", "generation_finished_at")
    op.drop_column("study_plans", "generation_started_at")
    op.drop_column("study_plans", "generation_attempts")
    op.drop_column("study_plans", "generation_error")
    op.drop_column("study_plans", "generation_status")
    op.drop_column("study_plans", "lesson_summary")
