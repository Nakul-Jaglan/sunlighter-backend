"""Add user identification fields

Revision ID: a1b2c3d4e5f6
Revises: 197ff6ce9f91
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '197ff6ce9f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user identification fields to users table."""
    # Add new columns to users table
    op.add_column('users', sa.Column('user_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('company_handle', sa.String(), nullable=True))
    op.add_column('users', sa.Column('employer_id', sa.Integer(), nullable=True))
    
    # Create indexes for the new columns
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)
    op.create_index(op.f('ix_users_company_handle'), 'users', ['company_handle'], unique=True)
    op.create_index(op.f('ix_users_employer_id'), 'users', ['employer_id'], unique=True)


def downgrade() -> None:
    """Remove user identification fields from users table."""
    # Drop indexes first
    op.drop_index(op.f('ix_users_employer_id'), table_name='users')
    op.drop_index(op.f('ix_users_company_handle'), table_name='users')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    
    # Drop columns
    op.drop_column('users', 'employer_id')
    op.drop_column('users', 'company_handle')
    op.drop_column('users', 'user_id')
