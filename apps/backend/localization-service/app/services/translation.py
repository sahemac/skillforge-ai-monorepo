"""
Translation service for business logic and data operations
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.translation import (
    TranslationKey, Translation, TranslationProject,
    TranslationMemory, Glossary, LanguageCode,
    TranslationStatus, ContentType
)
from ..core.cache import cache_set, cache_get, cache_delete


class TranslationService:
    """Service for translation management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_translation_keys(
        self,
        namespace: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 50
    ) -> List[TranslationKey]:
        """Get translation keys with filtering and pagination."""
        try:
            # For now, return mock data since we don't have database tables yet
            keys = [
                TranslationKey(
                    key="welcome_message",
                    namespace="ui",
                    content_type=ContentType.UI_TEXT,
                    default_text="Welcome to SkillForge AI",
                    description="Main welcome message on homepage"
                ),
                TranslationKey(
                    key="login_button",
                    namespace="auth",
                    content_type=ContentType.UI_TEXT,
                    default_text="Log In",
                    description="Login button text"
                )
            ]

            # Apply filters
            if namespace:
                keys = [k for k in keys if k.namespace == namespace]
            if content_type:
                keys = [k for k in keys if k.content_type == content_type]
            if active_only:
                keys = [k for k in keys if k.is_active]

            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            return keys[start:end]

        except Exception as e:
            raise ValueError(f"Failed to get translation keys: {str(e)}")

    async def create_translation_key(self, translation_key: TranslationKey) -> TranslationKey:
        """Create a new translation key."""
        try:
            # For now, just return the key with an ID
            translation_key.created_at = datetime.utcnow()
            return translation_key
        except Exception as e:
            raise ValueError(f"Failed to create translation key: {str(e)}")

    async def get_translations_for_key(
        self,
        key_id: UUID,
        language_code: Optional[LanguageCode] = None,
        status_filter: Optional[TranslationStatus] = None
    ) -> List[Translation]:
        """Get translations for a specific key."""
        try:
            # Return mock translations
            translations = [
                Translation(
                    translation_key_id=key_id,
                    language_code=LanguageCode.FR,
                    translated_text="Bienvenue sur SkillForge AI",
                    status=TranslationStatus.PUBLISHED
                ),
                Translation(
                    translation_key_id=key_id,
                    language_code=LanguageCode.ES,
                    translated_text="Bienvenido a SkillForge AI",
                    status=TranslationStatus.REVIEWED
                )
            ]

            # Apply filters
            if language_code:
                translations = [t for t in translations if t.language_code == language_code]
            if status_filter:
                translations = [t for t in translations if t.status == status_filter]

            return translations

        except Exception as e:
            raise ValueError(f"Failed to get translations: {str(e)}")

    async def create_translation(self, translation: Translation) -> Translation:
        """Create a new translation."""
        try:
            translation.created_at = datetime.utcnow()
            return translation
        except Exception as e:
            raise ValueError(f"Failed to create translation: {str(e)}")

    async def update_translation(self, translation_id: UUID, update_data: Dict[str, Any]) -> Optional[Translation]:
        """Update a translation."""
        try:
            # For now, return a mock updated translation
            translation = Translation(
                id=translation_id,
                translation_key_id=UUID("12345678-1234-5678-1234-567812345678"),
                language_code=LanguageCode.FR,
                translated_text=update_data.get("translated_text", "Updated translation"),
                status=TranslationStatus(update_data.get("status", "completed")),
                updated_at=datetime.utcnow()
            )
            return translation
        except Exception as e:
            raise ValueError(f"Failed to update translation: {str(e)}")

    async def export_translations(
        self,
        language_codes: List[LanguageCode],
        namespace: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        format: str = "json",
        published_only: bool = True
    ) -> Dict[str, Any]:
        """Export translations in various formats."""
        try:
            # Mock export data
            export_data = {}

            for lang in language_codes:
                export_data[lang.value] = {
                    "welcome_message": "Welcome to SkillForge AI" if lang == LanguageCode.EN else "Bienvenue sur SkillForge AI",
                    "login_button": "Log In" if lang == LanguageCode.EN else "Se connecter"
                }

            if format == "json":
                return export_data
            elif format == "po":
                # Convert to PO format (simplified)
                po_data = {}
                for lang, translations in export_data.items():
                    po_content = []
                    for key, value in translations.items():
                        po_content.append(f'msgid "{key}"\nmsgstr "{value}"\n')
                    po_data[lang] = "\n".join(po_content)
                return po_data
            else:
                return export_data

        except Exception as e:
            raise ValueError(f"Failed to export translations: {str(e)}")

    async def import_translations(self, import_data: Dict[str, Any]) -> Dict[str, int]:
        """Import translations from various formats."""
        try:
            # Mock import result
            imported_count = len(import_data.get("translations", {}))
            return {
                "imported": imported_count,
                "skipped": 0,
                "errors": 0
            }
        except Exception as e:
            raise ValueError(f"Failed to import translations: {str(e)}")

    async def get_translation_projects(
        self,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> List[TranslationProject]:
        """Get translation projects."""
        try:
            projects = [
                TranslationProject(
                    name="SkillForge UI Localization",
                    description="Translate main UI elements",
                    source_language=LanguageCode.EN,
                    target_languages=[LanguageCode.FR, LanguageCode.ES, LanguageCode.DE],
                    total_keys=150,
                    translated_keys=120,
                    reviewed_keys=100,
                    completion_percentage=80.0
                )
            ]
            return projects
        except Exception as e:
            raise ValueError(f"Failed to get translation projects: {str(e)}")

    async def create_translation_project(self, project: TranslationProject) -> TranslationProject:
        """Create a new translation project."""
        try:
            project.created_at = datetime.utcnow()
            return project
        except Exception as e:
            raise ValueError(f"Failed to create translation project: {str(e)}")

    async def search_translation_memory(
        self,
        source_text: str,
        source_language: LanguageCode,
        target_language: LanguageCode,
        similarity_threshold: float = 0.8,
        limit: int = 10
    ) -> List[TranslationMemory]:
        """Search translation memory for similar translations."""
        try:
            # Mock translation memory results
            if "welcome" in source_text.lower():
                return [
                    TranslationMemory(
                        source_text="Welcome to our platform",
                        target_text="Bienvenue sur notre plateforme",
                        source_language=source_language,
                        target_language=target_language,
                        domain="ui",
                        quality_score=0.95,
                        usage_count=25
                    )
                ]
            return []
        except Exception as e:
            raise ValueError(f"Failed to search translation memory: {str(e)}")

    async def get_glossary_terms(
        self,
        source_language: Optional[LanguageCode] = None,
        target_language: Optional[LanguageCode] = None,
        domain: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ) -> List[Glossary]:
        """Get glossary terms."""
        try:
            terms = [
                Glossary(
                    term="SkillForge",
                    translation="SkillForge",
                    source_language=LanguageCode.EN,
                    target_language=LanguageCode.FR,
                    definition="The name of our AI learning platform",
                    do_not_translate=True
                ),
                Glossary(
                    term="Course",
                    translation="Cours",
                    source_language=LanguageCode.EN,
                    target_language=LanguageCode.FR,
                    definition="A structured learning program"
                )
            ]

            # Apply filters
            if source_language:
                terms = [t for t in terms if t.source_language == source_language]
            if target_language:
                terms = [t for t in terms if t.target_language == target_language]
            if domain:
                terms = [t for t in terms if t.domain == domain]

            return terms
        except Exception as e:
            raise ValueError(f"Failed to get glossary terms: {str(e)}")

    async def create_glossary_term(self, glossary_term: Glossary) -> Glossary:
        """Create a new glossary term."""
        try:
            glossary_term.created_at = datetime.utcnow()
            return glossary_term
        except Exception as e:
            raise ValueError(f"Failed to create glossary term: {str(e)}")

    async def get_translation_stats(
        self,
        language_code: Optional[LanguageCode] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get translation statistics."""
        try:
            stats = {
                "total_keys": 500,
                "total_translations": 2250,
                "languages": 9,
                "completion_by_language": {
                    "en": 100.0,
                    "fr": 85.2,
                    "es": 78.4,
                    "de": 65.8,
                    "it": 45.2,
                    "pt": 32.1,
                    "ja": 25.6,
                    "ko": 18.3,
                    "zh": 12.7
                },
                "completion_by_status": {
                    "published": 1800,
                    "reviewed": 300,
                    "completed": 150,
                    "in_progress": 75,
                    "pending": 225
                },
                "recent_activity": {
                    "translations_this_week": 45,
                    "reviews_this_week": 32,
                    "new_keys_this_week": 8
                }
            }

            if language_code:
                stats["language_specific"] = {
                    "code": language_code.value,
                    "completion_percentage": stats["completion_by_language"].get(language_code.value, 0.0),
                    "pending_translations": 25,
                    "quality_score": 8.7
                }

            return stats
        except Exception as e:
            raise ValueError(f"Failed to get translation stats: {str(e)}")