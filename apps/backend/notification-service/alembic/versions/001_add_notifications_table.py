"""Add notifications table

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
    """Create notifications table."""

    # Create notification_type enum
    notification_type_enum = postgresql.ENUM(
        'PROJECT_MATCH', 'TEAM_INVITE', 'MESSAGE', 'EVALUATION',
        name='notificationtype',
        create_type=False
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Key
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Notification Details
        sa.Column('notification_type', sa.Enum('PROJECT_MATCH', 'TEAM_INVITE', 'MESSAGE', 'EVALUATION', name='notificationtype'), nullable=False, index=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),

        # Related Entity
        sa.Column('related_entity_type', sa.String(length=100), nullable=True, index=True),
        sa.Column('related_entity_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('action_url', sa.Text(), nullable=True),

        # Status
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false', index=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes
    op.create_index('ix_notifications_id', 'notifications', ['id'])
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'])
    op.create_index('ix_notifications_related_entity_type', 'notifications', ['related_entity_type'])
    op.create_index('ix_notifications_related_entity_id', 'notifications', ['related_entity_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_sent_at', 'notifications', ['sent_at'])

    # Composite indexes for performance
    op.create_index('ix_notifications_user_is_read', 'notifications', ['user_id', 'is_read'])
    op.create_index('ix_notifications_user_sent_at', 'notifications', ['user_id', 'sent_at'])
    op.create_index('ix_notifications_type_is_read', 'notifications', ['notification_type', 'is_read'])


def downgrade() -> None:
    """Drop notifications table."""

    # Drop indexes
    op.drop_index('ix_notifications_type_is_read', table_name='notifications')
    op.drop_index('ix_notifications_user_sent_at', table_name='notifications')
    op.drop_index('ix_notifications_user_is_read', table_name='notifications')
    op.drop_index('ix_notifications_sent_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_related_entity_id', table_name='notifications')
    op.drop_index('ix_notifications_related_entity_type', table_name='notifications')
    op.drop_index('ix_notifications_notification_type', table_name='notifications')
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')

    # Drop table
    op.drop_table('notifications')

    # Drop enum
    sa.Enum(name='notificationtype').drop(op.get_bind(), checkfirst=True)
