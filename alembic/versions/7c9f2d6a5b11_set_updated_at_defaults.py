"""set_updated_at_defaults

Revision ID: 7c9f2d6a5b11
Revises: 5b1c2f3e1a4c
Create Date: 2026-02-06 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c9f2d6a5b11"
down_revision = "5b1c2f3e1a4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = ["users", "transactions", "categories", "user_device_tokens"]
    for table in tables:
        op.execute(
            sa.text(
                f"""
                UPDATE {table}
                SET updated_at = COALESCE(updated_at, created_at, now())
                """
            )
        )
        op.execute(
            sa.text(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN updated_at SET DEFAULT now()
                """
            )
        )


def downgrade() -> None:
    tables = ["users", "transactions", "categories", "user_device_tokens"]
    for table in tables:
        op.execute(
            sa.text(
                f"""
                ALTER TABLE {table}
                ALTER COLUMN updated_at DROP DEFAULT
                """
            )
        )
