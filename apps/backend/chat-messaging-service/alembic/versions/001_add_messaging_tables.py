"""Add messaging tables

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
    """Create messaging tables."""

    # Create conversation_type enum
    conversation_type_enum = postgresql.ENUM(
        'PROJECT', 'TEAM', 'DIRECT',
        name='conversationtype',
        create_type=False
    )
    conversation_type_enum.create(op.get_bind(), checkfirst=True)

    # Create message_type enum
    message_type_enum = postgresql.ENUM(
        'TEXT', 'IMAGE', 'FILE', 'SYSTEM',
        name='messagetype',
        create_type=False
    )
    message_type_enum.create(op.get_bind(), checkfirst=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Keys
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),

        # Conversation Details
        sa.Column('conversation_type', sa.Enum('PROJECT', 'TEAM', 'DIRECT', name='conversationtype'), nullable=False, index=True),
        sa.Column('title', sa.String(length=200), nullable=True),

        # Status
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false', index=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes on conversations
    op.create_index('ix_conversations_id', 'conversations', ['id'])
    op.create_index('ix_conversations_project_id', 'conversations', ['project_id'])
    op.create_index('ix_conversations_created_by_user_id', 'conversations', ['created_by_user_id'])
    op.create_index('ix_conversations_conversation_type', 'conversations', ['conversation_type'])
    op.create_index('ix_conversations_last_message_at', 'conversations', ['last_message_at'])
    op.create_index('ix_conversations_is_archived', 'conversations', ['is_archived'])

    # Composite indexes for performance
    op.create_index(
        'ix_conversations_type_archived',
        'conversations',
        ['conversation_type', 'is_archived']
    )
    op.create_index(
        'ix_conversations_project_archived',
        'conversations',
        ['project_id', 'is_archived']
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text('gen_random_uuid()')),

        # Foreign Keys
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('sender_user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('reply_to_message_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),

        # Message Content
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('message_type', sa.Enum('TEXT', 'IMAGE', 'FILE', 'SYSTEM', name='messagetype'), nullable=False, index=True),

        # Edit Tracking
        sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),

        # Timestamps
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create indexes on messages
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_sender_user_id', 'messages', ['sender_user_id'])
    op.create_index('ix_messages_reply_to_message_id', 'messages', ['reply_to_message_id'])
    op.create_index('ix_messages_message_type', 'messages', ['message_type'])
    op.create_index('ix_messages_sent_at', 'messages', ['sent_at'])

    # Composite indexes for performance
    op.create_index(
        'ix_messages_conversation_sent_at',
        'messages',
        ['conversation_id', 'sent_at']
    )
    op.create_index(
        'ix_messages_sender_sent_at',
        'messages',
        ['sender_user_id', 'sent_at']
    )


def downgrade() -> None:
    """Drop messaging tables."""

    # Drop messages indexes
    op.drop_index('ix_messages_sender_sent_at', table_name='messages')
    op.drop_index('ix_messages_conversation_sent_at', table_name='messages')
    op.drop_index('ix_messages_sent_at', table_name='messages')
    op.drop_index('ix_messages_message_type', table_name='messages')
    op.drop_index('ix_messages_reply_to_message_id', table_name='messages')
    op.drop_index('ix_messages_sender_user_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_index('ix_messages_id', table_name='messages')

    # Drop conversations indexes
    op.drop_index('ix_conversations_project_archived', table_name='conversations')
    op.drop_index('ix_conversations_type_archived', table_name='conversations')
    op.drop_index('ix_conversations_is_archived', table_name='conversations')
    op.drop_index('ix_conversations_last_message_at', table_name='conversations')
    op.drop_index('ix_conversations_conversation_type', table_name='conversations')
    op.drop_index('ix_conversations_created_by_user_id', table_name='conversations')
    op.drop_index('ix_conversations_project_id', table_name='conversations')
    op.drop_index('ix_conversations_id', table_name='conversations')

    # Drop tables
    op.drop_table('messages')
    op.drop_table('conversations')

    # Drop enums
    sa.Enum(name='messagetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='conversationtype').drop(op.get_bind(), checkfirst=True)
