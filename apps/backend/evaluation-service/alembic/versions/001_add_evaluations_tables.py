"""Add evaluations tables

Revision ID: 001
Revises:
Create Date: 2025-11-07

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
    """Create evaluation tables."""

    # Create evaluation_type enum
    evaluation_type_enum = postgresql.ENUM(
        'PEER', 'COMPANY', 'AI', 'SELF',
        name='evaluationtype',
        create_type=False
    )
    evaluation_type_enum.create(op.get_bind(), checkfirst=True)

    # Create evaluation_status enum
    evaluation_status_enum = postgresql.ENUM(
        'DRAFT', 'SUBMITTED', 'APPROVED',
        name='evaluationstatus',
        create_type=False
    )
    evaluation_status_enum.create(op.get_bind(), checkfirst=True)

    # Create feedback_type enum
    feedback_type_enum = postgresql.ENUM(
        'STRENGTH', 'WEAKNESS', 'IMPROVEMENT',
        name='feedbacktype',
        create_type=False
    )
    feedback_type_enum.create(op.get_bind(), checkfirst=True)

    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Keys
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('evaluated_user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('evaluator_user_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('ai_model_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),

        # Evaluation Details
        sa.Column('evaluation_type', sa.Enum('PEER', 'COMPANY', 'AI', 'SELF', name='evaluationtype'), nullable=False, index=True),
        sa.Column('overall_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('technical_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('soft_skills_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('ai_analysis', postgresql.JSONB, nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'APPROVED', name='evaluationstatus'), nullable=False, server_default='DRAFT', index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.CheckConstraint(
            'overall_score >= 0 AND overall_score <= 100',
            name='ck_evaluations_overall_score'
        ),
        sa.CheckConstraint(
            'technical_score >= 0 AND technical_score <= 100',
            name='ck_evaluations_technical_score'
        ),
        sa.CheckConstraint(
            'soft_skills_score >= 0 AND soft_skills_score <= 100',
            name='ck_evaluations_soft_skills_score'
        ),
    )

    # Create indexes on evaluations
    op.create_index('ix_evaluations_id', 'evaluations', ['id'])
    op.create_index('ix_evaluations_project_id', 'evaluations', ['project_id'])
    op.create_index('ix_evaluations_evaluated_user_id', 'evaluations', ['evaluated_user_id'])
    op.create_index('ix_evaluations_evaluator_user_id', 'evaluations', ['evaluator_user_id'])
    op.create_index('ix_evaluations_ai_model_id', 'evaluations', ['ai_model_id'])
    op.create_index('ix_evaluations_evaluation_type', 'evaluations', ['evaluation_type'])
    op.create_index('ix_evaluations_status', 'evaluations', ['status'])

    # Composite indexes for performance
    op.create_index(
        'ix_evaluations_project_evaluated_user',
        'evaluations',
        ['project_id', 'evaluated_user_id']
    )
    op.create_index(
        'ix_evaluations_type_status',
        'evaluations',
        ['evaluation_type', 'status']
    )

    # Create evaluation_criteria table
    op.create_table(
        'evaluation_criteria',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Key
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Criteria Details
        sa.Column('criterion_name', sa.String(length=200), nullable=False),
        sa.Column('score', sa.DECIMAL(4, 2), nullable=False),
        sa.Column('weight', sa.DECIMAL(4, 2), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Constraints
        sa.CheckConstraint(
            'score >= 0 AND score <= 10',
            name='ck_evaluation_criteria_score'
        ),
        sa.CheckConstraint(
            'weight IS NULL OR (weight >= 0 AND weight <= 100)',
            name='ck_evaluation_criteria_weight'
        ),
    )

    # Create indexes on evaluation_criteria
    op.create_index('ix_evaluation_criteria_id', 'evaluation_criteria', ['id'])
    op.create_index('ix_evaluation_criteria_evaluation_id', 'evaluation_criteria', ['evaluation_id'])
    op.create_index('ix_evaluation_criteria_criterion_name', 'evaluation_criteria', ['criterion_name'])

    # Create evaluation_feedback table
    op.create_table(
        'evaluation_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Key
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Feedback Details
        sa.Column('feedback_type', sa.Enum('STRENGTH', 'WEAKNESS', 'IMPROVEMENT', name='feedbacktype'), nullable=False, index=True),
        sa.Column('feedback_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True, index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes on evaluation_feedback
    op.create_index('ix_evaluation_feedback_id', 'evaluation_feedback', ['id'])
    op.create_index('ix_evaluation_feedback_evaluation_id', 'evaluation_feedback', ['evaluation_id'])
    op.create_index('ix_evaluation_feedback_feedback_type', 'evaluation_feedback', ['feedback_type'])
    op.create_index('ix_evaluation_feedback_category', 'evaluation_feedback', ['category'])

    # Composite indexes for performance
    op.create_index(
        'ix_evaluation_feedback_evaluation_type',
        'evaluation_feedback',
        ['evaluation_id', 'feedback_type']
    )


def downgrade() -> None:
    """Drop evaluation tables."""

    # Drop evaluation_feedback indexes
    op.drop_index('ix_evaluation_feedback_evaluation_type', table_name='evaluation_feedback')
    op.drop_index('ix_evaluation_feedback_category', table_name='evaluation_feedback')
    op.drop_index('ix_evaluation_feedback_feedback_type', table_name='evaluation_feedback')
    op.drop_index('ix_evaluation_feedback_evaluation_id', table_name='evaluation_feedback')
    op.drop_index('ix_evaluation_feedback_id', table_name='evaluation_feedback')

    # Drop evaluation_criteria indexes
    op.drop_index('ix_evaluation_criteria_criterion_name', table_name='evaluation_criteria')
    op.drop_index('ix_evaluation_criteria_evaluation_id', table_name='evaluation_criteria')
    op.drop_index('ix_evaluation_criteria_id', table_name='evaluation_criteria')

    # Drop evaluations indexes
    op.drop_index('ix_evaluations_type_status', table_name='evaluations')
    op.drop_index('ix_evaluations_project_evaluated_user', table_name='evaluations')
    op.drop_index('ix_evaluations_status', table_name='evaluations')
    op.drop_index('ix_evaluations_evaluation_type', table_name='evaluations')
    op.drop_index('ix_evaluations_ai_model_id', table_name='evaluations')
    op.drop_index('ix_evaluations_evaluator_user_id', table_name='evaluations')
    op.drop_index('ix_evaluations_evaluated_user_id', table_name='evaluations')
    op.drop_index('ix_evaluations_project_id', table_name='evaluations')
    op.drop_index('ix_evaluations_id', table_name='evaluations')

    # Drop tables
    op.drop_table('evaluation_feedback')
    op.drop_table('evaluation_criteria')
    op.drop_table('evaluations')

    # Drop enums
    sa.Enum(name='feedbacktype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='evaluationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='evaluationtype').drop(op.get_bind(), checkfirst=True)
