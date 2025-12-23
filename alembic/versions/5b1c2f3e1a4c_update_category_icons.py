"""update_category_icons

Revision ID: 5b1c2f3e1a4c
Revises: 3d2c7f4b2dd7
Create Date: 2026-02-06 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b1c2f3e1a4c"
down_revision = "3d2c7f4b2dd7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    icon_map = {
        # Expense
        ("Food & Drinks", "expense"): "restaurant_menu",
        ("Shopping", "expense"): "shopping_bag_outlined",
        ("Home & Bills", "expense"): "home_outlined",
        ("Transport", "expense"): "directions_car_filled_outlined",
        ("Health & Education", "expense"): "health_and_safety_outlined",
        ("Finance & Invest", "expense"): "savings_outlined",
        ("Social & Gifts", "expense"): "cake_outlined",
        ("Other", "expense"): "category_outlined",
        # Income
        ("Salary", "income"): "attach_money",
        ("Bonus", "income"): "stars_rounded",
        ("Allowance", "income"): "card_giftcard",
        ("Side Job", "income"): "work_outline",
        ("Invest Profit", "income"): "trending_up",
        ("Small Business", "income"): "storefront_outlined",
        ("Family Support", "income"): "volunteer_activism_outlined",
        ("Refund", "income"): "refresh_outlined",
        ("Other Income", "income"): "category_outlined",
    }

    conn = op.get_bind()
    for (name, cat_type), icon in icon_map.items():
        conn.execute(
            sa.text(
                "UPDATE categories SET icon = :icon WHERE name = :name AND type = :type"
            ),
            {"icon": icon, "name": name, "type": cat_type},
        )


def downgrade() -> None:
    # Revert icons back to default attach_money to keep downgrade simple
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE categories SET icon = 'attach_money'"))
