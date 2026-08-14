"""Add separate lesson and quiz generation statuses.

Revision ID: 947ab215ef30
Revises: 6d8f91c2ab40
"""

from alembic import op
import sqlalchemy as sa

revision = "947ab215ef30"
down_revision = "6d8f91c2ab40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("study_plans", sa.Column("lesson_status", sa.String(20), nullable=False, server_default="not_started"))
    op.add_column("study_plans", sa.Column("quiz_status", sa.String(20), nullable=False, server_default="not_started"))
    op.execute("UPDATE study_plans SET lesson_status = CASE WHEN rag_content IS NOT NULL THEN 'ready' ELSE generation_status END")
    op.execute("UPDATE study_plans sp SET quiz_status = CASE WHEN EXISTS (SELECT 1 FROM quizzes q WHERE q.study_plan_id = sp.id) THEN 'ready' ELSE 'not_started' END")


def downgrade() -> None:
    op.drop_column("study_plans", "quiz_status")
    op.drop_column("study_plans", "lesson_status")
