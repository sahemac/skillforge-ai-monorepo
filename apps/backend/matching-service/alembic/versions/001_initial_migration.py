"""Initial migration for matching service

Revision ID: 001
Revises:
Create Date: 2024-09-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables for matching service."""

    # Create matching_profiles table
    op.create_table(
        'matching_profiles',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('user_type', sa.String(), nullable=False),
        sa.Column('profile_data', JSON(), nullable=False),
        sa.Column('skills', JSON(), nullable=False),
        sa.Column('interests', JSON(), nullable=False),
        sa.Column('experience_level', sa.String(), nullable=True),
        sa.Column('preferred_location', sa.String(), nullable=True),
        sa.Column('preferred_work_mode', sa.String(), nullable=True),
        sa.Column('salary_expectations', JSON(), nullable=True),
        sa.Column('skills_embedding', JSON(), nullable=True),
        sa.Column('profile_embedding', JSON(), nullable=True),
        sa.Column('matching_radius_km', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('profile_completeness_score', sa.Float(), nullable=False),
        sa.Column('last_activity', sa.String(), nullable=True),
    )

    # Create indexes on matching_profiles
    op.create_index('ix_matching_profiles_user_id', 'matching_profiles', ['user_id'])
    op.create_index('ix_matching_profiles_user_type', 'matching_profiles', ['user_type'])
    op.create_index('ix_matching_profiles_is_active', 'matching_profiles', ['is_active'])
    op.create_index('ix_matching_profiles_experience_level', 'matching_profiles', ['experience_level'])

    # Create match_results table
    op.create_table(
        'match_results',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('matching_type', sa.String(), nullable=False),
        sa.Column('algorithm_version', sa.String(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('skill_score', sa.Float(), nullable=True),
        sa.Column('experience_score', sa.Float(), nullable=True),
        sa.Column('location_score', sa.Float(), nullable=True),
        sa.Column('preference_score', sa.Float(), nullable=True),
        sa.Column('semantic_score', sa.Float(), nullable=True),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=False),
        sa.Column('match_reasons', JSON(), nullable=False),
        sa.Column('skill_overlaps', JSON(), nullable=False),
        sa.Column('missing_skills', JSON(), nullable=False),
        sa.Column('match_metadata', JSON(), nullable=False),
        sa.Column('computation_time_ms', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('is_mutual', sa.Boolean(), nullable=False),
        sa.Column('user_feedback', sa.String(), nullable=True),
        sa.Column('feedback_score', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )

    # Create indexes on match_results
    op.create_index('ix_match_results_user_id', 'match_results', ['user_id'])
    op.create_index('ix_match_results_target_id', 'match_results', ['target_id'])
    op.create_index('ix_match_results_matching_type', 'match_results', ['matching_type'])
    op.create_index('ix_match_results_overall_score', 'match_results', ['overall_score'])
    op.create_index('ix_match_results_is_active', 'match_results', ['is_active'])
    op.create_index('ix_match_results_created_at', 'match_results', ['created_at'])

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('profile_id', sa.String(), nullable=False),
        sa.Column('preference_type', sa.String(), nullable=False),
        sa.Column('preference_name', sa.String(), nullable=False),
        sa.Column('preference_value', JSON(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False),
        sa.Column('is_flexible', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('preference_metadata', JSON(), nullable=True),
    )

    # Create indexes on user_preferences
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    op.create_index('ix_user_preferences_profile_id', 'user_preferences', ['profile_id'])
    op.create_index('ix_user_preferences_preference_type', 'user_preferences', ['preference_type'])
    op.create_index('ix_user_preferences_is_active', 'user_preferences', ['is_active'])
    op.create_index('ix_user_preferences_priority', 'user_preferences', ['priority'])

    # Create preference_history table
    op.create_table(
        'preference_history',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('preference_id', sa.String(), nullable=False),
        sa.Column('old_value', JSON(), nullable=True),
        sa.Column('new_value', JSON(), nullable=False),
        sa.Column('change_reason', sa.String(), nullable=True),
        sa.Column('changed_by', sa.String(), nullable=True),
    )

    # Create indexes on preference_history
    op.create_index('ix_preference_history_user_id', 'preference_history', ['user_id'])
    op.create_index('ix_preference_history_preference_id', 'preference_history', ['preference_id'])
    op.create_index('ix_preference_history_created_at', 'preference_history', ['created_at'])

    # Create composite indexes for performance
    op.create_index(
        'ix_match_results_user_target_type',
        'match_results',
        ['user_id', 'target_type', 'matching_type']
    )

    op.create_index(
        'ix_match_results_score_active',
        'match_results',
        ['overall_score', 'is_active']
    )

    op.create_index(
        'ix_user_preferences_user_type_active',
        'user_preferences',
        ['user_id', 'preference_type', 'is_active']
    )


def downgrade() -> None:
    """Drop all tables."""

    # Drop indexes first
    op.drop_index('ix_user_preferences_user_type_active')
    op.drop_index('ix_match_results_score_active')
    op.drop_index('ix_match_results_user_target_type')

    op.drop_index('ix_preference_history_created_at')
    op.drop_index('ix_preference_history_preference_id')
    op.drop_index('ix_preference_history_user_id')

    op.drop_index('ix_user_preferences_priority')
    op.drop_index('ix_user_preferences_is_active')
    op.drop_index('ix_user_preferences_preference_type')
    op.drop_index('ix_user_preferences_profile_id')
    op.drop_index('ix_user_preferences_user_id')

    op.drop_index('ix_match_results_created_at')
    op.drop_index('ix_match_results_is_active')
    op.drop_index('ix_match_results_overall_score')
    op.drop_index('ix_match_results_matching_type')
    op.drop_index('ix_match_results_target_id')
    op.drop_index('ix_match_results_user_id')

    op.drop_index('ix_matching_profiles_experience_level')
    op.drop_index('ix_matching_profiles_is_active')
    op.drop_index('ix_matching_profiles_user_type')
    op.drop_index('ix_matching_profiles_user_id')

    # Drop tables
    op.drop_table('preference_history')
    op.drop_table('user_preferences')
    op.drop_table('match_results')
    op.drop_table('matching_profiles')