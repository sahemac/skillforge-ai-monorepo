"""
Models package for SkillForge AI Project Service
"""

from .base import BaseModel, TimestampMixin, UUIDMixin, SoftDeleteMixin
from .project import (
    Project,
    ProjectMember,
    ProjectTask,
    ProjectMilestone,
    ProjectComment,
    ProjectAttachment,
    ProjectStatus,
    ProjectPriority,
    ProjectType,
    ProjectRole,
    TaskStatus,
    TaskPriority,
    MilestoneStatus
)

__all__ = [
    # Base models
    "BaseModel",
    "TimestampMixin", 
    "UUIDMixin",
    "SoftDeleteMixin",
    
    # Project models
    "Project",
    "ProjectMember",
    "ProjectTask",
    "ProjectMilestone", 
    "ProjectComment",
    "ProjectAttachment",
    
    # Enumerations
    "ProjectStatus",
    "ProjectPriority",
    "ProjectType",
    "ProjectRole",
    "TaskStatus",
    "TaskPriority",
    "MilestoneStatus",
]