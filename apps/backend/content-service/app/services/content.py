"""
Content service for business logic and data operations
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.content import (
    Content, ContentVersion, ContentInteraction, ContentCollection,
    ContentType, ContentStatus, ContentCategory
)
from ..schemas.content import (
    ContentCreate, ContentUpdate, ContentListResponse,
    ContentSearchQuery, ContentCollectionCreate, ContentCollectionUpdate,
    ContentAnalytics
)
from ..core.cache import get_redis
from ..core.database import get_db


class ContentService:
    """Service for content management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_content(self, content_data: ContentCreate, user_id: UUID) -> Content:
        """Create new content."""
        try:
            # Override author_id with current user
            content_data.metadata.author_id = user_id

            content = Content(
                title=content_data.title,
                description=content_data.description,
                content_type=content_data.content_type,
                category=content_data.category,
                body=content_data.body,
                media_url=content_data.media_url,
                attachments=content_data.attachments,
                metadata=content_data.metadata.dict()
            )

            self.db.add(content)
            await self.db.commit()
            await self.db.refresh(content)

            # Create initial version
            await self._create_version(content, user_id, "Initial version")

            # Clear related caches
            await self._clear_content_cache()

            return content

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to create content: {str(e)}")

    async def get_content_by_id(self, content_id: UUID) -> Optional[Content]:
        """Get content by ID with caching."""
        try:
            # Try cache first
            cache_key = f"content:{content_id}"
            redis = await get_redis()
            cached_content = await redis.get(cache_key)

            if cached_content:
                return Content.parse_raw(cached_content)

            # Get from database
            query = select(Content).where(
                and_(Content.id == content_id, Content.status != ContentStatus.ARCHIVED)
            )
            result = await self.db.execute(query)
            content = result.scalar_one_or_none()

            if content:
                # Cache for 1 hour
                await redis.setex(cache_key, 3600, content.json())
                # Increment view count
                await self._increment_view_count(content_id)

            return content

        except Exception as e:
            raise ValueError(f"Failed to get content: {str(e)}")

    async def update_content(self, content_id: UUID, content_data: ContentUpdate, user_id: UUID) -> Optional[Content]:
        """Update content."""
        try:
            query = select(Content).where(Content.id == content_id)
            result = await self.db.execute(query)
            content = result.scalar_one_or_none()

            if not content:
                return None

            # Check permissions (author or admin)
            if content.metadata.get("author_id") != str(user_id):
                raise ValueError("Permission denied: only content author can update")

            # Update fields
            update_data = content_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field != "metadata" and hasattr(content, field):
                    setattr(content, field, value)

            # Handle metadata update
            if content_data.metadata:
                updated_metadata = content.metadata.copy()
                updated_metadata.update(content_data.metadata.dict(exclude_unset=True))
                content.metadata = updated_metadata

            content.updated_at = datetime.utcnow()
            content.version += 1

            await self.db.commit()
            await self.db.refresh(content)

            # Create version record
            await self._create_version(content, user_id, f"Updated to version {content.version}")

            # Clear cache
            await self._clear_content_cache(content_id)

            return content

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to update content: {str(e)}")

    async def update_content_status(self, content_id: UUID, new_status: ContentStatus, user_id: UUID, change_summary: Optional[str] = None) -> Optional[Content]:
        """Update content status."""
        try:
            query = select(Content).where(Content.id == content_id)
            result = await self.db.execute(query)
            content = result.scalar_one_or_none()

            if not content:
                return None

            old_status = content.status
            content.status = new_status
            content.updated_at = datetime.utcnow()

            # Set published_at when content is published
            if new_status == ContentStatus.PUBLISHED and not content.published_at:
                content.published_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(content)

            # Create version record for status change
            summary = change_summary or f"Status changed from {old_status.value} to {new_status.value}"
            await self._create_version(content, user_id, summary)

            # Clear cache
            await self._clear_content_cache(content_id)

            return content

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to update content status: {str(e)}")

    async def archive_content(self, content_id: UUID, user_id: UUID) -> bool:
        """Archive content (soft delete)."""
        try:
            query = select(Content).where(Content.id == content_id)
            result = await self.db.execute(query)
            content = result.scalar_one_or_none()

            if not content:
                return False

            # Check permissions
            if content.metadata.get("author_id") != str(user_id):
                raise ValueError("Permission denied: only content author can archive")

            content.status = ContentStatus.ARCHIVED
            content.updated_at = datetime.utcnow()

            await self.db.commit()

            # Clear cache
            await self._clear_content_cache(content_id)

            return True

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to archive content: {str(e)}")

    async def get_content_list(self, search_query: ContentSearchQuery) -> ContentListResponse:
        """Get paginated content list with filtering."""
        try:
            query = select(Content).where(Content.status != ContentStatus.ARCHIVED)

            # Apply filters
            if search_query.content_type:
                query = query.where(Content.content_type == search_query.content_type)

            if search_query.category:
                query = query.where(Content.category == search_query.category)

            if search_query.status:
                query = query.where(Content.status == search_query.status)

            if search_query.author_id:
                query = query.where(text("metadata->>'author_id' = :author_id")).params(author_id=str(search_query.author_id))

            if search_query.difficulty_level:
                query = query.where(text("CAST(metadata->>'difficulty_level' AS INTEGER) = :level")).params(level=search_query.difficulty_level)

            if search_query.tags:
                # PostgreSQL JSONB array contains any of the tags
                for tag in search_query.tags:
                    query = query.where(text("metadata->'tags' ? :tag")).params(tag=tag)

            # Count total
            count_query = select(func.count(Content.id)).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply sorting
            sort_column = getattr(Content, search_query.sort_by, Content.created_at)
            if search_query.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (search_query.page - 1) * search_query.per_page
            query = query.offset(offset).limit(search_query.per_page)

            result = await self.db.execute(query)
            contents = result.scalars().all()

            pages = (total + search_query.per_page - 1) // search_query.per_page

            return ContentListResponse(
                items=contents,
                total=total,
                page=search_query.page,
                per_page=search_query.per_page,
                pages=pages
            )

        except Exception as e:
            raise ValueError(f"Failed to get content list: {str(e)}")

    async def search_content(self, search_query: ContentSearchQuery) -> ContentListResponse:
        """Search content by query string."""
        try:
            # Build base query with text search
            query = select(Content).where(
                and_(
                    Content.status == ContentStatus.PUBLISHED,
                    or_(
                        Content.title.ilike(f"%{search_query.query}%"),
                        Content.description.ilike(f"%{search_query.query}%"),
                        Content.body.ilike(f"%{search_query.query}%"),
                        text("metadata->'tags' @> :tag_query")
                    )
                )
            ).params(tag_query=f'["{search_query.query}"]')

            # Apply additional filters
            if search_query.content_type:
                query = query.where(Content.content_type == search_query.content_type)

            if search_query.category:
                query = query.where(Content.category == search_query.category)

            if search_query.difficulty_level:
                query = query.where(text("CAST(metadata->>'difficulty_level' AS INTEGER) = :level")).params(level=search_query.difficulty_level)

            # Count total
            count_query = select(func.count(Content.id)).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply sorting (relevance by default, then by specified field)
            sort_column = getattr(Content, search_query.sort_by, Content.created_at)
            if search_query.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

            # Apply pagination
            offset = (search_query.page - 1) * search_query.per_page
            query = query.offset(offset).limit(search_query.per_page)

            result = await self.db.execute(query)
            contents = result.scalars().all()

            pages = (total + search_query.per_page - 1) // search_query.per_page

            return ContentListResponse(
                items=contents,
                total=total,
                page=search_query.page,
                per_page=search_query.per_page,
                pages=pages
            )

        except Exception as e:
            raise ValueError(f"Failed to search content: {str(e)}")

    async def create_interaction(self, interaction_data: Dict[str, Any]) -> ContentInteraction:
        """Create content interaction."""
        try:
            interaction = ContentInteraction(**interaction_data)
            self.db.add(interaction)
            await self.db.commit()
            await self.db.refresh(interaction)

            # Update content analytics counters
            if interaction.interaction_type == "like":
                await self._increment_like_count(interaction.content_id)
            elif interaction.interaction_type == "download":
                await self._increment_download_count(interaction.content_id)

            return interaction

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to create interaction: {str(e)}")

    async def get_content_versions(self, content_id: UUID) -> List[ContentVersion]:
        """Get content version history."""
        try:
            query = select(ContentVersion).where(ContentVersion.content_id == content_id).order_by(desc(ContentVersion.version_number))
            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise ValueError(f"Failed to get content versions: {str(e)}")

    async def get_content_analytics(self, content_id: UUID, days: int = 30) -> Optional[ContentAnalytics]:
        """Get content analytics."""
        try:
            # Get basic content info
            content = await self.get_content_by_id(content_id)
            if not content:
                return None

            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # Get interaction statistics
            interaction_query = select(
                func.count(ContentInteraction.id).label("total_interactions"),
                func.count(func.distinct(ContentInteraction.user_id)).label("unique_users"),
                ContentInteraction.interaction_type
            ).where(
                and_(
                    ContentInteraction.content_id == content_id,
                    ContentInteraction.timestamp >= start_date
                )
            ).group_by(ContentInteraction.interaction_type)

            result = await self.db.execute(interaction_query)
            interactions = result.fetchall()

            # Process interaction data
            total_views = 0
            unique_views = 0
            total_likes = 0
            total_downloads = 0

            for interaction in interactions:
                if interaction.interaction_type == "view":
                    total_views = interaction.total_interactions
                    unique_views = interaction.unique_users
                elif interaction.interaction_type == "like":
                    total_likes = interaction.total_interactions
                elif interaction.interaction_type == "download":
                    total_downloads = interaction.total_interactions

            # Get popular tags from metadata
            popular_tags = content.metadata.get("tags", [])

            # Get view trend data (daily)
            view_trend_query = select(
                func.date(ContentInteraction.timestamp).label("date"),
                func.count(ContentInteraction.id).label("views")
            ).where(
                and_(
                    ContentInteraction.content_id == content_id,
                    ContentInteraction.interaction_type == "view",
                    ContentInteraction.timestamp >= start_date
                )
            ).group_by(func.date(ContentInteraction.timestamp)).order_by(func.date(ContentInteraction.timestamp))

            trend_result = await self.db.execute(view_trend_query)
            view_trend = [
                {"date": str(row.date), "views": row.views}
                for row in trend_result.fetchall()
            ]

            # Calculate engagement rate
            engagement_rate = 0.0
            if total_views > 0:
                engagement_rate = ((total_likes + total_downloads) / total_views) * 100

            return ContentAnalytics(
                content_id=content_id,
                total_views=total_views,
                unique_views=unique_views,
                total_likes=total_likes,
                total_downloads=total_downloads,
                average_rating=0.0,  # TODO: Implement rating system
                engagement_rate=engagement_rate,
                popular_tags=popular_tags,
                view_trend=view_trend
            )

        except Exception as e:
            raise ValueError(f"Failed to get content analytics: {str(e)}")

    # Collection methods
    async def create_collection(self, collection_data: ContentCollectionCreate, owner_id: UUID) -> ContentCollection:
        """Create content collection."""
        try:
            collection = ContentCollection(
                name=collection_data.name,
                description=collection_data.description,
                owner_id=owner_id,
                content_ids=collection_data.content_ids,
                is_public=collection_data.is_public,
                tags=collection_data.tags
            )

            self.db.add(collection)
            await self.db.commit()
            await self.db.refresh(collection)

            return collection

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to create collection: {str(e)}")

    async def get_collections(self, page: int = 1, per_page: int = 20, owner_id: Optional[UUID] = None, is_public: Optional[bool] = None) -> List[ContentCollection]:
        """Get content collections."""
        try:
            query = select(ContentCollection)

            if owner_id:
                query = query.where(ContentCollection.owner_id == owner_id)

            if is_public is not None:
                query = query.where(ContentCollection.is_public == is_public)

            # Apply pagination
            offset = (page - 1) * per_page
            query = query.offset(offset).limit(per_page).order_by(desc(ContentCollection.created_at))

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise ValueError(f"Failed to get collections: {str(e)}")

    async def get_collection_by_id(self, collection_id: UUID) -> Optional[ContentCollection]:
        """Get collection by ID."""
        try:
            query = select(ContentCollection).where(ContentCollection.id == collection_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            raise ValueError(f"Failed to get collection: {str(e)}")

    async def update_collection(self, collection_id: UUID, collection_data: ContentCollectionUpdate, user_id: UUID) -> Optional[ContentCollection]:
        """Update collection."""
        try:
            query = select(ContentCollection).where(ContentCollection.id == collection_id)
            result = await self.db.execute(query)
            collection = result.scalar_one_or_none()

            if not collection:
                return None

            # Check permissions
            if collection.owner_id != user_id:
                raise ValueError("Permission denied: only collection owner can update")

            # Update fields
            update_data = collection_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(collection, field):
                    setattr(collection, field, value)

            collection.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(collection)

            return collection

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to update collection: {str(e)}")

    async def delete_collection(self, collection_id: UUID, user_id: UUID) -> bool:
        """Delete collection."""
        try:
            query = select(ContentCollection).where(ContentCollection.id == collection_id)
            result = await self.db.execute(query)
            collection = result.scalar_one_or_none()

            if not collection:
                return False

            # Check permissions
            if collection.owner_id != user_id:
                raise ValueError("Permission denied: only collection owner can delete")

            await self.db.delete(collection)
            await self.db.commit()

            return True

        except Exception as e:
            await self.db.rollback()
            raise ValueError(f"Failed to delete collection: {str(e)}")

    # Private helper methods
    async def _create_version(self, content: Content, user_id: UUID, change_summary: str):
        """Create content version record."""
        version = ContentVersion(
            content_id=content.id,
            version_number=content.version,
            title=content.title,
            body=content.body,
            metadata=content.metadata,
            created_by=user_id,
            change_summary=change_summary
        )
        self.db.add(version)
        await self.db.commit()

    async def _increment_view_count(self, content_id: UUID):
        """Increment content view count."""
        query = select(Content).where(Content.id == content_id)
        result = await self.db.execute(query)
        content = result.scalar_one_or_none()

        if content:
            content.view_count += 1
            await self.db.commit()

    async def _increment_like_count(self, content_id: UUID):
        """Increment content like count."""
        query = select(Content).where(Content.id == content_id)
        result = await self.db.execute(query)
        content = result.scalar_one_or_none()

        if content:
            content.like_count += 1
            await self.db.commit()

    async def _increment_download_count(self, content_id: UUID):
        """Increment content download count."""
        query = select(Content).where(Content.id == content_id)
        result = await self.db.execute(query)
        content = result.scalar_one_or_none()

        if content:
            content.download_count += 1
            await self.db.commit()

    async def _clear_content_cache(self, content_id: Optional[UUID] = None):
        """Clear content-related cache."""
        redis = await get_redis()
        if content_id:
            await redis.delete(f"content:{content_id}")
        else:
            # Clear pattern-based cache
            keys = await redis.keys("content:*")
            if keys:
                await redis.delete(*keys)