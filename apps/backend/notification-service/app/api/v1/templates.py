"""
Notification Templates API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas.notification import (
    NotificationTemplateCreate,
    NotificationTemplateUpdate,
    NotificationTemplateResponse,
    NotificationType
)

router = APIRouter()

# Mock database session
def get_db():
    """Mock database session"""
    return None


# Mock template service
class TemplateService:
    """Mock template service"""

    @staticmethod
    async def get_templates() -> List[dict]:
        """Get all templates"""
        return [
            {
                "id": 1,
                "template_name": "Welcome Email",
                "template_key": "welcome_email",
                "subject_template": "Welcome to SkillForge AI, {{user_name}}!",
                "content_template": "Hi {{user_name}}, welcome to SkillForge AI! Start your learning journey today.",
                "html_template": "<h1>Welcome {{user_name}}!</h1><p>Start your learning journey today.</p>",
                "notification_type": "email",
                "priority": "normal",
                "category": "welcome",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 2,
                "template_name": "Course Completion",
                "template_key": "course_completed",
                "subject_template": "Congratulations! You completed {{course_name}}",
                "content_template": "Great job completing {{course_name}}! Your certificate is ready.",
                "notification_type": "email",
                "priority": "normal",
                "category": "achievement",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 3,
                "template_name": "Password Reset",
                "template_key": "password_reset",
                "subject_template": "Reset your SkillForge AI password",
                "content_template": "Click here to reset your password: {{reset_link}}",
                "html_template": "<p>Click <a href='{{reset_link}}'>here</a> to reset your password.</p>",
                "notification_type": "email",
                "priority": "high",
                "category": "security",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]

    @staticmethod
    async def get_template_by_key(template_key: str) -> dict:
        """Get template by key"""
        templates = await TemplateService.get_templates()
        for template in templates:
            if template["template_key"] == template_key:
                return template
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )


@router.get("/",
    response_model=List[NotificationTemplateResponse],
    summary="Get all notification templates")
async def get_templates(
    notification_type: Optional[NotificationType] = Query(None, description="Filter by type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active templates"),
    db: Session = Depends(get_db)
):
    """
    Get all notification templates with optional filtering.

    - **notification_type**: Filter by notification type
    - **category**: Filter by category
    - **active_only**: Show only active templates
    """
    try:
        templates = await TemplateService.get_templates()

        # Apply filters
        if notification_type:
            templates = [t for t in templates if t["notification_type"] == notification_type]

        if category:
            templates = [t for t in templates if t.get("category") == category]

        if active_only:
            templates = [t for t in templates if t.get("is_active", True)]

        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )


@router.get("/{template_id}",
    response_model=NotificationTemplateResponse,
    summary="Get template by ID")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific template by ID."""
    templates = await TemplateService.get_templates()
    for template in templates:
        if template["id"] == template_id:
            return template

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Template not found"
    )


@router.get("/key/{template_key}",
    response_model=NotificationTemplateResponse,
    summary="Get template by key")
async def get_template_by_key(
    template_key: str,
    db: Session = Depends(get_db)
):
    """Get a template by its unique key."""
    try:
        template = await TemplateService.get_template_by_key(template_key)
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.post("/",
    response_model=NotificationTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification template")
async def create_template(
    template: NotificationTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new notification template.

    - **template_name**: Human-readable template name
    - **template_key**: Unique key for the template
    - **subject_template**: Subject template with variables
    - **content_template**: Content template with variables
    - **html_template**: Optional HTML template
    - **notification_type**: Type of notification
    """
    try:
        # In production, save to database
        new_template = {
            "id": 999,  # Mock ID
            **template.dict(),
            "created_at": datetime.now().isoformat()
        }

        return new_template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.patch("/{template_id}",
    response_model=NotificationTemplateResponse,
    summary="Update notification template")
async def update_template(
    template_id: int,
    template_update: NotificationTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing template."""
    try:
        # Mock update
        templates = await TemplateService.get_templates()
        for template in templates:
            if template["id"] == template_id:
                # Update fields
                update_data = template_update.dict(exclude_unset=True)
                template.update(update_data)
                template["updated_at"] = datetime.now().isoformat()
                return template

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification template")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a template."""
    # In production, delete from database
    return


@router.post("/{template_key}/preview",
    summary="Preview template with data")
async def preview_template(
    template_key: str,
    template_data: dict,
    db: Session = Depends(get_db)
):
    """
    Preview how a template will look with specific data.

    - **template_key**: Template key to preview
    - **template_data**: Variables to substitute in template
    """
    try:
        template = await TemplateService.get_template_by_key(template_key)

        # Simple template substitution (in production, use Jinja2)
        subject = template["subject_template"]
        content = template["content_template"]
        html_content = template.get("html_template", "")

        for key, value in template_data.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            content = content.replace(placeholder, str(value))
            if html_content:
                html_content = html_content.replace(placeholder, str(value))

        return {
            "template_key": template_key,
            "subject": subject,
            "content": content,
            "html_content": html_content,
            "notification_type": template["notification_type"],
            "template_data": template_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview template: {str(e)}"
        )