"""
Schemas package for SkillForge AI Project Service
"""

from .project import (
    # Project schemas
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    ProjectSummary,
    
    # Member schemas
    ProjectMemberBase,
    ProjectMemberCreate,
    ProjectMemberUpdate,
    ProjectMemberResponse,
    
    # Task schemas
    ProjectTaskBase,
    ProjectTaskCreate,
    ProjectTaskUpdate,
    ProjectTaskResponse,
    
    # Milestone schemas
    ProjectMilestoneBase,
    ProjectMilestoneCreate,
    ProjectMilestoneUpdate,
    ProjectMilestoneResponse,
    
    # Analytics schemas
    ProjectStats,
    ProjectAnalytics,
    
    # Bulk operations
    BulkProjectUpdate,
    BulkTaskUpdate,
    
    # Error schemas
    ProjectError,
)

__all__ = [
    # Project schemas
    "ProjectBase",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    "ProjectSummary",
    
    # Member schemas
    "ProjectMemberBase",
    "ProjectMemberCreate",
    "ProjectMemberUpdate",
    "ProjectMemberResponse",
    
    # Task schemas
    "ProjectTaskBase",
    "ProjectTaskCreate",
    "ProjectTaskUpdate",
    "ProjectTaskResponse",
    
    # Milestone schemas
    "ProjectMilestoneBase",
    "ProjectMilestoneCreate",
    "ProjectMilestoneUpdate",
    "ProjectMilestoneResponse",
    
    # Analytics schemas
    "ProjectStats",
    "ProjectAnalytics",
    
    # Bulk operations
    "BulkProjectUpdate",
    "BulkTaskUpdate",
    
    # Error schemas
    "ProjectError",
]