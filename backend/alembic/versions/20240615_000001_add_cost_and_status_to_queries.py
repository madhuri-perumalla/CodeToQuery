"""Add cost and status fields to extracted_queries

Revision ID: 002
Revises: 001
Create Date: 2024-06-15 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add cost column
    op.add_column('extracted_queries', sa.Column('cost', sa.Numeric(precision=20, scale=2), nullable=True))
    op.create_index('idx_queries_cost', 'extracted_queries', ['cost'])
    
    # Add execution_time column
    op.add_column('extracted_queries', sa.Column('execution_time', sa.Numeric(precision=10, scale=2), nullable=True))
    
    # Add health_score column
    op.add_column('extracted_queries', sa.Column('health_score', sa.Integer(), nullable=True))
    
    # Add status column with enum
    query_status_enum = postgresql.ENUM('healthy', 'warning', 'critical', 'analyzing', name='query_status', create_type=True)
    query_status_enum.create(op.get_bind())
    op.add_column('extracted_queries', sa.Column('status', query_status_enum, nullable=True, server_default='analyzing'))
    op.create_index('idx_queries_status', 'extracted_queries', ['status'])
    
    # Add updated_at column
    op.add_column('extracted_queries', sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_index('idx_queries_status', table_name='extracted_queries')
    op.drop_column('extracted_queries', 'status')
    
    op.drop_column('extracted_queries', 'health_score')
    op.drop_column('extracted_queries', 'execution_time')
    
    op.drop_index('idx_queries_cost', table_name='extracted_queries')
    op.drop_column('extracted_queries', 'cost')
    
    op.drop_column('extracted_queries', 'updated_at')
    
    op.execute('DROP TYPE IF EXISTS query_status')
