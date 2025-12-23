"""add_name_to_transactions_table

Revision ID: d481217ccf7a
Revises: b4e1a9c2d7f3
Create Date: 2025-12-22 15:35:15.269227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd481217ccf7a'
down_revision = 'b4e1a9c2d7f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column(
            "name",
            sa.String(255),
            server_default="",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("transactions", "name")

