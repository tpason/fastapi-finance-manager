"""add_user_limit_amount

Revision ID: b4e1a9c2d7f3
Revises: 8c72b5c9b4f1
Create Date: 2025-02-14 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b4e1a9c2d7f3"
down_revision = "8c72b5c9b4f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "limit_amount",
            sa.Numeric(10, 2),
            server_default="2000000.0",
            nullable=False,
        ),
    )
    op.execute("UPDATE users SET limit_amount = 2000000.0 WHERE limit_amount IS NULL")


def downgrade() -> None:
    op.drop_column("users", "limit_amount")
