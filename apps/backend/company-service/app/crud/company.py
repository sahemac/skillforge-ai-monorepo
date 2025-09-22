"""
Company CRUD operations for SkillForge AI Company Service
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.crud.base import CRUDBase
from app.models.company import CompanyProfile, CompanyTeamMember, CompanySubscription
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[CompanyProfile, CompanyCreate, CompanyUpdate]):
    """CRUD operations for CompanyProfile."""
    
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[CompanyProfile]:
        """Get company by slug."""
        return await self.get_by_field(db, "slug", slug)
    
    async def get_by_owner(
        self, 
        db: AsyncSession, 
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get companies owned by a user."""
        return await self.get_multi(
            db, 
            skip=skip, 
            limit=limit, 
            filters={"owner_id": owner_id, "is_active": True},
            order_by="created_at"
        )
    
    async def create(self, db: AsyncSession, obj_in: CompanyCreate, owner_id: UUID) -> CompanyProfile:
        """Create a company with owner."""
        create_data = obj_in.model_dump(exclude_unset=True)
        
        # Generate slug if not provided
        if not create_data.get("slug"):
            create_data["slug"] = self._generate_slug(create_data["name"])
        
        # Ensure slug is unique
        create_data["slug"] = await self._ensure_unique_slug(db, create_data["slug"])
        
        # Set owner
        create_data["owner_id"] = owner_id
        
        db_obj = CompanyProfile(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def search_companies(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CompanyProfile]:
        """Search companies by name, description, or skills."""
        query = select(CompanyProfile)
        
        # Apply base filters
        if filters:
            for field_name, field_value in filters.items():
                if hasattr(CompanyProfile, field_name) and field_value is not None:
                    field = getattr(CompanyProfile, field_name)
                    query = query.where(field == field_value)
        
        # Search conditions
        search_conditions = []
        if search_term:
            search_pattern = f"%{search_term}%"
            search_conditions.extend([
                CompanyProfile.name.ilike(search_pattern),
                CompanyProfile.description.ilike(search_pattern),
                CompanyProfile.slug.ilike(search_pattern)
            ])
        
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        # Apply pagination and ordering
        query = query.order_by(CompanyProfile.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_companies_by_skills(
        self,
        db: AsyncSession,
        skills: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get companies that focus on specific skills."""
        query = select(CompanyProfile).where(
            and_(
                CompanyProfile.is_active == True,
                CompanyProfile.skills_focus.op("&&")(skills)  # PostgreSQL array overlap operator
            )
        ).order_by(CompanyProfile.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    def _generate_slug(self, name: str) -> str:
        """Generate a URL-friendly slug from company name."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        return slug[:100]  # Limit to max length
    
    async def _ensure_unique_slug(self, db: AsyncSession, base_slug: str) -> str:
        """Ensure slug is unique by appending numbers if needed."""
        slug = base_slug
        counter = 1
        
        while await self.get_by_slug(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug


class CRUDTeamMember(CRUDBase[CompanyTeamMember, dict, dict]):
    """CRUD operations for CompanyTeamMember."""
    
    async def get_by_company_and_user(
        self, 
        db: AsyncSession, 
        company_id: UUID, 
        user_id: UUID
    ) -> Optional[CompanyTeamMember]:
        """Get team member by company and user."""
        result = await db.execute(
            select(CompanyTeamMember).where(
                and_(
                    CompanyTeamMember.company_id == company_id,
                    CompanyTeamMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_company_members(
        self,
        db: AsyncSession,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[CompanyTeamMember]:
        """Get all members of a company."""
        query = select(CompanyTeamMember).where(CompanyTeamMember.company_id == company_id)
        
        if active_only:
            query = query.where(CompanyTeamMember.is_active == True)
        
        query = query.order_by(CompanyTeamMember.joined_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_members_by_role(
        self,
        db: AsyncSession,
        company_id: UUID,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyTeamMember]:
        """Get company members by role."""
        query = select(CompanyTeamMember).where(
            and_(
                CompanyTeamMember.company_id == company_id,
                CompanyTeamMember.role == role,
                CompanyTeamMember.is_active == True
            )
        ).order_by(CompanyTeamMember.joined_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def add_member(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        role: str,
        title: Optional[str] = None,
        department: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        invited_by: Optional[UUID] = None
    ) -> CompanyTeamMember:
        """Add a new team member."""
        from datetime import datetime
        
        member_data = {
            "company_id": company_id,
            "user_id": user_id,
            "role": role,
            "title": title,
            "department": department,
            "permissions": permissions or [],
            "invited_by": invited_by,
            "invited_at": datetime.utcnow(),
            "invitation_accepted_at": datetime.utcnow()
        }
        
        return await self.create(db, member_data)
    
    async def remove_member(self, db: AsyncSession, member: CompanyTeamMember) -> None:
        """Remove (soft delete) a team member."""
        from datetime import datetime
        
        await self.update(db, member, {
            "is_active": False,
            "left_at": datetime.utcnow()
        })


class CRUDSubscription(CRUDBase[CompanySubscription, dict, dict]):
    """CRUD operations for CompanySubscription."""
    
    async def get_by_company(self, db: AsyncSession, company_id: UUID) -> Optional[CompanySubscription]:
        """Get active subscription for a company."""
        result = await db.execute(
            select(CompanySubscription).where(
                and_(
                    CompanySubscription.company_id == company_id,
                    CompanySubscription.status == "active"
                )
            ).order_by(CompanySubscription.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_by_stripe_subscription_id(
        self, 
        db: AsyncSession, 
        stripe_subscription_id: str
    ) -> Optional[CompanySubscription]:
        """Get subscription by Stripe subscription ID."""
        return await self.get_by_field(db, "stripe_subscription_id", stripe_subscription_id)


# Create instances
company = CRUDCompany(CompanyProfile)
team_member = CRUDTeamMember(CompanyTeamMember)
subscription = CRUDSubscription(CompanySubscription)