"""Add deliverables management system

Revision ID: 001
Revises: 
Create Date: 2024-01-20 10:00:00.000000

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
    """Create deliverables management tables."""
    
    # Create enum types
    op.execute("""
        CREATE TYPE deliverable_type_enum AS ENUM (
            'FILE_UPLOAD', 
            'GIT_REPO_URL', 
            'EXTERNAL_URL'
        )
    """)
    
    op.execute("""
        CREATE TYPE deliverable_status_enum AS ENUM (
            'draft',
            'submitted', 
            'under_review',
            'approved',
            'rejected',
            'revision_requested'
        )
    """)
    
    op.execute("""
        CREATE TYPE project_status_enum AS ENUM (
            'draft',
            'planning',
            'active',
            'on_hold', 
            'completed',
            'cancelled',
            'archived'
        )
    """)
    
    op.execute("""
        CREATE TYPE project_priority_enum AS ENUM (
            'low',
            'medium',
            'high',
            'critical'
        )
    """)
    
    op.execute("""
        CREATE TYPE project_type_enum AS ENUM (
            'learning',
            'development',
            'research',
            'training',
            'certification',
            'internal',
            'client',
            'other'
        )
    """)
    
    op.execute("""
        CREATE TYPE project_role_enum AS ENUM (
            'owner',
            'manager', 
            'lead',
            'member',
            'contributor',
            'viewer'
        )
    """)
    
    op.execute("""
        CREATE TYPE task_status_enum AS ENUM (
            'todo',
            'in_progress',
            'in_review',
            'blocked',
            'completed',
            'cancelled'
        )
    """)
    
    op.execute("""
        CREATE TYPE task_priority_enum AS ENUM (
            'low',
            'medium', 
            'high',
            'urgent'
        )
    """)
    
    op.execute("""
        CREATE TYPE milestone_status_enum AS ENUM (
            'upcoming',
            'in_progress',
            'completed',
            'delayed',
            'cancelled'
        )
    """)
    
    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('short_description', sa.String(length=500), nullable=True),
        sa.Column('project_type', postgresql.ENUM('learning', 'development', 'research', 'training', 'certification', 'internal', 'client', 'other', name='project_type_enum'), nullable=False, default='learning'),
        sa.Column('status', postgresql.ENUM('draft', 'planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived', name='project_status_enum'), nullable=False, default='draft'),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'critical', name='project_priority_enum'), nullable=False, default='medium'),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date, nullable=True),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('estimated_hours', sa.Integer, nullable=True),
        sa.Column('actual_hours', sa.Integer, nullable=True, default=0),
        sa.Column('budget', sa.Float, nullable=True),
        sa.Column('actual_cost', sa.Float, nullable=True, default=0),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('progress_percentage', sa.Integer, nullable=False, default=0),
        sa.Column('completed_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('total_tasks', sa.Integer, nullable=False, default=0),
        sa.Column('skills_required', postgresql.JSON, nullable=True, default=[]),
        sa.Column('skills_learned', postgresql.JSON, nullable=True, default=[]),
        sa.Column('tags', postgresql.JSON, nullable=True, default=[]),
        sa.Column('is_public', sa.Boolean, nullable=False, default=False),
        sa.Column('visibility', sa.String(length=50), nullable=False, default='company'),
        sa.Column('metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('project_settings', postgresql.JSON, nullable=True, default={}),
        sa.Column('external_project_id', sa.String(length=100), nullable=True),
        sa.Column('repository_url', sa.String(length=500), nullable=True),
        sa.Column('documentation_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )
    
    # Create indexes for projects
    op.create_index('idx_projects_company_status', 'projects', ['company_id', 'status'])
    op.create_index('idx_projects_company_active', 'projects', ['company_id', 'is_active'])
    op.create_index('idx_projects_created_by_status', 'projects', ['created_by', 'status'])
    op.create_index('idx_projects_type_status', 'projects', ['project_type', 'status'])
    op.create_index('idx_projects_priority_status', 'projects', ['priority', 'status'])
    op.create_index('idx_projects_visibility_public', 'projects', ['visibility', 'is_public'])
    op.create_index('idx_projects_name', 'projects', ['name'])
    op.create_index('idx_projects_slug', 'projects', ['slug'])
    
    # Create project_members table
    op.create_table('project_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'manager', 'lead', 'member', 'contributor', 'viewer', name='project_role_enum'), nullable=False),
        sa.Column('permissions', postgresql.JSON, nullable=True, default=[]),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('hourly_rate', sa.Float, nullable=True),
        sa.Column('allocated_hours', sa.Integer, nullable=True),
        sa.Column('worked_hours', sa.Integer, nullable=True, default=0),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('joined_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('left_at', sa.DateTime, nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invited_at', sa.DateTime, nullable=True),
        sa.Column('invitation_accepted_at', sa.DateTime, nullable=True),
        sa.Column('invitation_message', sa.String(length=1000), nullable=True),
        sa.Column('member_notes', sa.String(length=2000), nullable=True),
        sa.Column('member_metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )
    
    # Create indexes for project_members
    op.create_index('idx_project_members_project_user', 'project_members', ['project_id', 'user_id'])
    op.create_index('idx_project_members_project_role', 'project_members', ['project_id', 'role'])
    op.create_index('idx_project_members_project_active', 'project_members', ['project_id', 'is_active'])
    op.create_index('idx_project_members_user_projects', 'project_members', ['user_id', 'is_active'])
    
    # Create project_milestones table
    op.create_table('project_milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('target_date', sa.Date, nullable=False),
        sa.Column('actual_date', sa.Date, nullable=True),
        sa.Column('status', postgresql.ENUM('upcoming', 'in_progress', 'completed', 'delayed', 'cancelled', name='milestone_status_enum'), nullable=False, default='upcoming'),
        sa.Column('progress_percentage', sa.Integer, nullable=False, default=0),
        sa.Column('order_index', sa.Integer, nullable=False, default=0),
        sa.Column('milestone_number', sa.String(length=50), nullable=True),
        sa.Column('deliverables', postgresql.JSON, nullable=True, default=[]),
        sa.Column('success_criteria', postgresql.JSON, nullable=True, default=[]),
        sa.Column('responsible_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('budget_allocated', sa.Float, nullable=True),
        sa.Column('budget_spent', sa.Float, nullable=True, default=0),
        sa.Column('external_milestone_id', sa.String(length=100), nullable=True),
        sa.Column('milestone_metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )
    
    # Create indexes for project_milestones
    op.create_index('idx_project_milestones_project_status', 'project_milestones', ['project_id', 'status'])
    op.create_index('idx_project_milestones_project_target_date', 'project_milestones', ['project_id', 'target_date'])
    op.create_index('idx_project_milestones_responsible_user', 'project_milestones', ['responsible_user_id', 'status'])
    op.create_index('idx_project_milestones_target_date_status', 'project_milestones', ['target_date', 'status'])
    
    # Create project_deliverables table (NEW - Main feature)
    op.create_table('project_deliverables',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('milestone_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_milestones.id'), nullable=True),
        sa.Column('type', postgresql.ENUM('FILE_UPLOAD', 'GIT_REPO_URL', 'EXTERNAL_URL', name='deliverable_type_enum'), nullable=False),
        sa.Column('file_path_or_url', sa.Text, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('submitted_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('status', postgresql.ENUM('draft', 'submitted', 'under_review', 'approved', 'rejected', 'revision_requested', name='deliverable_status_enum'), nullable=False, default='draft'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('version', sa.String(length=20), nullable=False, default='1.0'),
        sa.Column('previous_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_deliverables.id'), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('file_size_bytes', sa.Integer, nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('download_count', sa.Integer, nullable=False, default=0),
        sa.Column('last_downloaded_at', sa.DateTime, nullable=True),
        sa.Column('deliverable_metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )
    
    # Create indexes for project_deliverables (OPTIMIZED for performance)
    op.create_index('idx_project_deliverables_project_user', 'project_deliverables', ['project_id', 'user_id'])
    op.create_index('idx_project_deliverables_project_status', 'project_deliverables', ['project_id', 'status'])
    op.create_index('idx_project_deliverables_user_submissions', 'project_deliverables', ['user_id', 'submitted_at'])
    op.create_index('idx_project_deliverables_milestone', 'project_deliverables', ['milestone_id', 'submitted_at'])
    op.create_index('idx_project_deliverables_type_status', 'project_deliverables', ['type', 'status'])
    op.create_index('idx_project_deliverables_reviewed_by', 'project_deliverables', ['reviewed_by', 'reviewed_at'])
    op.create_index('idx_project_deliverables_active', 'project_deliverables', ['is_active', 'created_at'])
    
    # Create project_tasks table
    op.create_table('project_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_tasks.id'), nullable=True),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', postgresql.ENUM('todo', 'in_progress', 'in_review', 'blocked', 'completed', 'cancelled', name='task_status_enum'), nullable=False, default='todo'),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', name='task_priority_enum'), nullable=False, default='medium'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('estimated_hours', sa.Float, nullable=True),
        sa.Column('actual_hours', sa.Float, nullable=True, default=0),
        sa.Column('progress_percentage', sa.Integer, nullable=False, default=0),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('order_index', sa.Integer, nullable=False, default=0),
        sa.Column('task_number', sa.String(length=50), nullable=True),
        sa.Column('skills_required', postgresql.JSON, nullable=True, default=[]),
        sa.Column('labels', postgresql.JSON, nullable=True, default=[]),
        sa.Column('dependencies', postgresql.JSON, nullable=True, default=[]),
        sa.Column('blocked_by', postgresql.JSON, nullable=True, default=[]),
        sa.Column('blocking_reason', sa.String(length=500), nullable=True),
        sa.Column('external_task_id', sa.String(length=100), nullable=True),
        sa.Column('external_url', sa.String(length=500), nullable=True),
        sa.Column('task_metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )
    
    # Create indexes for project_tasks
    op.create_index('idx_project_tasks_project_status', 'project_tasks', ['project_id', 'status'])
    op.create_index('idx_project_tasks_project_assigned', 'project_tasks', ['project_id', 'assigned_to'])
    op.create_index('idx_project_tasks_assigned_status', 'project_tasks', ['assigned_to', 'status'])
    op.create_index('idx_project_tasks_due_date_status', 'project_tasks', ['due_date', 'status'])
    op.create_index('idx_project_tasks_parent_task', 'project_tasks', ['parent_task_id', 'order_index'])
    op.create_index('idx_project_tasks_created_by_project', 'project_tasks', ['created_by', 'project_id'])
    
    # Create project_attachments table (Enhanced to support deliverables)
    op.create_table('project_attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_tasks.id'), nullable=True),
        sa.Column('milestone_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_milestones.id'), nullable=True),
        sa.Column('deliverable_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('project_deliverables.id'), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('file_type', sa.String(length=100), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('upload_source', sa.String(length=50), nullable=False, default='web'),
        sa.Column('is_public', sa.Boolean, nullable=False, default=False),
        sa.Column('download_count', sa.Integer, nullable=False, default=0),
        sa.Column('file_metadata', postgresql.JSON, nullable=True, default={}),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )
    
    # Create indexes for project_attachments
    op.create_index('idx_project_attachments_project_files', 'project_attachments', ['project_id', 'created_at'])
    op.create_index('idx_project_attachments_task_files', 'project_attachments', ['task_id', 'created_at'])
    op.create_index('idx_project_attachments_milestone_files', 'project_attachments', ['milestone_id', 'created_at'])
    op.create_index('idx_project_attachments_deliverable_files', 'project_attachments', ['deliverable_id', 'created_at'])
    op.create_index('idx_project_attachments_uploaded_by', 'project_attachments', ['uploaded_by', 'created_at'])


def downgrade() -> None:
    """Drop deliverables management tables."""
    
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('project_attachments')
    op.drop_table('project_tasks')
    op.drop_table('project_deliverables')  # Main table to drop
    op.drop_table('project_milestones')
    op.drop_table('project_members')
    op.drop_table('projects')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS deliverable_type_enum")
    op.execute("DROP TYPE IF EXISTS deliverable_status_enum")
    op.execute("DROP TYPE IF EXISTS project_status_enum")
    op.execute("DROP TYPE IF EXISTS project_priority_enum")
    op.execute("DROP TYPE IF EXISTS project_type_enum")
    op.execute("DROP TYPE IF EXISTS project_role_enum")
    op.execute("DROP TYPE IF EXISTS task_status_enum")
    op.execute("DROP TYPE IF EXISTS task_priority_enum")
    op.execute("DROP TYPE IF EXISTS milestone_status_enum")