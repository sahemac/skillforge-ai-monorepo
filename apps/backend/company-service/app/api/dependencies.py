"""
Dependencies for SkillForge AI Company Service API
Database sessions, pagination, search, etc.
"""

from typing import Optional, Generator, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging

from app.core.database import get_session

logger = logging.getLogger(__name__)


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session."""
    async for session in get_session():
        yield session


# Pagination dependency
class PaginationParams:
    """Pagination parameters."""
    
    def __init__(
        self, 
        page: int = 1,
        size: int = 20,
        max_size: int = 100
    ):
        if page < 1:
            page = 1
        if size < 1:
            size = 1
        if size > max_size:
            size = max_size
            
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


async def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, size=size)


# Search and filter dependencies
class SearchParams:
    """Search parameters."""
    
    def __init__(
        self,
        q: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "desc"
        self.filters = filters or {}
        
        # Validate sort order
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"


async def get_search_params(
    q: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> SearchParams:
    """Get search parameters."""
    return SearchParams(q=q, sort_by=sort_by, sort_order=sort_order)


# Request logging dependency
async def log_request(request: Request):
    """Log incoming requests."""
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Client: {request.client.host} - "
        f"User-Agent: {request.headers.get('user-agent', 'Unknown')}"
    )


# Content type validation
async def validate_json_content_type(request: Request):
    """Validate JSON content type for POST/PUT requests."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Content-Type must be application/json"
            )