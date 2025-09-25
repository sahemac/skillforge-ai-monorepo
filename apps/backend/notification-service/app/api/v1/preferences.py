"""
Notification Preferences API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.notification import (
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse
)

router = APIRouter()

# Mock database session
def get_db():
    """Mock database session"""
    return None


# Mock preferences service
class PreferencesService:
    """Mock preferences service"""

    @staticmethod
    async def get_user_preferences(user_id: int) -> dict:
        """Get user preferences"""
        # Mock default preferences
        return {
            "id": 1,
            "user_id": user_id,
            "email_notifications": True,
            "email_marketing": True,
            "email_updates": True,
            "sms_notifications": False,
            "sms_urgent_only": True,
            "push_notifications": True,
            "push_sound": True,
            "push_vibration": True,
            "in_app_notifications": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "UTC",
            "created_at": "2024-01-15T10:00:00Z"
        }

    @staticmethod
    async def update_user_preferences(user_id: int, preferences: dict) -> dict:
        """Update user preferences"""
        current_prefs = await PreferencesService.get_user_preferences(user_id)
        current_prefs.update(preferences)
        current_prefs["updated_at"] = datetime.now().isoformat()
        return current_prefs


@router.get("/{user_id}",
    response_model=NotificationPreferenceResponse,
    summary="Get user notification preferences")
async def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get notification preferences for a specific user.

    - **user_id**: User ID to get preferences for
    """
    try:
        preferences = await PreferencesService.get_user_preferences(user_id)
        return preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.patch("/{user_id}",
    response_model=NotificationPreferenceResponse,
    summary="Update user notification preferences")
async def update_user_preferences(
    user_id: int,
    preferences: NotificationPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update notification preferences for a specific user.

    - **user_id**: User ID to update preferences for
    - **email_notifications**: Enable/disable email notifications
    - **email_marketing**: Enable/disable marketing emails
    - **sms_notifications**: Enable/disable SMS notifications
    - **push_notifications**: Enable/disable push notifications
    - **quiet_hours_start**: Start time for quiet hours (HH:MM)
    - **quiet_hours_end**: End time for quiet hours (HH:MM)
    - **timezone**: User timezone
    """
    try:
        update_data = preferences.dict(exclude_unset=True)
        updated_preferences = await PreferencesService.update_user_preferences(
            user_id, update_data
        )
        return updated_preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.post("/{user_id}/reset",
    response_model=NotificationPreferenceResponse,
    summary="Reset user preferences to defaults")
async def reset_user_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Reset user notification preferences to default values."""
    try:
        # Create default preferences
        default_preferences = {
            "email_notifications": True,
            "email_marketing": False,
            "email_updates": True,
            "sms_notifications": False,
            "sms_urgent_only": True,
            "push_notifications": True,
            "push_sound": True,
            "push_vibration": True,
            "in_app_notifications": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "UTC"
        }

        updated_preferences = await PreferencesService.update_user_preferences(
            user_id, default_preferences
        )
        return updated_preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset preferences: {str(e)}"
        )


@router.post("/{user_id}/unsubscribe",
    summary="Unsubscribe from all notifications")
async def unsubscribe_user(
    user_id: int,
    notification_type: str = "all",
    db: Session = Depends(get_db)
):
    """
    Unsubscribe user from notifications.

    - **user_id**: User ID to unsubscribe
    - **notification_type**: Type to unsubscribe from ('all', 'email', 'sms', 'push')
    """
    try:
        if notification_type == "all":
            unsubscribe_data = {
                "email_notifications": False,
                "sms_notifications": False,
                "push_notifications": False,
                "email_marketing": False
            }
        elif notification_type == "email":
            unsubscribe_data = {
                "email_notifications": False,
                "email_marketing": False
            }
        elif notification_type == "sms":
            unsubscribe_data = {"sms_notifications": False}
        elif notification_type == "push":
            unsubscribe_data = {"push_notifications": False}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid notification_type. Use 'all', 'email', 'sms', or 'push'"
            )

        await PreferencesService.update_user_preferences(user_id, unsubscribe_data)

        return {
            "message": f"Successfully unsubscribed from {notification_type} notifications",
            "user_id": user_id,
            "notification_type": notification_type,
            "unsubscribed_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unsubscribe user: {str(e)}"
        )