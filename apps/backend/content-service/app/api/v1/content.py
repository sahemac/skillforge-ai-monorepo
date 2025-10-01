"""
Content API endpoints for SkillForge AI Content Service
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...models.content import Content, ContentStatus
from ...schemas.content import (
    ContentCreate, ContentUpdate, ContentStatusUpdate,
    ContentResponse, ContentListResponse, ContentSearchQuery,
    ContentInteractionCreate, ContentInteractionResponse,
    ContentCollectionCreate, ContentCollectionUpdate, ContentCollectionResponse,
    ContentVersionResponse, ContentAnalytics
)
from ...services.content import ContentService
from ...core.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: ContentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new content."""
    try:
        content_service = ContentService(db)
        content = await content_service.create_content(content_data, current_user["user_id"])
        return content
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ContentListResponse)
async def get_content_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    author_id: Optional[UUID] = None,
    tags: Optional[List[str]] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated content list with filtering."""
    try:
        search_query = ContentSearchQuery(
            page=page,
            per_page=per_page,
            content_type=content_type,
            category=category,
            status=status,
            author_id=author_id,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order
        )

        content_service = ContentService(db)
        result = await content_service.get_content_list(search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/search", response_model=ContentListResponse)
async def search_content(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    difficulty_level: Optional[int] = Query(None, ge=1, le=5),
    tags: Optional[List[str]] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Search content by query string."""
    try:
        search_query = ContentSearchQuery(
            query=query,
            page=page,
            per_page=per_page,
            content_type=content_type,
            category=category,
            difficulty_level=difficulty_level,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order
        )

        content_service = ContentService(db)
        result = await content_service.search_content(search_query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content by ID."""
    try:
        content_service = ContentService(db)

        # Track view interaction
        await content_service.create_interaction({
            "content_id": content_id,
            "user_id": current_user["user_id"],
            "interaction_type": "view"
        })

        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return content
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update content."""
    try:
        content_service = ContentService(db)
        content = await content_service.update_content(content_id, content_data, current_user["user_id"])
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return content
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{content_id}/status", response_model=ContentResponse)
async def update_content_status(
    content_id: UUID,
    status_data: ContentStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update content status."""
    try:
        content_service = ContentService(db)
        content = await content_service.update_content_status(
            content_id,
            status_data.status,
            current_user["user_id"],
            status_data.change_summary
        )
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return content
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete content (soft delete - archive)."""
    try:
        content_service = ContentService(db)
        success = await content_service.archive_content(content_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Content not found")

        return JSONResponse(status_code=204, content={"message": "Content archived successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{content_id}/interactions", response_model=ContentInteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    content_id: UUID,
    interaction_data: ContentInteractionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create content interaction."""
    try:
        # Override content_id from URL
        interaction_data.content_id = content_id

        content_service = ContentService(db)
        interaction = await content_service.create_interaction({
            **interaction_data.dict(),
            "user_id": current_user["user_id"]
        })
        return interaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{content_id}/versions", response_model=List[ContentVersionResponse])
async def get_content_versions(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get content version history."""
    try:
        content_service = ContentService(db)
        versions = await content_service.get_content_versions(content_id)
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{content_id}/analytics", response_model=ContentAnalytics)
async def get_content_analytics(
    content_id: UUID,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """Get content analytics."""
    try:
        content_service = ContentService(db)
        analytics = await content_service.get_content_analytics(content_id, days)
        if not analytics:
            raise HTTPException(status_code=404, detail="Content not found")

        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Content Collections endpoints
@router.post("/collections", response_model=ContentCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: ContentCollectionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create content collection."""
    try:
        content_service = ContentService(db)
        collection = await content_service.create_collection(collection_data, current_user["user_id"])
        return collection
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/collections", response_model=List[ContentCollectionResponse])
async def get_collections(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    owner_id: Optional[UUID] = None,
    is_public: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get content collections."""
    try:
        content_service = ContentService(db)
        collections = await content_service.get_collections(
            page=page,
            per_page=per_page,
            owner_id=owner_id,
            is_public=is_public
        )
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/collections/{collection_id}", response_model=ContentCollectionResponse)
async def get_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get collection by ID."""
    try:
        content_service = ContentService(db)
        collection = await content_service.get_collection_by_id(collection_id)
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/collections/{collection_id}", response_model=ContentCollectionResponse)
async def update_collection(
    collection_id: UUID,
    collection_data: ContentCollectionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update collection."""
    try:
        content_service = ContentService(db)
        collection = await content_service.update_collection(collection_id, collection_data, current_user["user_id"])
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        return collection
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete collection."""
    try:
        content_service = ContentService(db)
        success = await content_service.delete_collection(collection_id, current_user["user_id"])
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found")

        return JSONResponse(status_code=204, content={"message": "Collection deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")