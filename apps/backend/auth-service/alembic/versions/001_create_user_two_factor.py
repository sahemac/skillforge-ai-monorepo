"""Create user_two_factor table

Revision ID: 001
Revises:
Create Date: 2025-11-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_two_factor table owned by auth-service."""
    op.create_table('user_two_factor',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('secret', sa.Text(), nullable=False),
    sa.Column('backup_codes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('enabled_at', sa.DateTime(), nullable=True),
    sa.Column('last_verified_at', sa.DateTime(), nullable=True),
    sa.Column('recovery_email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_two_factor_user_id'), 'user_two_factor', ['user_id'], unique=True)


def downgrade() -> None:
    """Drop user_two_factor table."""
    op.drop_index(op.f('ix_user_two_factor_user_id'), table_name='user_two_factor')
    op.drop_table('user_two_factor')
