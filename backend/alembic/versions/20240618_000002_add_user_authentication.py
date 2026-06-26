"""Add user authentication

Revision ID: 003
Revises: 002
Create Date: 2024-06-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    
    # Add owner_id column to projects table
    # First, make it nullable to handle existing data
    op.add_column('projects', sa.Column('owner_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_projects_owner_id_users', 
        'projects', 
        'users', 
        ['owner_id'], 
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create index on owner_id
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])
    
    # For existing projects, we need to set a default owner
    # This will be handled by a data migration script or manually
    # For now, we'll make owner_id nullable to allow existing projects
    
    # Note: In production, you should run a data migration to assign
    # existing projects to a default user before making owner_id non-nullable


def downgrade() -> None:
    # Remove owner_id from projects table
    op.drop_index('ix_projects_owner_id', table_name='projects')
    op.drop_constraint('fk_projects_owner_id_users', 'projects', type_='foreignkey')
    op.drop_column('projects', 'owner_id')
    
    # Drop users table
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
