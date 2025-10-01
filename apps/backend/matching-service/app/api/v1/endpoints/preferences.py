"""
User preferences endpoints for SkillForge AI Matching Service
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_session
from app.models import (
    UserPreference,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    BulkPreferenceUpdate,
    PreferenceStats,
    PreferenceTemplate,
    MatchingProfile,
    PreferenceType
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=UserPreferenceResponse)
@limiter.limit("30/minute")
async def create_preference(
    preference_data: UserPreferenceCreate,
    session: Session = Depends(get_session)
):
    """Create a new user preference."""

    try:
        # Validate that the profile exists
        profile = session.exec(
            select(MatchingProfile).where(MatchingProfile.id == preference_data.profile_id)
        ).first()

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Matching profile not found"
            )

        # Check for duplicate preferences
        existing = session.exec(
            select(UserPreference).where(
                UserPreference.user_id == preference_data.user_id,
                UserPreference.preference_type == preference_data.preference_type,
                UserPreference.preference_name == preference_data.preference_name,
                UserPreference.is_active == True
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Active preference already exists: {preference_data.preference_name}"
            )

        # Create preference
        preference = UserPreference(**preference_data.model_dump())
        session.add(preference)
        session.commit()
        session.refresh(preference)

        logger.info(f"Created preference {preference.id} for user {preference_data.user_id}")

        return UserPreferenceResponse.model_validate(preference)

    except Exception as e:
        logger.error(f"Error creating preference: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating preference: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[UserPreferenceResponse])
@limiter.limit("60/minute")
async def get_user_preferences(
    user_id: str,
    preference_type: Optional[str] = None,
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Get all preferences for a user."""

    try:
        query = select(UserPreference).where(UserPreference.user_id == user_id)

        if active_only:
            query = query.where(UserPreference.is_active == True)

        if preference_type:
            query = query.where(UserPreference.preference_type == preference_type)

        preferences = session.exec(query).all()

        return [
            UserPreferenceResponse.model_validate(pref)
            for pref in preferences
        ]

    except Exception as e:
        logger.error(f"Error getting preferences for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user preferences: {str(e)}"
        )


@router.put("/{preference_id}", response_model=UserPreferenceResponse)
@limiter.limit("30/minute")
async def update_preference(
    preference_id: str,
    preference_update: UserPreferenceUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing user preference."""

    try:
        preference = session.exec(
            select(UserPreference).where(UserPreference.id == preference_id)
        ).first()

        if not preference:
            raise HTTPException(
                status_code=404,
                detail="Preference not found"
            )

        # Update fields
        update_data = preference_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)

        session.add(preference)
        session.commit()
        session.refresh(preference)

        logger.info(f"Updated preference {preference_id}")

        return UserPreferenceResponse.model_validate(preference)

    except Exception as e:
        logger.error(f"Error updating preference {preference_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating preference: {str(e)}"
        )


@router.delete("/{preference_id}")
@limiter.limit("20/minute")
async def delete_preference(
    preference_id: str,
    hard_delete: bool = False,
    session: Session = Depends(get_session)
):
    """Delete a user preference (soft delete by default)."""

    try:
        preference = session.exec(
            select(UserPreference).where(UserPreference.id == preference_id)
        ).first()

        if not preference:
            raise HTTPException(
                status_code=404,
                detail="Preference not found"
            )

        if hard_delete:
            session.delete(preference)
        else:
            preference.is_active = False
            session.add(preference)

        session.commit()

        action = "deleted" if hard_delete else "deactivated"
        logger.info(f"Preference {preference_id} {action}")

        return {"message": f"Preference {action} successfully"}

    except Exception as e:
        logger.error(f"Error deleting preference {preference_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting preference: {str(e)}"
        )


@router.post("/bulk-update")
@limiter.limit("10/minute")
async def bulk_update_preferences(
    bulk_update: BulkPreferenceUpdate,
    session: Session = Depends(get_session)
):
    """Bulk update multiple preferences."""

    try:
        updated_count = 0
        errors = []

        for pref_update in bulk_update.preferences:
            try:
                preference_id = pref_update.get("id")
                if not preference_id:
                    errors.append({"error": "Missing preference ID", "data": pref_update})
                    continue

                preference = session.exec(
                    select(UserPreference).where(UserPreference.id == preference_id)
                ).first()

                if not preference:
                    errors.append({"error": f"Preference {preference_id} not found", "id": preference_id})
                    continue

                # Update fields
                for field, value in pref_update.items():
                    if field != "id" and hasattr(preference, field):
                        setattr(preference, field, value)

                session.add(preference)
                updated_count += 1

            except Exception as e:
                errors.append({"error": str(e), "data": pref_update})

        session.commit()

        return {
            "message": f"Bulk update completed",
            "updated_count": updated_count,
            "errors": errors,
            "success_rate": updated_count / len(bulk_update.preferences) if bulk_update.preferences else 0
        }

    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in bulk update: {str(e)}"
        )


@router.get("/stats/{user_id}", response_model=PreferenceStats)
@limiter.limit("30/minute")
async def get_preference_stats(
    user_id: str,
    session: Session = Depends(get_session)
):
    """Get statistics about user preferences."""

    try:
        preferences = session.exec(
            select(UserPreference).where(UserPreference.user_id == user_id)
        ).all()

        if not preferences:
            return PreferenceStats(
                user_id=user_id,
                total_preferences=0,
                active_preferences=0,
                mandatory_preferences=0,
                preference_types={},
                avg_priority=0.0,
                avg_weight=0.0,
                last_updated=None
            )

        active_prefs = [p for p in preferences if p.is_active]
        mandatory_prefs = [p for p in preferences if p.is_mandatory]

        # Count by type
        type_counts = {}
        for pref in active_prefs:
            type_counts[pref.preference_type] = type_counts.get(pref.preference_type, 0) + 1

        # Calculate averages
        avg_priority = sum(p.priority for p in active_prefs) / len(active_prefs) if active_prefs else 0.0
        avg_weight = sum(p.weight for p in active_prefs) / len(active_prefs) if active_prefs else 0.0

        # Find last updated
        last_updated = max(p.updated_at for p in preferences if p.updated_at) if preferences else None

        return PreferenceStats(
            user_id=user_id,
            total_preferences=len(preferences),
            active_preferences=len(active_prefs),
            mandatory_preferences=len(mandatory_prefs),
            preference_types=type_counts,
            avg_priority=avg_priority,
            avg_weight=avg_weight,
            last_updated=str(last_updated) if last_updated else None
        )

    except Exception as e:
        logger.error(f"Error getting preference stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting preference stats: {str(e)}"
        )


@router.get("/templates", response_model=List[PreferenceTemplate])
@limiter.limit("30/minute")
async def get_preference_templates():
    """Get available preference templates."""

    templates = [
        PreferenceTemplate(
            template_name="Remote Work Preference",
            template_description="Preference for remote work arrangements",
            preference_type=PreferenceType.WORK_MODE,
            default_value={"work_mode": "remote", "flexibility": "required"},
            default_priority=1,
            default_weight=2.0,
            is_mandatory=True
        ),
        PreferenceTemplate(
            template_name="Salary Range",
            template_description="Expected salary range preference",
            preference_type=PreferenceType.SALARY,
            default_value={"min_salary": 50000, "max_salary": 100000, "currency": "USD"},
            default_priority=2,
            default_weight=1.5,
            is_mandatory=False
        ),
        PreferenceTemplate(
            template_name="Location Preference",
            template_description="Geographic location preferences",
            preference_type=PreferenceType.LOCATION,
            default_value={"locations": [], "max_distance_km": 50},
            default_priority=3,
            default_weight=1.0,
            is_mandatory=False
        ),
        PreferenceTemplate(
            template_name="Required Skills",
            template_description="Must-have skills for matching",
            preference_type=PreferenceType.SKILLS,
            default_value={"required_skills": [], "nice_to_have": []},
            default_priority=1,
            default_weight=2.5,
            is_mandatory=True
        ),
        PreferenceTemplate(
            template_name="Experience Level",
            template_description="Required experience level",
            preference_type=PreferenceType.EXPERIENCE_LEVEL,
            default_value={"min_level": "intermediate", "max_level": "expert"},
            default_priority=2,
            default_weight=1.0,
            is_mandatory=False
        ),
        PreferenceTemplate(
            template_name="Project Type",
            template_description="Preferred types of projects",
            preference_type=PreferenceType.PROJECT_TYPE,
            default_value={"types": ["web_development", "mobile_app"], "exclude": []},
            default_priority=2,
            default_weight=1.5,
            is_mandatory=False
        )
    ]

    return templates


@router.post("/from-template")
@limiter.limit("20/minute")
async def create_preference_from_template(
    user_id: str,
    profile_id: str,
    template_name: str,
    custom_values: Optional[Dict[str, Any]] = None,
    session: Session = Depends(get_session)
):
    """Create a preference from a template."""

    try:
        # Get templates
        templates = await get_preference_templates()
        template = next((t for t in templates if t.template_name == template_name), None)

        if not template:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )

        # Merge custom values with template defaults
        preference_value = template.default_value.copy()
        if custom_values:
            preference_value.update(custom_values)

        # Create preference
        preference_data = UserPreferenceCreate(
            user_id=user_id,
            profile_id=profile_id,
            preference_type=template.preference_type,
            preference_name=template.template_name,
            preference_value=preference_value,
            priority=template.default_priority,
            weight=template.default_weight,
            is_mandatory=template.is_mandatory,
            preference_metadata={
                "created_from_template": template_name,
                "template_description": template.template_description
            }
        )

        return await create_preference(preference_data, session)

    except Exception as e:
        logger.error(f"Error creating preference from template: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating preference from template: {str(e)}"
        )