"""
Company endpoints for SkillForge AI User Service
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from uuid import UUID

from app.api.dependencies import (
    get_db,
    get_current_verified_user,
    get_user_company,
    get_pagination_params,
    get_search_params,
    PaginationParams,
    SearchParams
)
from app.crud import company as company_crud, team_member as member_crud
from app.schemas.company import (
    CompanyResponse,
    CompanyPublicResponse,
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyPublicListResponse,
    TeamMemberResponse,
    TeamMemberInvite,
    TeamMemberUpdate,
    TeamMemberListResponse,
    CompanySearchFilters
)
from app.models.user_simple import User
from app.models.company_simple import CompanyProfile, CompanySize, IndustryType

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_create: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Create a new company profile."""
    try:
        # Check if slug already exists
        if company_create.slug:
            existing = await company_crud.get_by_slug(db, company_create.slug)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company slug already exists"
                )
        
        company = await company_crud.create(db, company_create, current_user.id)
        
        logger.info(f"Company created: {company.name} by {current_user.email}")
        
        return company
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company creation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company creation failed"
        )


@router.get("/my-companies", response_model=CompanyListResponse)
async def get_my_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    pagination: PaginationParams = Depends(get_pagination_params)
) -> Any:
    """Get current user's companies."""
    try:
        companies = await company_crud.get_by_owner(
            db,
            current_user.id,
            skip=pagination.skip,
            limit=pagination.limit
        )
        
        total = await company_crud.count(db, filters={"owner_id": current_user.id})
        total_pages = (total + pagination.size - 1) // pagination.size
        
        return {
            "companies": companies,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"My companies list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get companies"
        )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Get company by ID (owner or team member only)."""
    company = await get_user_company(company_id, db, current_user)
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_update: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Update company profile."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        # Only owner can update company profile
        if company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only company owner can update profile"
            )
        
        update_data = company_update.model_dump(exclude_unset=True)
        updated_company = await company_crud.update(db, company, update_data)
        
        logger.info(f"Company updated: {company.name}")
        
        return updated_company
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company update failed"
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> None:
    """Delete company (soft delete)."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        # Only owner can delete company
        if company.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only company owner can delete company"
            )
        
        # Soft delete
        await company_crud.update(db, company, {"is_active": False})
        
        logger.info(f"Company deleted: {company.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Company deletion failed"
        )


# Public company endpoints
@router.get("/public/search", response_model=CompanyPublicListResponse)
async def search_public_companies(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    search: SearchParams = Depends(get_search_params),
    industry: Optional[IndustryType] = Query(None, description="Filter by industry"),
    company_size: Optional[CompanySize] = Query(None, description="Filter by company size"),
    country: Optional[str] = Query(None, description="Filter by country"),
    verified_only: bool = Query(True, description="Show only verified companies"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills focus")
) -> Any:
    """Search public company profiles."""
    try:
        filters = {"is_active": True}
        if verified_only:
            filters["is_verified"] = True
        if industry:
            filters["industry"] = industry
        if company_size:
            filters["company_size"] = company_size
        if country:
            filters["country"] = country
        
        if search.q:
            companies = await company_crud.search_companies(
                db,
                search_term=search.q,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters
            )
        elif skills:
            companies = await company_crud.get_companies_by_skills(
                db,
                skills=skills,
                skip=pagination.skip,
                limit=pagination.limit
            )
        else:
            companies = await company_crud.get_multi(
                db,
                skip=pagination.skip,
                limit=pagination.limit,
                filters=filters,
                order_by="created_at"
            )
        
        # Get total count
        total = await company_crud.count(db, filters=filters)
        total_pages = (total + pagination.size - 1) // pagination.size
        
        return {
            "companies": companies,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Public companies search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search companies"
        )


@router.get("/public/{company_id}", response_model=CompanyPublicResponse)
async def get_public_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get public company profile."""
    company = await company_crud.get(db, company_id)
    if not company or not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.get("/slug/{slug}", response_model=CompanyPublicResponse)
async def get_company_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get company by slug."""
    company = await company_crud.get_by_slug(db, slug)
    if not company or not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


# Team management endpoints
@router.get("/{company_id}/members", response_model=TeamMemberListResponse)
async def get_team_members(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    role: Optional[str] = Query(None, description="Filter by role")
) -> Any:
    """Get company team members."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        if role:
            members = await member_crud.get_members_by_role(
                db,
                company_id,
                role,
                skip=pagination.skip,
                limit=pagination.limit
            )
        else:
            members = await member_crud.get_company_members(
                db,
                company_id,
                skip=pagination.skip,
                limit=pagination.limit
            )
        
        total = await member_crud.count(
            db, 
            filters={"company_id": company_id, "is_active": True}
        )
        total_pages = (total + pagination.size - 1) // pagination.size
        
        return {
            "members": members,
            "total": total,
            "page": pagination.page,
            "size": pagination.size,
            "pages": total_pages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team members list error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get team members"
        )


@router.post("/{company_id}/members", response_model=TeamMemberResponse)
async def invite_team_member(
    company_id: UUID,
    member_invite: TeamMemberInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Invite team member."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        # Only owner or admin members can invite
        if company.owner_id != current_user.id:
            membership = await member_crud.get_by_company_and_user(
                db, company_id, current_user.id
            )
            if not membership or membership.role not in ["admin", "manager"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to invite members"
                )
        
        # Check if user exists
        from app.crud import user as user_crud
        invited_user = await user_crud.get_by_email(db, member_invite.email)
        if not invited_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already a member
        existing_member = await member_crud.get_by_company_and_user(
            db, company_id, invited_user.id
        )
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a team member"
            )
        
        # Add member
        member = await member_crud.add_member(
            db,
            company_id=company_id,
            user_id=invited_user.id,
            role=member_invite.role,
            title=member_invite.title,
            department=member_invite.department,
            permissions=member_invite.permissions,
            invited_by=current_user.id
        )
        
        # In a real app, send invitation email
        # await send_team_invitation_email(invited_user.email, company.name, member_invite.message)
        
        logger.info(f"Team member invited: {invited_user.email} to {company.name}")
        
        return member
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team member invitation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team member invitation failed"
        )


@router.put("/{company_id}/members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    company_id: UUID,
    member_id: UUID,
    member_update: TeamMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> Any:
    """Update team member."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        member = await member_crud.get(db, member_id)
        if not member or member.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Check permissions
        if company.owner_id != current_user.id:
            current_membership = await member_crud.get_by_company_and_user(
                db, company_id, current_user.id
            )
            if not current_membership or current_membership.role not in ["admin", "manager"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to update member"
                )
        
        update_data = member_update.model_dump(exclude_unset=True)
        updated_member = await member_crud.update(db, member, update_data)
        
        logger.info(f"Team member updated: {member_id} in {company.name}")
        
        return updated_member
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team member update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team member update failed"
        )


@router.delete("/{company_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_member(
    company_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_verified_user)
) -> None:
    """Remove team member."""
    try:
        company = await get_user_company(company_id, db, current_user)
        
        member = await member_crud.get(db, member_id)
        if not member or member.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        
        # Check permissions - can remove self or if owner/admin
        can_remove = (
            member.user_id == current_user.id or  # Self
            company.owner_id == current_user.id   # Owner
        )
        
        if not can_remove:
            current_membership = await member_crud.get_by_company_and_user(
                db, company_id, current_user.id
            )
            if current_membership and current_membership.role in ["admin", "manager"]:
                can_remove = True
        
        if not can_remove:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove member"
            )
        
        await member_crud.remove_member(db, member)
        
        logger.info(f"Team member removed: {member_id} from {company.name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Team member removal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Team member removal failed"
        )