"""convert_ids_to_uuid7

Revision ID: 0714db8dcf21
Revises:
Create Date: 2025-12-02 10:06:24.191879

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '0714db8dcf21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Initial schema for fresh deployments (UUID primary keys).
    Idempotent for empty databases on Render free tier.
    """
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Users (minimal columns; later migrations add role/limit_amount)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR NOT NULL UNIQUE,
            username VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            full_name VARCHAR,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")

    # Categories (user_id removed; join table added in later migration)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL,
            description VARCHAR,
            type VARCHAR NOT NULL,
            color VARCHAR,
            icon VARCHAR,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_categories_id ON categories (id)")
    op.execute(
        """
        ALTER TABLE categories
        DROP CONSTRAINT IF EXISTS uq_category_name_type;
        """
    )
    op.execute(
        """
        ALTER TABLE categories
        ADD CONSTRAINT uq_category_name_type UNIQUE (name, type);
        """
    )

    # Transactions (name added later in migration d481217ccf7a)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            amount NUMERIC(10,2) NOT NULL,
            type VARCHAR NOT NULL,
            description TEXT,
            date TIMESTAMPTZ NOT NULL DEFAULT now(),
            user_id UUID NOT NULL,
            category_id UUID,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now(),
            CONSTRAINT transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id),
            CONSTRAINT transactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions (id)")


def downgrade() -> None:
    # For simplicity, drop tables (fresh deployments only).
    op.execute("DROP TABLE IF EXISTS transactions CASCADE")
    op.execute("DROP TABLE IF EXISTS categories CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
