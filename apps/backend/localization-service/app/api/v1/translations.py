"""
Translation API endpoints for SkillForge AI Localization Service
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ...models.translation import (
    TranslationKey, Translation, TranslationProject,
    TranslationMemory, Glossary, LanguageCode,
    TranslationStatus, ContentType
)
from ...core.database import get_db
from ...services.translation import TranslationService
from ...services.machine_translation import MachineTranslationService

router = APIRouter()


@router.get("/languages", response_model=List[Dict[str, str]])
async def get_supported_languages():
    """Get list of supported languages."""
    languages = [
        {"code": "en", "name": "English", "native": "English"},
        {"code": "fr", "name": "French", "native": "Français"},
        {"code": "es", "name": "Spanish", "native": "Español"},
        {"code": "de", "name": "German", "native": "Deutsch"},
        {"code": "it", "name": "Italian", "native": "Italiano"},
        {"code": "pt", "name": "Portuguese", "native": "Português"},
        {"code": "ja", "name": "Japanese", "native": "日本語"},
        {"code": "ko", "name": "Korean", "native": "한국어"},
        {"code": "zh", "name": "Chinese (Simplified)", "native": "中文 (简体)"}
    ]
    return languages


@router.get("/keys", response_model=List[TranslationKey])
async def get_translation_keys(
    namespace: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    active_only: bool = True,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db = Depends(get_db)
):
    """Get translation keys with optional filtering."""
    try:
        service = TranslationService(db)
        keys = await service.get_translation_keys(
            namespace=namespace,
            content_type=content_type,
            active_only=active_only,
            page=page,
            per_page=per_page
        )
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys", response_model=TranslationKey, status_code=status.HTTP_201_CREATED)
async def create_translation_key(
    key_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a new translation key."""
    try:
        service = TranslationService(db)

        translation_key = TranslationKey(
            key=key_data["key"],
            namespace=key_data["namespace"],
            content_type=ContentType(key_data["content_type"]),
            default_text=key_data["default_text"],
            description=key_data.get("description"),
            metadata=key_data.get("metadata", {})
        )

        result = await service.create_translation_key(translation_key)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys/{key_id}/translations", response_model=List[Translation])
async def get_key_translations(
    key_id: UUID,
    language_code: Optional[LanguageCode] = None,
    status_filter: Optional[TranslationStatus] = None,
    db = Depends(get_db)
):
    """Get translations for a specific key."""
    try:
        service = TranslationService(db)
        translations = await service.get_translations_for_key(
            key_id=key_id,
            language_code=language_code,
            status_filter=status_filter
        )
        return translations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/{key_id}/translations", response_model=Translation, status_code=status.HTTP_201_CREATED)
async def create_translation(
    key_id: UUID,
    translation_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a new translation for a key."""
    try:
        service = TranslationService(db)

        translation = Translation(
            translation_key_id=key_id,
            language_code=LanguageCode(translation_data["language_code"]),
            translated_text=translation_data["translated_text"],
            status=TranslationStatus(translation_data.get("status", "pending")),
            translator_id=translation_data.get("translator_id"),
            translation_notes=translation_data.get("translation_notes"),
            is_machine_translated=translation_data.get("is_machine_translated", False),
            translation_service=translation_data.get("translation_service")
        )

        result = await service.create_translation(translation)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/translations/{translation_id}", response_model=Translation)
async def update_translation(
    translation_id: UUID,
    update_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Update a translation."""
    try:
        service = TranslationService(db)
        result = await service.update_translation(translation_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Translation not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translations/export", response_model=Dict[str, Dict[str, str]])
async def export_translations(
    language_codes: List[LanguageCode] = Query(...),
    namespace: Optional[str] = None,
    content_type: Optional[ContentType] = None,
    format: str = Query("json", regex="^(json|po|csv)$"),
    published_only: bool = True,
    db = Depends(get_db)
):
    """Export translations in various formats."""
    try:
        service = TranslationService(db)
        result = await service.export_translations(
            language_codes=language_codes,
            namespace=namespace,
            content_type=content_type,
            format=format,
            published_only=published_only
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translations/import", status_code=status.HTTP_201_CREATED)
async def import_translations(
    import_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Import translations from various formats."""
    try:
        service = TranslationService(db)
        result = await service.import_translations(import_data)
        return {"message": f"Successfully imported {result['imported']} translations", "details": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate/machine", response_model=Dict[str, str])
async def machine_translate(
    text: str,
    source_language: LanguageCode,
    target_languages: List[LanguageCode],
    service_name: str = "google",
    db = Depends(get_db)
):
    """Get machine translations for text."""
    try:
        mt_service = MachineTranslationService()
        results = {}

        for target_lang in target_languages:
            translation = await mt_service.translate(
                text=text,
                source_language=source_language,
                target_language=target_lang,
                service=service_name
            )
            results[target_lang.value] = translation

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=List[TranslationProject])
async def get_translation_projects(
    active_only: bool = True,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db = Depends(get_db)
):
    """Get translation projects."""
    try:
        service = TranslationService(db)
        projects = await service.get_translation_projects(
            active_only=active_only,
            page=page,
            per_page=per_page
        )
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects", response_model=TranslationProject, status_code=status.HTTP_201_CREATED)
async def create_translation_project(
    project_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a new translation project."""
    try:
        service = TranslationService(db)

        project = TranslationProject(
            name=project_data["name"],
            description=project_data.get("description"),
            source_language=LanguageCode(project_data.get("source_language", "en")),
            target_languages=[LanguageCode(lang) for lang in project_data["target_languages"]],
            project_manager_id=project_data.get("project_manager_id"),
            deadline=project_data.get("deadline"),
            priority=project_data.get("priority", 5)
        )

        result = await service.create_translation_project(project)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/search")
async def search_translation_memory(
    source_text: str,
    source_language: LanguageCode,
    target_language: LanguageCode,
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=50),
    db = Depends(get_db)
):
    """Search translation memory for similar translations."""
    try:
        service = TranslationService(db)
        results = await service.search_translation_memory(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            similarity_threshold=similarity_threshold,
            limit=limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/glossary", response_model=List[Glossary])
async def get_glossary_terms(
    source_language: Optional[LanguageCode] = None,
    target_language: Optional[LanguageCode] = None,
    domain: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db = Depends(get_db)
):
    """Get glossary terms."""
    try:
        service = TranslationService(db)
        terms = await service.get_glossary_terms(
            source_language=source_language,
            target_language=target_language,
            domain=domain,
            page=page,
            per_page=per_page
        )
        return terms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/glossary", response_model=Glossary, status_code=status.HTTP_201_CREATED)
async def create_glossary_term(
    glossary_data: Dict[str, Any],
    db = Depends(get_db)
):
    """Create a new glossary term."""
    try:
        service = TranslationService(db)

        glossary_term = Glossary(
            term=glossary_data["term"],
            translation=glossary_data["translation"],
            source_language=LanguageCode(glossary_data["source_language"]),
            target_language=LanguageCode(glossary_data["target_language"]),
            definition=glossary_data.get("definition"),
            context=glossary_data.get("context"),
            domain=glossary_data.get("domain"),
            do_not_translate=glossary_data.get("do_not_translate", False),
            alternative_translations=glossary_data.get("alternative_translations", [])
        )

        result = await service.create_glossary_term(glossary_term)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=Dict[str, Any])
async def get_translation_stats(
    language_code: Optional[LanguageCode] = None,
    namespace: Optional[str] = None,
    db = Depends(get_db)
):
    """Get translation statistics."""
    try:
        service = TranslationService(db)
        stats = await service.get_translation_stats(
            language_code=language_code,
            namespace=namespace
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))