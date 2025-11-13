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
    # Create table without FK constraint first
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
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_two_factor_user_id'), 'user_two_factor', ['user_id'], unique=True)

    # Conditionally add FK constraint only if users table exists
    # This allows the migration to run in test environments where users table might not exist
    # Using EXCEPTION block to gracefully handle the case where users table doesn't exist
    op.execute("""
        DO $$
        BEGIN
            ALTER TABLE user_two_factor
            ADD CONSTRAINT user_two_factor_user_id_fkey
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
        EXCEPTION
            WHEN undefined_table THEN
                -- Silently ignore if users table doesn't exist (e.g., in test environment)
                NULL;
        END $$;
    """)


def downgrade() -> None:
    """Drop user_two_factor table."""
    # Drop FK constraint if it exists - using EXCEPTION to handle gracefully
    op.execute("""
        DO $$
        BEGIN
            ALTER TABLE user_two_factor DROP CONSTRAINT user_two_factor_user_id_fkey;
        EXCEPTION
            WHEN undefined_object THEN
                -- Silently ignore if constraint doesn't exist
                NULL;
        END $$;
    """)

    op.drop_index(op.f('ix_user_two_factor_user_id'), table_name='user_two_factor')
    op.drop_table('user_two_factor')
