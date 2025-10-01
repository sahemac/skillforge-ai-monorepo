"""
Translation models for SkillForge AI Localization Service
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LanguageCode(str, Enum):
    """Supported language codes (ISO 639-1)."""
    EN = "en"  # English
    FR = "fr"  # French
    ES = "es"  # Spanish
    DE = "de"  # German
    IT = "it"  # Italian
    PT = "pt"  # Portuguese
    JA = "ja"  # Japanese
    KO = "ko"  # Korean
    ZH = "zh"  # Chinese (Simplified)


class TranslationStatus(str, Enum):
    """Translation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    REJECTED = "rejected"


class ContentType(str, Enum):
    """Content type for translations."""
    UI_TEXT = "ui_text"
    COURSE_CONTENT = "course_content"
    EMAIL_TEMPLATE = "email_template"
    NOTIFICATION = "notification"
    ERROR_MESSAGE = "error_message"
    HELP_TEXT = "help_text"
    MARKETING = "marketing"


class TranslationKey(BaseModel):
    """Translation key model."""
    id: UUID = Field(default_factory=uuid4)
    key: str = Field(..., description="Unique identifier for the translation")
    namespace: str = Field(..., description="Namespace/module for the translation")
    content_type: ContentType
    default_text: str = Field(..., description="Default text (usually in English)")
    description: Optional[str] = Field(default=None, description="Context description for translators")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Translation(BaseModel):
    """Translation model."""
    id: UUID = Field(default_factory=uuid4)
    translation_key_id: UUID
    language_code: LanguageCode
    translated_text: str
    status: TranslationStatus = TranslationStatus.PENDING

    # Translation metadata
    translator_id: Optional[UUID] = Field(default=None)
    reviewer_id: Optional[UUID] = Field(default=None)
    translation_notes: Optional[str] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)

    # Quality metrics
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_machine_translated: bool = Field(default=False)
    translation_service: Optional[str] = Field(default=None)  # Google Translate, DeepL, etc.

    # Versioning
    version: int = Field(default=1)
    parent_translation_id: Optional[UUID] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TranslationProject(BaseModel):
    """Translation project for organizing related translations."""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    source_language: LanguageCode = LanguageCode.EN
    target_languages: list[LanguageCode]

    # Project metadata
    project_manager_id: Optional[UUID] = Field(default=None)
    deadline: Optional[datetime] = Field(default=None)
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest, 10 = lowest

    # Progress tracking
    total_keys: int = Field(default=0)
    translated_keys: int = Field(default=0)
    reviewed_keys: int = Field(default=0)
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

    # Status
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TranslationMemory(BaseModel):
    """Translation memory for reusing previous translations."""
    id: UUID = Field(default_factory=uuid4)
    source_text: str
    target_text: str
    source_language: LanguageCode
    target_language: LanguageCode

    # Context and metadata
    domain: Optional[str] = Field(default=None)  # e.g., "education", "technical", "legal"
    context: Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)

    # Quality and usage metrics
    usage_count: int = Field(default=1)
    quality_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)

    # Metadata
    created_by: Optional[UUID] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Glossary(BaseModel):
    """Glossary terms for consistent translations."""
    id: UUID = Field(default_factory=uuid4)
    term: str = Field(..., description="Term in source language")
    translation: str = Field(..., description="Translation in target language")
    source_language: LanguageCode
    target_language: LanguageCode

    # Context and definition
    definition: Optional[str] = Field(default=None)
    context: Optional[str] = Field(default=None)
    domain: Optional[str] = Field(default=None)

    # Usage instructions
    do_not_translate: bool = Field(default=False)
    preferred_translation: bool = Field(default=True)
    alternative_translations: list[str] = Field(default_factory=list)

    # Metadata
    created_by: Optional[UUID] = Field(default=None)
    approved_by: Optional[UUID] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }