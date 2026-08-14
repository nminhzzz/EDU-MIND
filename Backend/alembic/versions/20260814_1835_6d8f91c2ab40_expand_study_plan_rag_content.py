"""Expand study plan lecture storage to MEDIUMTEXT.

Revision ID: 6d8f91c2ab40
Revises: c29e4a6d817b
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "6d8f91c2ab40"
down_revision = "c29e4a6d817b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "study_plans",
        "rag_content",
        existing_type=sa.Text(),
        type_=mysql.MEDIUMTEXT(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "study_plans",
        "rag_content",
        existing_type=mysql.MEDIUMTEXT(),
        type_=sa.Text(),
        existing_nullable=True,
    )
