"""
Content schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.content import ContentType, ContentStatus, ContentCategory


class ContentMetadataCreate(BaseModel):
    """Schema for creating content metadata."""
    author_id: UUID
    tags: List[str] = Field(default_factory=list)
    difficulty_level: int = Field(ge=1, le=5, default=1)
    estimated_duration: Optional[int] = Field(default=None)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ContentCreate(BaseModel):
    """Schema for creating content."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content_type: ContentType
    category: ContentCategory
    body: Optional[str] = Field(default=None)
    media_url: Optional[str] = Field(default=None)
    attachments: List[str] = Field(default_factory=list)
    metadata: ContentMetadataCreate


class ContentUpdate(BaseModel):
    """Schema for updating content."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    content_type: Optional[ContentType] = Field(default=None)
    category: Optional[ContentCategory] = Field(default=None)
    body: Optional[str] = Field(default=None)
    media_url: Optional[str] = Field(default=None)
    attachments: Optional[List[str]] = Field(default=None)
    metadata: Optional[ContentMetadataCreate] = Field(default=None)


class ContentStatusUpdate(BaseModel):
    """Schema for updating content status."""
    status: ContentStatus
    change_summary: Optional[str] = Field(default=None)


class ContentMetadataResponse(BaseModel):
    """Schema for content metadata response."""
    author_id: UUID
    tags: List[str]
    difficulty_level: int
    estimated_duration: Optional[int]
    prerequisites: List[str]
    learning_objectives: List[str]
    custom_fields: Dict[str, Any]


class ContentResponse(BaseModel):
    """Schema for content response."""
    id: UUID
    title: str
    description: Optional[str]
    content_type: ContentType
    category: ContentCategory
    status: ContentStatus
    body: Optional[str]
    media_url: Optional[str]
    attachments: List[str]
    metadata: ContentMetadataResponse
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    view_count: int
    like_count: int
    download_count: int
    version: int
    parent_id: Optional[UUID]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ContentListResponse(BaseModel):
    """Schema for paginated content list response."""
    items: List[ContentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ContentSearchQuery(BaseModel):
    """Schema for content search query."""
    query: Optional[str] = Field(default=None)
    content_type: Optional[ContentType] = Field(default=None)
    category: Optional[ContentCategory] = Field(default=None)
    status: Optional[ContentStatus] = Field(default=None)
    author_id: Optional[UUID] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=5)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class ContentInteractionCreate(BaseModel):
    """Schema for creating content interaction."""
    content_id: UUID
    interaction_type: str
    session_id: Optional[str] = Field(default=None)
    duration: Optional[int] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentInteractionResponse(BaseModel):
    """Schema for content interaction response."""
    id: UUID
    content_id: UUID
    user_id: UUID
    interaction_type: str
    timestamp: datetime
    session_id: Optional[str]
    duration: Optional[int]
    metadata: Dict[str, Any]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ContentCollectionCreate(BaseModel):
    """Schema for creating content collection."""
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    content_ids: List[UUID] = Field(default_factory=list)
    is_public: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)


class ContentCollectionUpdate(BaseModel):
    """Schema for updating content collection."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    content_ids: Optional[List[UUID]] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)


class ContentCollectionResponse(BaseModel):
    """Schema for content collection response."""
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    content_ids: List[UUID]
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[str]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ContentVersionResponse(BaseModel):
    """Schema for content version response."""
    id: UUID
    content_id: UUID
    version_number: int
    title: str
    body: Optional[str]
    metadata: ContentMetadataResponse
    created_at: datetime
    created_by: UUID
    change_summary: Optional[str]

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class ContentAnalytics(BaseModel):
    """Schema for content analytics."""
    content_id: UUID
    total_views: int
    unique_views: int
    total_likes: int
    total_downloads: int
    average_rating: float
    engagement_rate: float
    popular_tags: List[str]
    view_trend: List[Dict[str, Any]]  # Daily/weekly/monthly view data