"""update_category_colors

Revision ID: 8c72b5c9b4f1
Revises: 7c9f2d6a5b11
Create Date: 2026-02-06 01:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c72b5c9b4f1"
down_revision = "7c9f2d6a5b11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    color_map = {
        # Expense
        ("Food & Drinks", "expense"): "accentPink",
        ("Shopping", "expense"): "accentPurple",
        ("Home & Bills", "expense"): "primary",
        ("Transport", "expense"): "accentBlue",
        ("Health & Education", "expense"): "teal",
        ("Finance & Invest", "expense"): "orangeAccent",
        ("Social & Gifts", "expense"): "brown",
        ("Other", "expense"): "grey",
        # Income
        ("Salary", "income"): "primary",
        ("Bonus", "income"): "amber",
        ("Allowance", "income"): "accentPink",
        ("Side Job", "income"): "accentBlue",
        ("Invest Profit", "income"): "green",
        ("Small Business", "income"): "deepPurple",
        ("Family Support", "income"): "redAccent",
        ("Refund", "income"): "teal",
        ("Other Income", "income"): "grey",
        ("Other", "income"): "grey",  # in case name was created as "Other"
    }

    conn = op.get_bind()
    for (name, cat_type), color in color_map.items():
        conn.execute(
            sa.text(
                "UPDATE categories SET color = :color WHERE name = :name AND type = :type"
            ),
            {"color": color, "name": name, "type": cat_type},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE categories SET color = 'primary'"))
