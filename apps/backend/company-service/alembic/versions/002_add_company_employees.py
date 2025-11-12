"""Add company employees table

Revision ID: 002
Revises: 001
Create Date: 2025-11-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create company_employees table."""

    # Create company_employees table
    op.create_table(
        'company_employees',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_post_projects', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_manage_employees', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_review_applications', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('can_view_analytics', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_manage_billing', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(50), nullable=False, server_default='ACTIVE'),
        sa.Column('employment_type', sa.String(50), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notification_email', sa.String(255), nullable=True),
        sa.Column('receive_application_alerts', sa.Boolean(), server_default='true'),
        sa.Column('invited_by_user_id', UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint('company_id', 'user_id', name='uq_company_employees_company_user'),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'LEFT')",
            name='ck_company_employees_status'
        ),
        sa.CheckConstraint(
            "employment_type IS NULL OR employment_type IN ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERN')",
            name='ck_company_employees_employment_type'
        ),
    )

    # Create indexes on company_employees
    op.create_index('ix_company_employees_company_id', 'company_employees', ['company_id'])
    op.create_index('ix_company_employees_user_id', 'company_employees', ['user_id'])
    op.create_index('ix_company_employees_role', 'company_employees', ['role'])
    op.create_index('ix_company_employees_status', 'company_employees', ['status'])
    op.create_index('ix_company_employees_is_admin', 'company_employees', ['is_admin'])

    # Create composite indexes for performance
    op.create_index(
        'ix_company_employees_company_status',
        'company_employees',
        ['company_id', 'status']
    )


def downgrade() -> None:
    """Drop company_employees table."""

    # Drop indexes
    op.drop_index('ix_company_employees_company_status')
    op.drop_index('ix_company_employees_is_admin')
    op.drop_index('ix_company_employees_status')
    op.drop_index('ix_company_employees_role')
    op.drop_index('ix_company_employees_user_id')
    op.drop_index('ix_company_employees_company_id')

    # Drop table
    op.drop_table('company_employees')
