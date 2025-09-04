"""
Base CRUD operations for SkillForge AI User Service
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from uuid import UUID
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[ModelType]):
        """Initialize CRUD with model class."""
        self.model = model
    
    async def get(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_by_field(
        self, 
        db: AsyncSession, 
        field_name: str, 
        field_value: Any
    ) -> Optional[ModelType]:
        """Get a single record by field name and value."""
        field = getattr(self.model, field_name)
        result = await db.execute(select(self.model).where(field == field_value))
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name) and field_value is not None:
                    field = getattr(self.model, field_name)
                    if isinstance(field_value, list):
                        query = query.where(field.in_(field_value))
                    else:
                        query = query.where(field == field_value)
        
        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                order_field = getattr(self.model, order_by[1:], None)
                if order_field:
                    query = query.order_by(order_field.desc())
            else:
                order_field = getattr(self.model, order_by, None)
                if order_field:
                    query = query.order_by(order_field.asc())
        else:
            # Default ordering by created_at if available
            if hasattr(self.model, "created_at"):
                query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count(
        self, 
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filtering."""
        query = select(func.count(self.model.id))
        
        # Apply filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name) and field_value is not None:
                    field = getattr(self.model, field_name)
                    if isinstance(field_value, list):
                        query = query.where(field.in_(field_value))
                    else:
                        query = query.where(field == field_value)
        
        result = await db.execute(query)
        return result.scalar()
    
    async def create(
        self, 
        db: AsyncSession, 
        obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new record."""
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump(exclude_unset=True)
        
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Update timestamp if available
        if hasattr(db_obj, "updated_at"):
            from datetime import datetime
            update_data["updated_at"] = datetime.utcnow()
        
        for field_name, field_value in update_data.items():
            if hasattr(db_obj, field_name):
                setattr(db_obj, field_name, field_value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Delete a record by ID."""
        result = await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()
        return result.rowcount > 0
    
    async def soft_delete(self, db: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Soft delete a record by setting is_active to False."""
        db_obj = await self.get(db, id)
        if db_obj and hasattr(db_obj, "is_active"):
            return await self.update(db, db_obj, {"is_active": False})
        return None
    
    async def exists(self, db: AsyncSession, id: UUID) -> bool:
        """Check if a record exists by ID."""
        result = await db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None
    
    async def search(
        self,
        db: AsyncSession,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Search records by term in specified fields."""
        query = select(self.model)
        
        # Build search conditions
        search_conditions = []
        for field_name in search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                search_conditions.append(field.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        # Apply additional filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name) and field_value is not None:
                    field = getattr(self.model, field_name)
                    if isinstance(field_value, list):
                        query = query.where(field.in_(field_value))
                    else:
                        query = query.where(field == field_value)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Default ordering by created_at if available
        if hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def bulk_create(
        self, 
        db: AsyncSession, 
        objs_in: List[Union[CreateSchemaType, Dict[str, Any]]]
    ) -> List[ModelType]:
        """Create multiple records in bulk."""
        db_objs = []
        for obj_in in objs_in:
            if isinstance(obj_in, dict):
                obj_data = obj_in
            else:
                obj_data = obj_in.model_dump(exclude_unset=True)
            
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)
        
        db.add_all(db_objs)
        await db.commit()
        
        for db_obj in db_objs:
            await db.refresh(db_obj)
        
        return db_objs
    
    async def bulk_update(
        self,
        db: AsyncSession,
        updates: List[Dict[str, Any]]
    ) -> int:
        """Bulk update records."""
        if not updates:
            return 0
        
        # Add timestamp if available
        if hasattr(self.model, "updated_at"):
            from datetime import datetime
            for update_item in updates:
                update_item["updated_at"] = datetime.utcnow()
        
        result = await db.execute(
            update(self.model),
            updates
        )
        await db.commit()
        return result.rowcount