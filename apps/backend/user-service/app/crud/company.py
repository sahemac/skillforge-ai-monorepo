"""
Company CRUD operations for SkillForge AI User Service
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.company_simple import (
    CompanyProfile, 
    TeamMember, 
    Subscription,
    CompanySize,
    IndustryType
)
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[CompanyProfile, CompanyCreate, CompanyUpdate]):
    """CRUD operations for CompanyProfile model."""
    
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[CompanyProfile]:
        """Get company by slug."""
        result = await db.execute(
            select(CompanyProfile).where(CompanyProfile.slug == slug)
        )
        return result.scalar_one_or_none()
    
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
            filters={"owner_id": owner_id}
        )
    
    async def create(self, db: AsyncSession, obj_in: CompanyCreate, owner_id: UUID) -> CompanyProfile:
        """Create a new company profile."""
        company_data = obj_in.model_dump(exclude_unset=True)
        company_data["owner_id"] = owner_id
        
        # Generate slug if not provided
        if not company_data.get("slug"):
            base_slug = company_data["name"].lower()
            slug = "".join(c if c.isalnum() or c == "-" else "-" for c in base_slug)
            slug = "-".join(filter(None, slug.split("-")))
            company_data["slug"] = slug[:100]
        
        # Ensure slug is unique
        company_data["slug"] = await self._ensure_unique_slug(db, company_data["slug"])
        
        db_company = CompanyProfile(**company_data)
        db.add(db_company)
        await db.commit()
        await db.refresh(db_company)
        
        return db_company
    
    async def _ensure_unique_slug(self, db: AsyncSession, base_slug: str) -> str:
        """Ensure slug is unique by appending numbers if necessary."""
        original_slug = base_slug
        counter = 1
        
        while await self.get_by_slug(db, base_slug):
            base_slug = f"{original_slug}-{counter}"
            counter += 1
        
        return base_slug
    
    async def verify_company(self, db: AsyncSession, company: CompanyProfile) -> CompanyProfile:
        """Verify a company profile."""
        return await self.update(
            db,
            company,
            {
                "is_verified": True,
                "verified_at": datetime.utcnow()
            }
        )
    
    async def search_companies(
        self,
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CompanyProfile]:
        """Search companies by name or description."""
        search_fields = ["name", "description"]
        return await self.search(
            db,
            search_term,
            search_fields,
            skip=skip,
            limit=limit,
            filters=filters
        )
    
    async def get_by_industry(
        self,
        db: AsyncSession,
        industry: IndustryType,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get companies by industry."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"industry": industry, "is_active": True}
        )
    
    async def get_by_size(
        self,
        db: AsyncSession,
        company_size: CompanySize,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get companies by size."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"company_size": company_size, "is_active": True}
        )
    
    async def get_verified_companies(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get verified companies."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"is_verified": True, "is_active": True}
        )
    
    async def get_companies_by_skills(
        self,
        db: AsyncSession,
        skills: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[CompanyProfile]:
        """Get companies by skills focus."""
        query = select(CompanyProfile).where(
            and_(
                CompanyProfile.is_active.is_(True),
                CompanyProfile.skills_focus.op("&&")(skills)  # PostgreSQL array overlap
            )
        ).offset(skip).limit(limit).order_by(CompanyProfile.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()


class CRUDTeamMember(CRUDBase[TeamMember, dict, dict]):
    """CRUD operations for TeamMember model."""
    
    async def get_by_company_and_user(
        self, 
        db: AsyncSession, 
        company_id: UUID, 
        user_id: UUID
    ) -> Optional[TeamMember]:
        """Get team member by company and user ID."""
        result = await db.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.company_id == company_id,
                    TeamMember.user_id == user_id,
                    TeamMember.is_active.is_(True)
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
    ) -> List[TeamMember]:
        """Get all members of a company."""
        filters = {"company_id": company_id}
        if active_only:
            filters["is_active"] = True
        
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )
    
    async def get_user_companies(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[TeamMember]:
        """Get all companies a user is member of."""
        filters = {"user_id": user_id}
        if active_only:
            filters["is_active"] = True
        
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters
        )
    
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
    ) -> TeamMember:
        """Add a member to a company."""
        member_data = {
            "company_id": company_id,
            "user_id": user_id,
            "role": role,
            "title": title,
            "department": department,
            "permissions": permissions or [],
            "is_active": True,
            "joined_at": datetime.utcnow(),
            "invited_by": invited_by,
            "invited_at": datetime.utcnow() if invited_by else None,
            "invitation_accepted_at": datetime.utcnow() if not invited_by else None
        }
        
        return await self.create(db, member_data)
    
    async def accept_invitation(
        self, 
        db: AsyncSession, 
        member: TeamMember
    ) -> TeamMember:
        """Accept team member invitation."""
        return await self.update(
            db,
            member,
            {"invitation_accepted_at": datetime.utcnow()}
        )
    
    async def remove_member(
        self, 
        db: AsyncSession, 
        member: TeamMember
    ) -> TeamMember:
        """Remove a member from a company."""
        return await self.update(
            db,
            member,
            {
                "is_active": False,
                "left_at": datetime.utcnow()
            }
        )
    
    async def update_member_role(
        self,
        db: AsyncSession,
        member: TeamMember,
        role: str,
        permissions: Optional[List[str]] = None
    ) -> TeamMember:
        """Update member role and permissions."""
        update_data = {"role": role}
        if permissions is not None:
            update_data["permissions"] = permissions
        
        return await self.update(db, member, update_data)
    
    async def get_members_by_role(
        self,
        db: AsyncSession,
        company_id: UUID,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TeamMember]:
        """Get company members by role."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={
                "company_id": company_id,
                "role": role,
                "is_active": True
            }
        )


class CRUDSubscription(CRUDBase[Subscription, dict, dict]):
    """CRUD operations for Subscription model."""
    
    async def get_by_company(
        self, 
        db: AsyncSession, 
        company_id: UUID
    ) -> Optional[Subscription]:
        """Get active subscription for a company."""
        result = await db.execute(
            select(Subscription)
            .where(Subscription.company_id == company_id)
            .order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def create_subscription(
        self,
        db: AsyncSession,
        company_id: UUID,
        plan_name: str,
        plan_price: float,
        billing_cycle: str,
        seats_included: int = 1,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
        stripe_subscription_id: Optional[str] = None,
        stripe_customer_id: Optional[str] = None
    ) -> Subscription:
        """Create a new subscription."""
        if not current_period_start:
            current_period_start = datetime.utcnow()
        
        if not current_period_end:
            if billing_cycle == "monthly":
                from dateutil.relativedelta import relativedelta
                current_period_end = current_period_start + relativedelta(months=1)
            else:  # yearly
                from dateutil.relativedelta import relativedelta
                current_period_end = current_period_start + relativedelta(years=1)
        
        subscription_data = {
            "company_id": company_id,
            "plan_name": plan_name,
            "plan_price": plan_price,
            "billing_cycle": billing_cycle,
            "currency": "USD",
            "status": "active",
            "current_period_start": current_period_start,
            "current_period_end": current_period_end,
            "seats_included": seats_included,
            "seats_used": 0,
            "stripe_subscription_id": stripe_subscription_id,
            "stripe_customer_id": stripe_customer_id,
            "metadata": {}
        }
        
        return await self.create(db, subscription_data)
    
    async def update_subscription_status(
        self,
        db: AsyncSession,
        subscription: Subscription,
        status: str
    ) -> Subscription:
        """Update subscription status."""
        return await self.update(db, subscription, {"status": status})
    
    async def update_seats_used(
        self,
        db: AsyncSession,
        subscription: Subscription,
        seats_used: int
    ) -> Subscription:
        """Update seats used in subscription."""
        return await self.update(db, subscription, {"seats_used": seats_used})
    
    async def get_expired_subscriptions(
        self, 
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subscription]:
        """Get expired subscriptions."""
        query = select(Subscription).where(
            and_(
                Subscription.current_period_end <= datetime.utcnow(),
                Subscription.is_active.is_(True)
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_subscriptions_by_plan(
        self,
        db: AsyncSession,
        plan_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subscription]:
        """Get subscriptions by plan name."""
        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters={"plan_name": plan_name, "status": "active"}
        )


# Create CRUD instances
company = CRUDCompany(CompanyProfile)
team_member = CRUDTeamMember(TeamMember)
subscription = CRUDSubscription(Subscription)