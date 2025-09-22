"""
Base CRUD operations for SkillForge AI Company Service
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
                    query = query.where(field == field_value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_field = getattr(self.model, order_by)
            query = query.order_by(order_field.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        
        db_obj = self.model(**create_data)
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
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False
    
    async def count(
        self, 
        db: AsyncSession, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records with optional filters."""
        query = select(func.count(self.model.id))
        
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(self.model, field_name) and field_value is not None:
                    field = getattr(self.model, field_name)
                    query = query.where(field == field_value)
        
        result = await db.execute(query)
        return result.scalar() or 0