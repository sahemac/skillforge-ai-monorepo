"""Add company profiles table

Revision ID: 001
Revises:
Create Date: 2025-11-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create company size enum
    company_size_enum = postgresql.ENUM(
        'startup', 'small', 'medium', 'large', 'enterprise',
        name='companysize',
        create_type=False
    )
    company_size_enum.create(op.get_bind(), checkfirst=True)

    # Create industry type enum
    industry_type_enum = postgresql.ENUM(
        'technology', 'healthcare', 'finance', 'education', 'retail',
        'manufacturing', 'consulting', 'media', 'government', 'non_profit', 'other',
        name='industrytype',
        create_type=False
    )
    industry_type_enum.create(op.get_bind(), checkfirst=True)

    # Create company_profiles table
    op.create_table(
        'company_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),

        # Basic Information
        sa.Column('name', sa.String(length=200), nullable=False, index=True),
        sa.Column('slug', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),

        # Contact Information
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),

        # Address Information
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True, index=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),

        # Company Details
        sa.Column('industry', sa.Enum('technology', 'healthcare', 'finance', 'education', 'retail',
                                     'manufacturing', 'consulting', 'media', 'government', 'non_profit', 'other',
                                     name='industrytype'), nullable=True, index=True),
        sa.Column('company_size', sa.Enum('startup', 'small', 'medium', 'large', 'enterprise',
                                          name='companysize'), nullable=True),
        sa.Column('founded_year', sa.Integer(), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),

        # Social Media Links
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('twitter_url', sa.String(length=500), nullable=True),
        sa.Column('facebook_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),

        # Business Information
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('registration_number', sa.String(length=50), nullable=True),

        # SkillForge AI Specific
        sa.Column('skills_focus', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_goals', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Subscription and Billing
        sa.Column('subscription_plan', sa.String(), nullable=False, server_default='free'),
        sa.Column('subscription_status', sa.String(), nullable=False, server_default='active'),
        sa.Column('billing_email', sa.String(length=255), nullable=True),

        # Account Management
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),

        # Owner Information
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Settings and Preferences
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index('ix_company_profiles_id', 'company_profiles', ['id'])
    op.create_index('ix_company_profiles_name', 'company_profiles', ['name'])
    op.create_index('ix_company_profiles_slug', 'company_profiles', ['slug'], unique=True)
    op.create_index('ix_company_profiles_owner_id', 'company_profiles', ['owner_id'])
    op.create_index('ix_company_profiles_industry', 'company_profiles', ['industry'])
    op.create_index('ix_company_profiles_country', 'company_profiles', ['country'])
    op.create_index('ix_company_profiles_is_active', 'company_profiles', ['is_active'])

    # Create composite indexes for common queries
    op.create_index('ix_company_profiles_industry_country', 'company_profiles', ['industry', 'country'])
    op.create_index('ix_company_profiles_is_active_industry', 'company_profiles', ['is_active', 'industry'])

    # Add constraints
    op.create_check_constraint(
        'ck_company_profiles_founded_year',
        'company_profiles',
        'founded_year >= 1800 AND founded_year <= 2024'
    )
    op.create_check_constraint(
        'ck_company_profiles_employee_count',
        'company_profiles',
        'employee_count >= 0'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_company_profiles_is_active_industry', table_name='company_profiles')
    op.drop_index('ix_company_profiles_industry_country', table_name='company_profiles')
    op.drop_index('ix_company_profiles_is_active', table_name='company_profiles')
    op.drop_index('ix_company_profiles_country', table_name='company_profiles')
    op.drop_index('ix_company_profiles_industry', table_name='company_profiles')
    op.drop_index('ix_company_profiles_owner_id', table_name='company_profiles')
    op.drop_index('ix_company_profiles_slug', table_name='company_profiles')
    op.drop_index('ix_company_profiles_name', table_name='company_profiles')
    op.drop_index('ix_company_profiles_id', table_name='company_profiles')

    # Drop table
    op.drop_table('company_profiles')

    # Drop enums
    sa.Enum(name='companysize').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='industrytype').drop(op.get_bind(), checkfirst=True)
