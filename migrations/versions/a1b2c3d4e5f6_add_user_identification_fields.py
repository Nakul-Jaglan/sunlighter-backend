"""Add user identification fields

Revision ID: a1b2c3d4e5f6
Revises: 197ff6ce9f91
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '197ff6ce9f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user identification fields to users table."""
    # Use raw SQL to safely add columns if they don't exist
    connection = op.get_bind()
    
    # Check if columns exist and add them if they don't
    print("🔍 Checking for existing columns...")
    
    # Add user_id column if it doesn't exist
    try:
        connection.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='user_id') THEN
                    ALTER TABLE users ADD COLUMN user_id VARCHAR;
                    RAISE NOTICE 'Added user_id column';
                ELSE
                    RAISE NOTICE 'user_id column already exists';
                END IF;
            END $$;
        """))
    except Exception as e:
        print(f"⚠️ Warning adding user_id: {e}")
    
    # Add company_handle column if it doesn't exist
    try:
        connection.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='company_handle') THEN
                    ALTER TABLE users ADD COLUMN company_handle VARCHAR;
                    RAISE NOTICE 'Added company_handle column';
                ELSE
                    RAISE NOTICE 'company_handle column already exists';
                END IF;
            END $$;
        """))
    except Exception as e:
        print(f"⚠️ Warning adding company_handle: {e}")
    
    # Add employer_id column if it doesn't exist
    try:
        connection.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='users' AND column_name='employer_id') THEN
                    ALTER TABLE users ADD COLUMN employer_id INTEGER;
                    RAISE NOTICE 'Added employer_id column';
                ELSE
                    RAISE NOTICE 'employer_id column already exists';
                END IF;
            END $$;
        """))
    except Exception as e:
        print(f"⚠️ Warning adding employer_id: {e}")
    
    # Create indexes if they don't exist
    try:
        connection.execute(text("""
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_users_user_id 
            ON users (user_id) WHERE user_id IS NOT NULL;
        """))
        print("✅ Created/verified user_id index")
    except Exception as e:
        print(f"⚠️ Warning creating user_id index: {e}")
    
    try:
        connection.execute(text("""
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_users_company_handle 
            ON users (company_handle) WHERE company_handle IS NOT NULL;
        """))
        print("✅ Created/verified company_handle index")
    except Exception as e:
        print(f"⚠️ Warning creating company_handle index: {e}")
    
    try:
        connection.execute(text("""
            CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_users_employer_id 
            ON users (employer_id) WHERE employer_id IS NOT NULL;
        """))
        print("✅ Created/verified employer_id index")
    except Exception as e:
        print(f"⚠️ Warning creating employer_id index: {e}")
    
    print("🎉 Migration completed successfully!")


def downgrade() -> None:
    """Remove user identification fields from users table."""
    # Use raw SQL for safe removal
    connection = op.get_bind()
    
    # Drop indexes first
    try:
        connection.execute(text("DROP INDEX IF EXISTS idx_users_employer_id;"))
        connection.execute(text("DROP INDEX IF EXISTS idx_users_company_handle;"))
        connection.execute(text("DROP INDEX IF EXISTS idx_users_user_id;"))
    except Exception as e:
        print(f"⚠️ Warning dropping indexes: {e}")
    
    # Drop columns
    try:
        connection.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS employer_id;"))
        connection.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS company_handle;"))
        connection.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS user_id;"))
    except Exception as e:
        print(f"⚠️ Warning dropping columns: {e}")
