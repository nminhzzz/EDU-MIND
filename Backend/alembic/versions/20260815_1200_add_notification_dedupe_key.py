"""Add a unique key used to make scheduled notifications idempotent."""

from alembic import op
import sqlalchemy as sa


revision = "20260815_1200"
down_revision = "947ab215ef30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("dedupe_key", sa.String(255), nullable=True))
    op.create_index(
        "ux_notification_dedupe_key", "notifications", ["dedupe_key"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ux_notification_dedupe_key", table_name="notifications")
    op.drop_column("notifications", "dedupe_key")
