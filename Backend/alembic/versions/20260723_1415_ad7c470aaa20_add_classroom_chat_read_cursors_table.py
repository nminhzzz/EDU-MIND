"""add_classroom_chat_read_cursors_table

Revision ID: ad7c470aaa20
Revises: ae7b32590c24
Create Date: 2026-07-23 14:15:14.654752+07:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ad7c470aaa20'
down_revision: Union[str, None] = 'ae7b32590c24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('classroom_chat_read_cursors',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('classroom_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('last_read_message_id', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['classroom_id'], ['classrooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('classroom_id', 'user_id', name='uq_chat_cursor_classroom_user')
    )


def downgrade() -> None:
    op.drop_table('classroom_chat_read_cursors')
