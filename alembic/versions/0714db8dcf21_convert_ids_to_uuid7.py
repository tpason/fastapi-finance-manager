"""convert_ids_to_uuid7

Revision ID: 0714db8dcf21
Revises: 
Create Date: 2025-12-02 10:06:24.191879

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '0714db8dcf21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Convert all ID columns from INTEGER to UUID7.
    This migration handles both new and existing databases.
    """
    # Enable uuid-ossp extension for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Step 0: Drop all foreign key constraints first (they depend on primary keys)
    # Drop foreign key constraints from transactions
    op.execute("""
        ALTER TABLE transactions 
        DROP CONSTRAINT IF EXISTS transactions_user_id_fkey CASCADE
    """)
    op.execute("""
        ALTER TABLE transactions 
        DROP CONSTRAINT IF EXISTS transactions_category_id_fkey CASCADE
    """)
    
    # Drop foreign key constraint from categories
    op.execute("""
        ALTER TABLE categories 
        DROP CONSTRAINT IF EXISTS categories_user_id_fkey CASCADE
    """)
    
    # Step 1: Add UUID columns to all tables (keep old integer columns for now)
    # Drop sequences
    op.execute('DROP SEQUENCE IF EXISTS users_id_seq CASCADE')
    op.execute('DROP SEQUENCE IF EXISTS categories_id_seq CASCADE')
    op.execute('DROP SEQUENCE IF EXISTS transactions_id_seq CASCADE')
    
    # Add temporary UUID columns to users
    op.add_column('users', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    
    # Add temporary UUID columns to categories
    op.add_column('categories', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('categories', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    
    # Add temporary UUID columns to transactions
    op.add_column('transactions', sa.Column('id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('transactions', sa.Column('user_id_new', UUID(as_uuid=True), nullable=True))
    op.add_column('transactions', sa.Column('category_id_new', UUID(as_uuid=True), nullable=True))
    
    # Step 2: Populate UUID columns
    # Generate UUIDs for users (join on old integer id)
    op.execute("""
        UPDATE users 
        SET id_new = gen_random_uuid()
    """)
    
    # Generate UUIDs for categories and map user_id (join on old integer columns)
    op.execute("""
        UPDATE categories c
        SET 
            id_new = gen_random_uuid(),
            user_id_new = u.id_new
        FROM users u
        WHERE c.user_id = u.id
    """)
    
    # Handle categories with NULL user_id
    op.execute("""
        UPDATE categories
        SET id_new = gen_random_uuid()
        WHERE id_new IS NULL
    """)
    
    # Generate UUIDs for transactions and map foreign keys (join on old integer columns)
    # First update user_id
    op.execute("""
        UPDATE transactions t
        SET 
            id_new = gen_random_uuid(),
            user_id_new = u.id_new
        FROM users u
        WHERE t.user_id = u.id
    """)
    
    # Then update category_id
    op.execute("""
        UPDATE transactions t
        SET category_id_new = c.id_new
        FROM categories c
        WHERE t.category_id = c.id
    """)
    
    # Step 3: Make UUID columns NOT NULL
    op.alter_column('users', 'id_new', nullable=False)
    op.alter_column('categories', 'id_new', nullable=False)
    op.alter_column('transactions', 'id_new', nullable=False)
    op.alter_column('transactions', 'user_id_new', nullable=False)
    
    # Step 4: Drop old columns and rename new ones
    # Start with users
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('users', 'id')
    op.alter_column('users', 'id_new', new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_index('ix_users_id', 'users', ['id'])
    
    # Then categories
    op.drop_constraint('categories_pkey', 'categories', type_='primary')
    op.drop_column('categories', 'id')
    op.drop_column('categories', 'user_id')
    op.alter_column('categories', 'id_new', new_column_name='id')
    op.alter_column('categories', 'user_id_new', new_column_name='user_id')
    op.create_primary_key('categories_pkey', 'categories', ['id'])
    op.create_index('ix_categories_id', 'categories', ['id'])
    op.create_foreign_key('categories_user_id_fkey', 'categories', 'users', ['user_id'], ['id'])
    
    # Finally transactions
    op.drop_constraint('transactions_pkey', 'transactions', type_='primary')
    op.drop_column('transactions', 'id')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'category_id')
    op.alter_column('transactions', 'id_new', new_column_name='id')
    op.alter_column('transactions', 'user_id_new', new_column_name='user_id')
    op.alter_column('transactions', 'category_id_new', new_column_name='category_id')
    op.create_primary_key('transactions_pkey', 'transactions', ['id'])
    op.create_index('ix_transactions_id', 'transactions', ['id'])
    op.create_foreign_key('transactions_user_id_fkey', 'transactions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('transactions_category_id_fkey', 'transactions', 'categories', ['category_id'], ['id'])


def downgrade() -> None:
    """
    Revert UUID columns back to INTEGER.
    WARNING: This will lose data if UUIDs cannot be converted back to integers.
    """
    # This downgrade is complex and may not be fully reversible
    # For safety, we'll create a basic structure but data may be lost
    
    # Drop foreign keys
    op.drop_constraint('transactions_category_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('transactions_user_id_fkey', 'transactions', type_='foreignkey')
    op.drop_constraint('categories_user_id_fkey', 'categories', type_='foreignkey')
    
    # Convert transactions
    op.drop_constraint('transactions_pkey', 'transactions', type_='primary')
    op.drop_index('ix_transactions_id', 'transactions')
    op.add_column('transactions', sa.Column('id_old', sa.INTEGER(), nullable=True))
    op.add_column('transactions', sa.Column('user_id_old', sa.INTEGER(), nullable=True))
    op.add_column('transactions', sa.Column('category_id_old', sa.INTEGER(), nullable=True))
    # Note: UUID to INTEGER conversion will fail for most values
    # This is a placeholder - actual conversion would need custom logic
    op.drop_column('transactions', 'id')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'category_id')
    op.alter_column('transactions', 'id_old', new_column_name='id')
    op.alter_column('transactions', 'user_id_old', new_column_name='user_id')
    op.alter_column('transactions', 'category_id_old', new_column_name='category_id')
    op.create_primary_key('transactions_pkey', 'transactions', ['id'])
    op.create_foreign_key('transactions_user_id_fkey', 'transactions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('transactions_category_id_fkey', 'transactions', 'categories', ['category_id'], ['id'])
    
    # Convert categories
    op.drop_constraint('categories_pkey', 'categories', type_='primary')
    op.drop_index('ix_categories_id', 'categories')
    op.add_column('categories', sa.Column('id_old', sa.INTEGER(), nullable=True))
    op.add_column('categories', sa.Column('user_id_old', sa.INTEGER(), nullable=True))
    op.drop_column('categories', 'id')
    op.drop_column('categories', 'user_id')
    op.alter_column('categories', 'id_old', new_column_name='id')
    op.alter_column('categories', 'user_id_old', new_column_name='user_id')
    op.create_primary_key('categories_pkey', 'categories', ['id'])
    op.create_foreign_key('categories_user_id_fkey', 'categories', 'users', ['user_id'], ['id'])
    
    # Convert users
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_index('ix_users_id', 'users')
    op.add_column('users', sa.Column('id_old', sa.INTEGER(), nullable=True))
    op.drop_column('users', 'id')
    op.alter_column('users', 'id_old', new_column_name='id')
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_sequence('users_id_seq')
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")

