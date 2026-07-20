"""add_tab_violations_count_to_quiz_attempts

Revision ID: ae7b32590c24
Revises: e16679b3e9b7
Create Date: 2026-07-19 17:12:45.045460+07:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae7b32590c24'
down_revision: Union[str, None] = 'e16679b3e9b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'quiz_attempts',
        sa.Column(
            'tab_violations_count',
            sa.Integer(),
            nullable=False,
            server_default='0'
        )
    )


def downgrade() -> None:
    op.drop_column('quiz_attempts', 'tab_violations_count')
