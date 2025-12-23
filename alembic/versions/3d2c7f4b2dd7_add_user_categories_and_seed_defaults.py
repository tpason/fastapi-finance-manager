"""add_user_categories_and_seed_defaults

Revision ID: 3d2c7f4b2dd7
Revises: 17845bf84fa9
Create Date: 2026-02-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = "3d2c7f4b2dd7"
down_revision = "17845bf84fa9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Idempotent safety: remove stray table/constraint/column if already present
    op.execute("DROP TABLE IF EXISTS user_categories CASCADE")

    # Create user_categories join table
    op.create_table(
        "user_categories",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "category_id"),
    )
    op.create_index(op.f("ix_user_categories_user_id"), "user_categories", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_categories_category_id"), "user_categories", ["category_id"], unique=False)

    # Drop old foreign key and column on categories if they still exist
    op.execute("ALTER TABLE categories DROP CONSTRAINT IF EXISTS categories_user_id_fkey")
    op.execute("ALTER TABLE categories DROP COLUMN IF EXISTS user_id")

    # Ensure unique constraint on name/type (drop first if present, then add)
    op.execute("ALTER TABLE categories DROP CONSTRAINT IF EXISTS uq_category_name_type")
    with op.batch_alter_table("categories") as batch_op:
        batch_op.create_unique_constraint("uq_category_name_type", ["name", "type"])

    # Seed default categories from the Flutter list (name=label, description=subtitle)
    seed_categories = [
        # Expense
        ("Food & Drinks", "Meals, coffee, eating out", "expense"),
        ("Shopping", "Clothes, cosmetics, accessories", "expense"),
        ("Home & Bills", "Rent, utilities, household", "expense"),
        ("Transport", "Taxi, fuel, travel", "expense"),
        ("Health & Education", "Study, hospital, insurance", "expense"),
        ("Finance & Invest", "Debt, interest, investing", "expense"),
        ("Social & Gifts", "Gifts, parties, charity", "expense"),
        ("Other", "Other expense", "expense"),
        # Income
        ("Salary", "Primary monthly income", "income"),
        ("Bonus", "KPI or year-end bonus", "income"),
        ("Allowance", "Meal, commute stipend", "income"),
        ("Side Job", "Freelance, overtime", "income"),
        ("Invest Profit", "Stocks, crypto, funds", "income"),
        ("Small Business", "Online sales, services", "income"),
        ("Family Support", "Money from parents", "income"),
        ("Refund", "Reimbursement, cashback", "income"),
        ("Other Income", "Other income", "income"),
    ]

    insert_sql = """
        INSERT INTO categories (id, name, description, type, color, icon)
        VALUES (:id, :name, :description, :type, 'primary', 'attach_money')
        ON CONFLICT (name, type) DO NOTHING
    """
    for name, description, cat_type in seed_categories:
        bind.execute(
            sa.text(insert_sql),
            {
                "id": uuid.uuid4(),
                "name": name,
                "description": description,
                "type": cat_type,
            },
        )


def downgrade() -> None:
    # Remove seeded categories
    op.execute(
        """
        DELETE FROM categories
        WHERE name IN (
            'Food & Drinks','Shopping','Home & Bills','Transport','Health & Education',
            'Finance & Invest','Social & Gifts','Other','Salary','Bonus','Allowance',
            'Side Job','Invest Profit','Small Business','Family Support','Refund','Other Income'
        )
        """
    )

    # Recreate user_id column on categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key("categories_user_id_fkey", "users", ["user_id"], ["id"])
        batch_op.drop_constraint("uq_category_name_type", type_="unique")

    # Move links back to categories table (best effort; may duplicate if multiple users shared a category)
    op.execute(
        """
        UPDATE categories c
        SET user_id = uc.user_id
        FROM (
            SELECT category_id, MIN(user_id) AS user_id
            FROM user_categories
            GROUP BY category_id
        ) uc
        WHERE c.id = uc.category_id
        """
    )

    # Drop join table
    op.drop_index(op.f("ix_user_categories_category_id"), table_name="user_categories")
    op.drop_index(op.f("ix_user_categories_user_id"), table_name="user_categories")
    op.drop_table("user_categories")
