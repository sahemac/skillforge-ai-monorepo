"""
Project schemas for SkillForge AI Project Service
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
import re

from app.models.project import (
    ProjectStatus, ProjectPriority, ProjectType, ProjectRole,
    TaskStatus, TaskPriority, MilestoneStatus, 
    DeliverableType, DeliverableStatus
)


# Base schemas
class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=5000, description="Project description")
    short_description: Optional[str] = Field(None, max_length=500, description="Short description")
    project_type: ProjectType = Field(default=ProjectType.LEARNING, description="Project type")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Project status")
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM, description="Project priority")
    
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Estimated hours")
    
    budget: Optional[float] = Field(None, ge=0, description="Project budget")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    
    skills_required: List[str] = Field(default=[], description="Required skills")
    skills_learned: List[str] = Field(default=[], description="Skills learned")
    tags: List[str] = Field(default=[], description="Project tags")
    
    is_public: bool = Field(default=False, description="Is project public")
    visibility: str = Field(default="company", description="Project visibility")
    
    repository_url: Optional[str] = Field(None, max_length=500, description="Repository URL")
    documentation_url: Optional[str] = Field(None, max_length=500, description="Documentation URL")
    
    metadata: Dict[str, Any] = Field(default={}, description="Project metadata")
    project_settings: Dict[str, Any] = Field(default={}, description="Project settings")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @field_validator('skills_required', 'skills_learned', 'tags')
    @classmethod
    def validate_string_lists(cls, v):
        if not isinstance(v, list):
            return []
        return [item.strip() for item in v if item and item.strip()]

    @field_validator('repository_url', 'documentation_url')
    @classmethod
    def validate_urls(cls, v):
        if v and not re.match(r'^https?://', v):
            raise ValueError('URL must start with http:// or https://')
        return v


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    company_id: UUID = Field(..., description="Company ID")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Web Development Training",
                "description": "Complete web development training program",
                "short_description": "Learn modern web development",
                "company_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_type": "learning",
                "status": "draft",
                "priority": "medium",
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "estimated_hours": 120,
                "budget": 5000.0,
                "currency": "USD",
                "skills_required": ["HTML", "CSS", "JavaScript", "React"],
                "tags": ["frontend", "web", "training"],
                "is_public": False,
                "visibility": "company"
            }
        }
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    short_description: Optional[str] = Field(None, max_length=500)
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    actual_hours: Optional[int] = Field(None, ge=0)
    
    budget: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    skills_required: Optional[List[str]] = None
    skills_learned: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    is_public: Optional[bool] = None
    visibility: Optional[str] = None
    
    repository_url: Optional[str] = Field(None, max_length=500)
    documentation_url: Optional[str] = Field(None, max_length=500)
    
    metadata: Optional[Dict[str, Any]] = None
    project_settings: Optional[Dict[str, Any]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Project name cannot be empty')
        return v.strip() if v else v

    @field_validator('repository_url', 'documentation_url')
    @classmethod
    def validate_urls(cls, v):
        if v and not re.match(r'^https?://', v):
            raise ValueError('URL must start with http:// or https://')
        return v


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: UUID
    slug: str
    company_id: UUID
    created_by: UUID
    
    actual_hours: int = 0
    actual_cost: float = 0.0
    progress_percentage: int = 0
    completed_tasks: int = 0
    total_tasks: int = 0
    
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for project list response."""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class ProjectSummary(BaseModel):
    """Schema for project summary."""
    id: UUID
    name: str
    short_description: Optional[str] = None
    status: ProjectStatus
    priority: ProjectPriority
    progress_percentage: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    company_id: UUID
    created_by: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Project Member Schemas
class ProjectMemberBase(BaseModel):
    """Base project member schema."""
    role: ProjectRole = Field(..., description="Member role")
    permissions: List[str] = Field(default=[], description="Member permissions")
    title: Optional[str] = Field(None, max_length=200, description="Member title")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate")
    allocated_hours: Optional[int] = Field(None, ge=0, description="Allocated hours")
    invitation_message: Optional[str] = Field(None, max_length=1000, description="Invitation message")
    member_notes: Optional[str] = Field(None, max_length=2000, description="Member notes")
    member_metadata: Dict[str, Any] = Field(default={}, description="Member metadata")


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding a project member."""
    user_id: UUID = Field(..., description="User ID")
    project_id: UUID = Field(..., description="Project ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "member",
                "permissions": ["read", "write"],
                "title": "Frontend Developer",
                "hourly_rate": 50.0,
                "allocated_hours": 40,
                "invitation_message": "Welcome to our project!"
            }
        }
    )


class ProjectMemberUpdate(BaseModel):
    """Schema for updating a project member."""
    role: Optional[ProjectRole] = None
    permissions: Optional[List[str]] = None
    title: Optional[str] = Field(None, max_length=200)
    hourly_rate: Optional[float] = Field(None, ge=0)
    allocated_hours: Optional[int] = Field(None, ge=0)
    worked_hours: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    member_notes: Optional[str] = Field(None, max_length=2000)
    member_metadata: Optional[Dict[str, Any]] = None


class ProjectMemberResponse(ProjectMemberBase):
    """Schema for project member response."""
    id: UUID
    project_id: UUID
    user_id: UUID
    worked_hours: int = 0
    is_active: bool = True
    joined_at: datetime
    left_at: Optional[datetime] = None
    invited_by: Optional[UUID] = None
    invited_at: Optional[datetime] = None
    invitation_accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class ProjectTaskBase(BaseModel):
    """Base project task schema."""
    title: str = Field(..., min_length=1, max_length=300, description="Task title")
    description: Optional[str] = Field(None, max_length=5000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    
    assigned_to: Optional[UUID] = Field(None, description="Assigned user ID")
    parent_task_id: Optional[UUID] = Field(None, description="Parent task ID")
    
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours")
    
    order_index: int = Field(default=0, ge=0, description="Task order")
    task_number: Optional[str] = Field(None, max_length=50, description="Task number")
    
    skills_required: List[str] = Field(default=[], description="Required skills")
    labels: List[str] = Field(default=[], description="Task labels")
    dependencies: List[str] = Field(default=[], description="Task dependencies")
    blocking_reason: Optional[str] = Field(None, max_length=500, description="Blocking reason")
    
    external_task_id: Optional[str] = Field(None, max_length=100, description="External task ID")
    external_url: Optional[str] = Field(None, max_length=500, description="External URL")
    task_metadata: Dict[str, Any] = Field(default={}, description="Task metadata")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Task title cannot be empty')
        return v.strip()


class ProjectTaskCreate(ProjectTaskBase):
    """Schema for creating a project task."""
    project_id: UUID = Field(..., description="Project ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Setup development environment",
                "description": "Install and configure development tools",
                "status": "todo",
                "priority": "high",
                "estimated_hours": 4.0,
                "due_date": "2024-01-15T17:00:00Z",
                "skills_required": ["Docker", "Node.js"],
                "labels": ["setup", "environment"]
            }
        }
    )


class ProjectTaskUpdate(BaseModel):
    """Schema for updating a project task."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    
    assigned_to: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    order_index: Optional[int] = Field(None, ge=0)
    task_number: Optional[str] = Field(None, max_length=50)
    
    skills_required: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    blocking_reason: Optional[str] = Field(None, max_length=500)
    
    external_task_id: Optional[str] = Field(None, max_length=100)
    external_url: Optional[str] = Field(None, max_length=500)
    task_metadata: Optional[Dict[str, Any]] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Task title cannot be empty')
        return v.strip() if v else v


class ProjectTaskResponse(ProjectTaskBase):
    """Schema for project task response."""
    id: UUID
    project_id: UUID
    created_by: UUID
    actual_hours: float = 0.0
    progress_percentage: int = 0
    completed_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Milestone Schemas
class ProjectMilestoneBase(BaseModel):
    """Base project milestone schema."""
    title: str = Field(..., min_length=1, max_length=300, description="Milestone title")
    description: Optional[str] = Field(None, max_length=5000, description="Milestone description")
    target_date: date = Field(..., description="Target completion date")
    
    order_index: int = Field(default=0, ge=0, description="Milestone order")
    milestone_number: Optional[str] = Field(None, max_length=50, description="Milestone number")
    
    deliverables: List[str] = Field(default=[], description="Milestone deliverables")
    success_criteria: List[str] = Field(default=[], description="Success criteria")
    
    responsible_user_id: Optional[UUID] = Field(None, description="Responsible user ID")
    budget_allocated: Optional[float] = Field(None, ge=0, description="Allocated budget")
    
    external_milestone_id: Optional[str] = Field(None, max_length=100, description="External milestone ID")
    milestone_metadata: Dict[str, Any] = Field(default={}, description="Milestone metadata")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Milestone title cannot be empty')
        return v.strip()


class ProjectMilestoneCreate(ProjectMilestoneBase):
    """Schema for creating a project milestone."""
    project_id: UUID = Field(..., description="Project ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "MVP Release",
                "description": "Release minimum viable product",
                "target_date": "2024-03-31",
                "deliverables": ["Working application", "Documentation", "Tests"],
                "success_criteria": ["All tests pass", "Performance benchmarks met"],
                "budget_allocated": 10000.0
            }
        }
    )


class ProjectMilestoneUpdate(BaseModel):
    """Schema for updating a project milestone."""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = Field(None, max_length=5000)
    target_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[MilestoneStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    order_index: Optional[int] = Field(None, ge=0)
    milestone_number: Optional[str] = Field(None, max_length=50)
    
    deliverables: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    
    responsible_user_id: Optional[UUID] = None
    budget_allocated: Optional[float] = Field(None, ge=0)
    budget_spent: Optional[float] = Field(None, ge=0)
    
    external_milestone_id: Optional[str] = Field(None, max_length=100)
    milestone_metadata: Optional[Dict[str, Any]] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Milestone title cannot be empty')
        return v.strip() if v else v


class ProjectMilestoneResponse(ProjectMilestoneBase):
    """Schema for project milestone response."""
    id: UUID
    project_id: UUID
    created_by: UUID
    status: MilestoneStatus = MilestoneStatus.UPCOMING
    actual_date: Optional[date] = None
    progress_percentage: int = 0
    budget_spent: float = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Analytics and Reports
class ProjectStats(BaseModel):
    """Project statistics schema."""
    total_projects: int
    active_projects: int
    completed_projects: int
    on_hold_projects: int
    cancelled_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_members: int
    total_hours_estimated: float
    total_hours_worked: float
    total_budget: float
    total_spent: float


class ProjectAnalytics(BaseModel):
    """Project analytics schema."""
    project_id: UUID
    completion_rate: float = Field(ge=0, le=100)
    efficiency_rate: float = Field(ge=0)  # actual_hours / estimated_hours
    budget_utilization: float = Field(ge=0, le=100)
    team_utilization: float = Field(ge=0, le=100)
    avg_task_completion_time: Optional[float] = None
    milestone_completion_rate: float = Field(ge=0, le=100)
    overdue_tasks_count: int = Field(ge=0)
    critical_path_tasks: List[UUID] = Field(default=[])


# Error schemas
class ProjectError(BaseModel):
    """Project error schema."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Bulk operations
class BulkProjectUpdate(BaseModel):
    """Schema for bulk project updates."""
    project_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: ProjectUpdate

    @field_validator('project_ids')
    @classmethod
    def validate_project_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Duplicate project IDs found')
        return v


class BulkTaskUpdate(BaseModel):
    """Schema for bulk task updates."""
    task_ids: List[UUID] = Field(..., min_length=1, max_length=100)
    updates: ProjectTaskUpdate

    @field_validator('task_ids')
    @classmethod
    def validate_task_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Duplicate task IDs found')
        return v