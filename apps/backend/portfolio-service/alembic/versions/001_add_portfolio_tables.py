"""Add portfolio tables

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
    """Create portfolio tables."""

    # Create portfolio_item_type enum
    portfolio_item_type_enum = postgresql.ENUM(
        'PROJECT', 'CERTIFICATION', 'AWARD', 'PUBLICATION',
        name='portfolioitemtype',
        create_type=False
    )
    portfolio_item_type_enum.create(op.get_bind(), checkfirst=True)

    # Create portfolios table
    op.create_table(
        'portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Key (1:1 with users)
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True, index=True),

        # Profile Information
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('profile_picture_url', sa.Text(), nullable=True),

        # Social Links
        sa.Column('github_url', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),
        sa.Column('website_url', sa.Text(), nullable=True),

        # Portfolio Settings
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true', index=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.CheckConstraint(
            'view_count >= 0',
            name='ck_portfolios_view_count'
        ),
    )

    # Create indexes on portfolios
    op.create_index('ix_portfolios_id', 'portfolios', ['id'])
    op.create_index('ix_portfolios_user_id', 'portfolios', ['user_id'], unique=True)
    op.create_index('ix_portfolios_is_public', 'portfolios', ['is_public'])

    # Create portfolio_items table
    op.create_table(
        'portfolio_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Keys
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),

        # Item Details
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('PROJECT', 'CERTIFICATION', 'AWARD', 'PUBLICATION', name='portfolioitemtype'), nullable=False, index=True),

        # URLs and Media
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),

        # Metadata
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false', index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes on portfolio_items
    op.create_index('ix_portfolio_items_id', 'portfolio_items', ['id'])
    op.create_index('ix_portfolio_items_portfolio_id', 'portfolio_items', ['portfolio_id'])
    op.create_index('ix_portfolio_items_project_id', 'portfolio_items', ['project_id'])
    op.create_index('ix_portfolio_items_type', 'portfolio_items', ['type'])
    op.create_index('ix_portfolio_items_is_featured', 'portfolio_items', ['is_featured'])

    # Composite indexes for performance
    op.create_index(
        'ix_portfolio_items_portfolio_featured',
        'portfolio_items',
        ['portfolio_id', 'is_featured']
    )
    op.create_index(
        'ix_portfolio_items_portfolio_type',
        'portfolio_items',
        ['portfolio_id', 'type']
    )

    # Create portfolio_skills table
    op.create_table(
        'portfolio_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Keys
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('skill_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Display Settings
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('is_highlighted', sa.Boolean(), nullable=False, server_default='false', index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),

        # Constraints
        sa.UniqueConstraint('portfolio_id', 'skill_id', name='uq_portfolio_skills_portfolio_skill'),
    )

    # Create indexes on portfolio_skills
    op.create_index('ix_portfolio_skills_id', 'portfolio_skills', ['id'])
    op.create_index('ix_portfolio_skills_portfolio_id', 'portfolio_skills', ['portfolio_id'])
    op.create_index('ix_portfolio_skills_skill_id', 'portfolio_skills', ['skill_id'])
    op.create_index('ix_portfolio_skills_is_highlighted', 'portfolio_skills', ['is_highlighted'])

    # Composite indexes for performance
    op.create_index(
        'ix_portfolio_skills_portfolio_order',
        'portfolio_skills',
        ['portfolio_id', 'display_order']
    )


def downgrade() -> None:
    """Drop portfolio tables."""

    # Drop portfolio_skills indexes
    op.drop_index('ix_portfolio_skills_portfolio_order', table_name='portfolio_skills')
    op.drop_index('ix_portfolio_skills_is_highlighted', table_name='portfolio_skills')
    op.drop_index('ix_portfolio_skills_skill_id', table_name='portfolio_skills')
    op.drop_index('ix_portfolio_skills_portfolio_id', table_name='portfolio_skills')
    op.drop_index('ix_portfolio_skills_id', table_name='portfolio_skills')

    # Drop portfolio_items indexes
    op.drop_index('ix_portfolio_items_portfolio_type', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_portfolio_featured', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_is_featured', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_type', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_project_id', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_portfolio_id', table_name='portfolio_items')
    op.drop_index('ix_portfolio_items_id', table_name='portfolio_items')

    # Drop portfolios indexes
    op.drop_index('ix_portfolios_is_public', table_name='portfolios')
    op.drop_index('ix_portfolios_user_id', table_name='portfolios')
    op.drop_index('ix_portfolios_id', table_name='portfolios')

    # Drop tables
    op.drop_table('portfolio_skills')
    op.drop_table('portfolio_items')
    op.drop_table('portfolios')

    # Drop enums
    sa.Enum(name='portfolioitemtype').drop(op.get_bind(), checkfirst=True)
