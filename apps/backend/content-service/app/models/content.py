"""
Content models for SkillForge AI Content Service
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content type enumeration."""
    ARTICLE = "article"
    VIDEO = "video"
    COURSE = "course"
    QUIZ = "quiz"
    RESOURCE = "resource"
    TEMPLATE = "template"


class ContentStatus(str, Enum):
    """Content status enumeration."""
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentCategory(str, Enum):
    """Content category enumeration."""
    PROGRAMMING = "programming"
    DATA_SCIENCE = "data_science"
    DESIGN = "design"
    MARKETING = "marketing"
    BUSINESS = "business"
    SOFT_SKILLS = "soft_skills"
    OTHER = "other"


class ContentMetadata(BaseModel):
    """Content metadata model."""
    author_id: UUID
    tags: List[str] = Field(default_factory=list)
    difficulty_level: int = Field(ge=1, le=5, default=1)
    estimated_duration: Optional[int] = Field(default=None)  # in minutes
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class Content(BaseModel):
    """Main content model."""
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content_type: ContentType
    category: ContentCategory
    status: ContentStatus = ContentStatus.DRAFT

    # Content data
    body: Optional[str] = Field(default=None)  # HTML/Markdown content
    media_url: Optional[str] = Field(default=None)  # Video, image, etc.
    attachments: List[str] = Field(default_factory=list)  # File URLs

    # Metadata
    metadata: ContentMetadata

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)

    # Analytics
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    download_count: int = Field(default=0)

    # Version control
    version: int = Field(default=1)
    parent_id: Optional[UUID] = Field(default=None)  # For content versioning

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ContentVersion(BaseModel):
    """Content version tracking model."""
    id: UUID = Field(default_factory=uuid4)
    content_id: UUID
    version_number: int
    title: str
    body: Optional[str]
    metadata: ContentMetadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: UUID
    change_summary: Optional[str] = Field(default=None)


class ContentInteraction(BaseModel):
    """Content interaction tracking model."""
    id: UUID = Field(default_factory=uuid4)
    content_id: UUID
    user_id: UUID
    interaction_type: str  # view, like, share, download, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(default=None)
    duration: Optional[int] = Field(default=None)  # Time spent in seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentCollection(BaseModel):
    """Content collection/playlist model."""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    owner_id: UUID
    content_ids: List[UUID] = Field(default_factory=list)
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    tags: List[str] = Field(default_factory=list)