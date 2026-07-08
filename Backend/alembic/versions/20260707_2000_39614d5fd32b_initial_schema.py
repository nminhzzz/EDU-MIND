"""initial_schema — baseline

This is the BASELINE migration. It stamps the existing database as the
starting point for Alembic without modifying any tables.

Tables currently in the DB that have no model (kept intentionally):
  - question_bank   — planned feature (stub repository exists)
  - questions       — planned feature (stub repository exists)
  - classroom_subjects — legacy table, to be removed in a dedicated migration

Revision ID: 39614d5fd32b
Revises:
Create Date: 2026-07-07 20:00:36.871937+07:00
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "39614d5fd32b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Baseline migration — no changes applied.
    # The current database schema IS the starting point.
    pass


def downgrade() -> None:
    # Cannot roll back to "before the project existed".
    pass
