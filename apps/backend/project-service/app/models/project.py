"""
Project models for SkillForge AI Project Service
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Column, Relationship
from sqlalchemy import JSON, Index, Text
from enum import Enum
import uuid

from .base import BaseModel, SoftDeleteMixin


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    DRAFT = "draft"
    PLANNING = "planning"  
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectPriority(str, Enum):
    """Project priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectType(str, Enum):
    """Project type enumeration."""
    LEARNING = "learning"
    DEVELOPMENT = "development"
    RESEARCH = "research"
    TRAINING = "training"
    CERTIFICATION = "certification"
    INTERNAL = "internal"
    CLIENT = "client"
    OTHER = "other"


class ProjectRole(str, Enum):
    """Project member role enumeration."""
    OWNER = "owner"           # Full project control
    MANAGER = "manager"       # Project management
    LEAD = "lead"            # Technical leadership
    MEMBER = "member"        # Regular team member
    CONTRIBUTOR = "contributor"  # Limited contribution
    VIEWER = "viewer"        # Read-only access


class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MilestoneStatus(str, Enum):
    """Milestone status enumeration."""
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class DeliverableType(str, Enum):
    """Deliverable type enumeration."""
    FILE_UPLOAD = "FILE_UPLOAD"
    GIT_REPO_URL = "GIT_REPO_URL"
    EXTERNAL_URL = "EXTERNAL_URL"


class DeliverableStatus(str, Enum):
    """Deliverable status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class Project(BaseModel, SoftDeleteMixin, table=True):
    """Main project model."""
    
    __tablename__ = "projects"
    
    # Basic Information
    name: str = Field(nullable=False, max_length=200, index=True)
    slug: str = Field(unique=True, index=True, nullable=False, max_length=100)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    short_description: Optional[str] = Field(default=None, max_length=500)
    
    # Project Classification
    project_type: ProjectType = Field(default=ProjectType.LEARNING, nullable=False)
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, nullable=False, index=True)
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM, nullable=False)
    
    # Ownership and Company
    company_id: uuid.UUID = Field(nullable=False, index=True)
    created_by: uuid.UUID = Field(nullable=False, index=True)  # User who created the project
    
    # Timeline
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    estimated_hours: Optional[int] = Field(default=None, ge=0)
    actual_hours: Optional[int] = Field(default=0, ge=0)
    
    # Budget and Cost
    budget: Optional[float] = Field(default=None, ge=0)
    actual_cost: Optional[float] = Field(default=0, ge=0)
    currency: str = Field(default="USD", max_length=3)
    
    # Progress Tracking
    progress_percentage: int = Field(default=0, ge=0, le=100)
    completed_tasks: int = Field(default=0, ge=0)
    total_tasks: int = Field(default=0, ge=0)
    
    # Skills and Tags
    skills_required: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    skills_learned: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    
    # Visibility and Access
    is_public: bool = Field(default=False, nullable=False)
    visibility: str = Field(default="company", nullable=False)  # public, company, team, private
    
    # Metadata and Settings
    project_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    project_settings: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # External References
    external_project_id: Optional[str] = Field(default=None, max_length=100)
    repository_url: Optional[str] = Field(default=None, max_length=500)
    documentation_url: Optional[str] = Field(default=None, max_length=500)
    
    # Database Indexes for optimization
    __table_args__ = (
        Index('idx_company_status', 'company_id', 'status'),
        Index('idx_company_active', 'company_id', 'is_active'),
        Index('idx_created_by_status', 'created_by', 'status'),
        Index('idx_project_type_status', 'project_type', 'status'),
        Index('idx_priority_status', 'priority', 'status'),
        Index('idx_visibility_public', 'visibility', 'is_public'),
    )

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            uuid.UUID: str
        }


class ProjectMember(BaseModel, table=True):
    """Project team members."""
    
    __tablename__ = "project_members"
    
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(nullable=False, index=True)  # Reference to user service
    
    # Role and Permissions
    role: ProjectRole = Field(nullable=False)
    permissions: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    
    # Member Information
    title: Optional[str] = Field(default=None, max_length=200)
    hourly_rate: Optional[float] = Field(default=None, ge=0)
    allocated_hours: Optional[int] = Field(default=None, ge=0)
    worked_hours: Optional[int] = Field(default=0, ge=0)
    
    # Status and Timeline
    is_active: bool = Field(default=True, nullable=False)
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    left_at: Optional[datetime] = Field(default=None)
    
    # Invitation Information
    invited_by: Optional[uuid.UUID] = Field(default=None)
    invited_at: Optional[datetime] = Field(default=None)
    invitation_accepted_at: Optional[datetime] = Field(default=None)
    invitation_message: Optional[str] = Field(default=None, max_length=1000)
    
    # Member Metadata
    member_notes: Optional[str] = Field(default=None, max_length=2000)
    member_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes
    __table_args__ = (
        Index('idx_project_user', 'project_id', 'user_id'),
        Index('idx_project_role', 'project_id', 'role'),
        Index('idx_project_active', 'project_id', 'is_active'),
        Index('idx_user_projects', 'user_id', 'is_active'),
    )


class ProjectTask(BaseModel, SoftDeleteMixin, table=True):
    """Project tasks and subtasks."""
    
    __tablename__ = "project_tasks"
    
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    parent_task_id: Optional[uuid.UUID] = Field(foreign_key="project_tasks.id", default=None)
    
    # Basic Information
    title: str = Field(nullable=False, max_length=300)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Task Management
    status: TaskStatus = Field(default=TaskStatus.TODO, nullable=False, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False)
    
    # Assignment and Responsibility
    assigned_to: Optional[uuid.UUID] = Field(default=None, index=True)
    created_by: uuid.UUID = Field(nullable=False)
    
    # Timeline and Effort
    due_date: Optional[datetime] = Field(default=None)
    estimated_hours: Optional[float] = Field(default=None, ge=0)
    actual_hours: Optional[float] = Field(default=0, ge=0)
    
    # Progress and Completion
    progress_percentage: int = Field(default=0, ge=0, le=100)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Task Organization
    order_index: int = Field(default=0, ge=0)
    task_number: Optional[str] = Field(default=None, max_length=50)  # e.g., "PROJ-123"
    
    # Skills and Labels
    skills_required: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    labels: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    
    # Dependencies and Blocking
    dependencies: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))  # Task IDs
    blocked_by: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    blocking_reason: Optional[str] = Field(default=None, max_length=500)
    
    # External References
    external_task_id: Optional[str] = Field(default=None, max_length=100)
    external_url: Optional[str] = Field(default=None, max_length=500)
    
    # Task Metadata
    task_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes
    __table_args__ = (
        Index('idx_project_status', 'project_id', 'status'),
        Index('idx_project_assigned', 'project_id', 'assigned_to'),
        Index('idx_assigned_status', 'assigned_to', 'status'),
        Index('idx_due_date_status', 'due_date', 'status'),
        Index('idx_parent_task', 'parent_task_id', 'order_index'),
        Index('idx_created_by_project', 'created_by', 'project_id'),
    )


class ProjectMilestone(BaseModel, table=True):
    """Project milestones and deliverables."""
    
    __tablename__ = "project_milestones"
    
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    
    # Basic Information
    title: str = Field(nullable=False, max_length=300)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Timeline
    target_date: date = Field(nullable=False)
    actual_date: Optional[date] = Field(default=None)
    
    # Status and Progress
    status: MilestoneStatus = Field(default=MilestoneStatus.UPCOMING, nullable=False)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    
    # Organization
    order_index: int = Field(default=0, ge=0)
    milestone_number: Optional[str] = Field(default=None, max_length=50)
    
    # Deliverables and Requirements
    deliverables: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    success_criteria: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    
    # Responsibility
    responsible_user_id: Optional[uuid.UUID] = Field(default=None)
    created_by: uuid.UUID = Field(nullable=False)
    
    # Budget and Resources
    budget_allocated: Optional[float] = Field(default=None, ge=0)
    budget_spent: Optional[float] = Field(default=0, ge=0)
    
    # External References
    external_milestone_id: Optional[str] = Field(default=None, max_length=100)
    
    # Milestone Metadata
    milestone_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes
    __table_args__ = (
        Index('idx_project_status_milestone', 'project_id', 'status'),
        Index('idx_project_target_date', 'project_id', 'target_date'),
        Index('idx_responsible_user', 'responsible_user_id', 'status'),
        Index('idx_target_date_status', 'target_date', 'status'),
    )


class ProjectComment(BaseModel, table=True):
    """Comments and discussions on projects."""
    
    __tablename__ = "project_comments"
    
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    task_id: Optional[uuid.UUID] = Field(foreign_key="project_tasks.id", default=None)
    milestone_id: Optional[uuid.UUID] = Field(foreign_key="project_milestones.id", default=None)
    parent_comment_id: Optional[uuid.UUID] = Field(foreign_key="project_comments.id", default=None)
    
    # Comment Content
    content: str = Field(sa_column=Column(Text, nullable=False))
    content_type: str = Field(default="text", max_length=20)  # text, markdown, html
    
    # Author Information
    author_id: uuid.UUID = Field(nullable=False, index=True)
    
    # Comment Management
    is_resolved: bool = Field(default=False, nullable=False)
    is_pinned: bool = Field(default=False, nullable=False)
    
    # Attachments and References
    attachments: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    mentions: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))  # User IDs
    
    # Editing History
    edited_at: Optional[datetime] = Field(default=None)
    edit_count: int = Field(default=0, ge=0)
    
    # Comment Metadata
    comment_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes
    __table_args__ = (
        Index('idx_project_author', 'project_id', 'author_id'),
        Index('idx_task_comments', 'task_id', 'created_at'),
        Index('idx_milestone_comments', 'milestone_id', 'created_at'),
        Index('idx_parent_comment', 'parent_comment_id', 'created_at'),
    )


class ProjectDeliverable(BaseModel, SoftDeleteMixin, table=True):
    """Project deliverables management according to official specifications."""
    
    __tablename__ = "project_deliverables"
    
    # Basic References - Conform to Documentation
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    user_id: uuid.UUID = Field(nullable=False, index=True)  # Apprenant qui a soumis le livrable
    milestone_id: Optional[uuid.UUID] = Field(foreign_key="project_milestones.id", default=None)
    
    # Deliverable Core Information - According to Documentation
    type: DeliverableType = Field(nullable=False)  # FILE_UPLOAD, GIT_REPO_URL, EXTERNAL_URL
    file_path_or_url: str = Field(sa_column=Column(Text, nullable=False))  # Chemin GCS ou URL
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))  # Notes optionnelles
    
    # Submission Information
    submitted_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    status: DeliverableStatus = Field(default=DeliverableStatus.DRAFT, nullable=False)
    
    # Review and Validation
    reviewed_by: Optional[uuid.UUID] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(default=None)
    review_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Version Control
    version: str = Field(default="1.0", nullable=False, max_length=20)
    previous_version_id: Optional[uuid.UUID] = Field(foreign_key="project_deliverables.id", default=None)
    
    # File Information (for FILE_UPLOAD type)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    file_size_bytes: Optional[int] = Field(default=None, ge=0)
    mime_type: Optional[str] = Field(default=None, max_length=100)
    file_hash: Optional[str] = Field(default=None, max_length=64)  # SHA-256 for integrity
    
    # Download and Access Tracking
    download_count: int = Field(default=0, ge=0)
    last_downloaded_at: Optional[datetime] = Field(default=None)
    
    # Deliverable Metadata
    deliverable_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes for Performance
    __table_args__ = (
        Index('idx_project_user_deliverable', 'project_id', 'user_id'),
        Index('idx_project_status', 'project_id', 'status'),
        Index('idx_user_submissions', 'user_id', 'submitted_at'),
        Index('idx_milestone_deliverables', 'milestone_id', 'submitted_at'),
        Index('idx_type_status', 'type', 'status'),
        Index('idx_reviewed_by', 'reviewed_by', 'reviewed_at'),
    )


class ProjectAttachment(BaseModel, table=True):
    """File attachments for projects."""
    
    __tablename__ = "project_attachments"
    
    project_id: uuid.UUID = Field(foreign_key="projects.id", nullable=False, index=True)
    task_id: Optional[uuid.UUID] = Field(foreign_key="project_tasks.id", default=None)
    milestone_id: Optional[uuid.UUID] = Field(foreign_key="project_milestones.id", default=None)
    comment_id: Optional[uuid.UUID] = Field(foreign_key="project_comments.id", default=None)
    deliverable_id: Optional[uuid.UUID] = Field(foreign_key="project_deliverables.id", default=None)
    
    # File Information
    filename: str = Field(nullable=False, max_length=255)
    original_filename: str = Field(nullable=False, max_length=255)
    file_path: str = Field(nullable=False, max_length=500)
    file_size: int = Field(nullable=False, ge=0)
    file_type: str = Field(nullable=False, max_length=100)
    mime_type: str = Field(nullable=False, max_length=100)
    
    # Upload Information
    uploaded_by: uuid.UUID = Field(nullable=False, index=True)
    upload_source: str = Field(default="web", max_length=50)
    
    # File Properties
    is_public: bool = Field(default=False, nullable=False)
    download_count: int = Field(default=0, ge=0)
    
    # File Metadata
    file_metadata: Optional[Dict[str, Any]] = Field(default={}, sa_column=Column(JSON))
    
    # Database Indexes
    __table_args__ = (
        Index('idx_project_files', 'project_id', 'created_at'),
        Index('idx_task_files', 'task_id', 'created_at'),
        Index('idx_milestone_files', 'milestone_id', 'created_at'),
        Index('idx_deliverable_files', 'deliverable_id', 'created_at'),
        Index('idx_uploaded_by', 'uploaded_by', 'created_at'),
    )