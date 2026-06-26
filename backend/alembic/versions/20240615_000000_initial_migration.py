"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-06-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_projects_name', 'projects', ['name'])
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])

    # Create codebases table
    op.create_table(
        'codebases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('scan_path', sa.String(length=1024), nullable=False),
        sa.Column('scanned_at', sa.DateTime(), nullable=False),
        sa.Column('file_count', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'scanning', 'completed', 'failed', name='codebase_status'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_codebases_project_id', 'codebases', ['project_id'])
    op.create_index('idx_codebases_status', 'codebases', ['status'])
    op.create_index('idx_codebases_scanned_at', 'codebases', ['scanned_at'])

    # Create extracted_queries table
    op.create_table(
        'extracted_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codebase_id', sa.Integer(), nullable=False),
        sa.Column('raw_sql', sa.Text(), nullable=False),
        sa.Column('normalized_sql', sa.Text(), nullable=False),
        sa.Column('query_hash', sa.String(length=64), nullable=False),
        sa.Column('dialect', sa.String(length=50), nullable=False),
        sa.Column('query_type', sa.Enum('select', 'insert', 'update', 'delete', 'other', name='query_type'), nullable=True),
        sa.Column('source_type', sa.Enum('raw_sql', 'orm_sequelize', 'orm_typeorm', 'orm_sqlalchemy', 'orm_django', 'orm_prisma', name='source_type'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['codebase_id'], ['codebases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_queries_codebase_id', 'extracted_queries', ['codebase_id'])
    op.create_index('idx_queries_query_hash', 'extracted_queries', ['query_hash'])
    op.create_index('idx_queries_query_type', 'extracted_queries', ['query_type'])
    op.create_index('idx_queries_source_type', 'extracted_queries', ['source_type'])
    op.create_index('idx_queries_created_at', 'extracted_queries', ['created_at'])

    # Create query_locations table
    op.create_table(
        'query_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('column_number', sa.Integer(), nullable=False),
        sa.Column('function_name', sa.String(length=255), nullable=True),
        sa.Column('class_name', sa.String(length=255), nullable=True),
        sa.Column('context_snippet', sa.Text(), nullable=True),
        sa.Column('call_stack', postgresql.JSON(), nullable=False),
        sa.CheckConstraint('line_number > 0', name='valid_line_number'),
        sa.CheckConstraint('column_number >= 0', name='valid_column_number'),
        sa.ForeignKeyConstraint(['query_id'], ['extracted_queries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_locations_query_id', 'query_locations', ['query_id'])
    op.create_index('idx_locations_file_path', 'query_locations', ['file_path'])
    op.create_index('idx_locations_line_number', 'query_locations', ['line_number'])

    # Create execution_plans table
    op.create_table(
        'execution_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_id', sa.Integer(), nullable=False),
        sa.Column('plan_json', postgresql.JSON(), nullable=False),
        sa.Column('plan_hash', sa.String(length=64), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('total_rows', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('plan_width', sa.Integer(), nullable=True),
        sa.Column('format', sa.Enum('json', 'text', 'xml', name='plan_format'), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False),
        sa.Column('execution_time_ms', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['query_id'], ['extracted_queries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_id')
    )
    op.create_index('idx_plans_query_id', 'execution_plans', ['query_id'])
    op.create_index('idx_plans_plan_hash', 'execution_plans', ['plan_hash'])
    op.create_index('idx_plans_total_cost', 'execution_plans', ['total_cost'])
    op.create_index('idx_plans_analyzed_at', 'execution_plans', ['analyzed_at'])

    # Create diagnostics table
    op.create_table(
        'diagnostics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.Enum('critical', 'warning', 'info', name='severity'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('location', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['execution_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_diagnostics_plan_id', 'diagnostics', ['plan_id'])
    op.create_index('idx_diagnostics_rule_id', 'diagnostics', ['rule_id'])
    op.create_index('idx_diagnostics_severity', 'diagnostics', ['severity'])
    op.create_index('idx_diagnostics_created_at', 'diagnostics', ['created_at'])

    # Create fix_suggestions table
    op.create_table(
        'fix_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('diagnostic_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', sa.Enum('add_index', 'rewrite_query', 'add_filter', 'change_join_order', name='suggestion_type'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('sql_change', sa.Text(), nullable=True),
        sa.Column('impact_estimate', sa.Enum('high', 'medium', 'low', name='impact_estimate'), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='valid_confidence_score'),
        sa.ForeignKeyConstraint(['diagnostic_id'], ['diagnostics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_suggestions_diagnostic_id', 'fix_suggestions', ['diagnostic_id'])
    op.create_index('idx_suggestions_type', 'fix_suggestions', ['suggestion_type'])
    op.create_index('idx_suggestions_impact', 'fix_suggestions', ['impact_estimate'])

    # Create query_groups table
    op.create_table(
        'query_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codebase_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('pattern_signature', sa.String(length=255), nullable=False),
        sa.Column('query_count', sa.Integer(), nullable=False),
        sa.Column('max_cost', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('avg_cost', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('similarity_threshold', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('similarity_threshold >= 0 AND similarity_threshold <= 1', name='valid_similarity_threshold'),
        sa.ForeignKeyConstraint(['codebase_id'], ['codebases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_groups_codebase_id', 'query_groups', ['codebase_id'])
    op.create_index('idx_groups_pattern_signature', 'query_groups', ['pattern_signature'])
    op.create_index('idx_groups_query_count', 'query_groups', ['query_count'])
    op.create_index('idx_groups_max_cost', 'query_groups', ['max_cost'])

    # Create group_members table
    op.create_table(
        'group_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('query_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('is_representative', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('similarity_score >= 0 AND similarity_score <= 1', name='valid_similarity_score'),
        sa.ForeignKeyConstraint(['group_id'], ['query_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['query_id'], ['extracted_queries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'query_id', name='uq_group_query')
    )
    op.create_index('idx_group_members_group_id', 'group_members', ['group_id'])
    op.create_index('idx_group_members_query_id', 'group_members', ['query_id'])
    op.create_index('idx_group_members_similarity', 'group_members', ['similarity_score'])

    # Create analysis_runs table
    op.create_table(
        'analysis_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codebase_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='analysis_status'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['codebase_id'], ['codebases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_analysis_runs_codebase_id', 'analysis_runs', ['codebase_id'])
    op.create_index('idx_analysis_runs_status', 'analysis_runs', ['status'])
    op.create_index('idx_analysis_runs_started_at', 'analysis_runs', ['started_at'])


def downgrade() -> None:
    op.drop_index('idx_analysis_runs_started_at', table_name='analysis_runs')
    op.drop_index('idx_analysis_runs_status', table_name='analysis_runs')
    op.drop_index('idx_analysis_runs_codebase_id', table_name='analysis_runs')
    op.drop_table('analysis_runs')

    op.drop_index('idx_group_members_similarity', table_name='group_members')
    op.drop_index('idx_group_members_query_id', table_name='group_members')
    op.drop_index('idx_group_members_group_id', table_name='group_members')
    op.drop_table('group_members')

    op.drop_index('idx_groups_max_cost', table_name='query_groups')
    op.drop_index('idx_groups_query_count', table_name='query_groups')
    op.drop_index('idx_groups_pattern_signature', table_name='query_groups')
    op.drop_index('idx_groups_codebase_id', table_name='query_groups')
    op.drop_table('query_groups')

    op.drop_index('idx_suggestions_impact', table_name='fix_suggestions')
    op.drop_index('idx_suggestions_type', table_name='fix_suggestions')
    op.drop_index('idx_suggestions_diagnostic_id', table_name='fix_suggestions')
    op.drop_table('fix_suggestions')

    op.drop_index('idx_diagnostics_created_at', table_name='diagnostics')
    op.drop_index('idx_diagnostics_severity', table_name='diagnostics')
    op.drop_index('idx_diagnostics_rule_id', table_name='diagnostics')
    op.drop_index('idx_diagnostics_plan_id', table_name='diagnostics')
    op.drop_table('diagnostics')

    op.drop_index('idx_plans_analyzed_at', table_name='execution_plans')
    op.drop_index('idx_plans_total_cost', table_name='execution_plans')
    op.drop_index('idx_plans_plan_hash', table_name='execution_plans')
    op.drop_index('idx_plans_query_id', table_name='execution_plans')
    op.drop_table('execution_plans')

    op.drop_index('idx_locations_line_number', table_name='query_locations')
    op.drop_index('idx_locations_file_path', table_name='query_locations')
    op.drop_index('idx_locations_query_id', table_name='query_locations')
    op.drop_table('query_locations')

    op.drop_index('idx_queries_created_at', table_name='extracted_queries')
    op.drop_index('idx_queries_source_type', table_name='extracted_queries')
    op.drop_index('idx_queries_query_type', table_name='extracted_queries')
    op.drop_index('idx_queries_query_hash', table_name='extracted_queries')
    op.drop_index('idx_queries_codebase_id', table_name='extracted_queries')
    op.drop_table('extracted_queries')

    op.drop_index('idx_codebases_scanned_at', table_name='codebases')
    op.drop_index('idx_codebases_status', table_name='codebases')
    op.drop_index('idx_codebases_project_id', table_name='codebases')
    op.drop_table('codebases')

    op.drop_index('idx_projects_created_at', table_name='projects')
    op.drop_index('idx_projects_name', table_name='projects')
    op.drop_table('projects')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS analysis_status')
    op.execute('DROP TYPE IF EXISTS similarity_threshold')
    op.execute('DROP TYPE IF EXISTS valid_similarity_score')
    op.execute('DROP TYPE IF EXISTS impact_estimate')
    op.execute('DROP TYPE IF EXISTS suggestion_type')
    op.execute('DROP TYPE IF EXISTS severity')
    op.execute('DROP TYPE IF EXISTS plan_format')
    op.execute('DROP TYPE IF EXISTS valid_confidence_score')
    op.execute('DROP TYPE IF EXISTS source_type')
    op.execute('DROP TYPE IF EXISTS query_type')
    op.execute('DROP TYPE IF EXISTS codebase_status')
