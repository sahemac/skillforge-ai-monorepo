"""
Subscription endpoints for SkillForge AI Payment Service
Comprehensive subscription and billing management API
"""

import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import get_security_manager, PCISecurityManager
from app.core.payment_providers import StripePaymentProvider, PayPalPaymentProvider
from app.core.config import get_settings
from app.models import (
    Subscription, SubscriptionCreate, SubscriptionRead, SubscriptionUpdate,
    SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanRead, SubscriptionPlanUpdate,
    UsageRecord, UsageRecordCreate, UsageRecordRead,
    SubscriptionStatus, BillingInterval, PlanType
)

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def get_payment_provider(provider: str) -> StripePaymentProvider | PayPalPaymentProvider:
    """Get payment provider instance."""
    if provider.lower() == "stripe":
        config = {
            "secret_key": settings.STRIPE_SECRET_KEY,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        }
        return StripePaymentProvider(config)
    elif provider.lower() == "paypal":
        config = {
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET,
            "environment": settings.PAYPAL_ENVIRONMENT,
        }
        return PayPalPaymentProvider(config)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported payment provider: {provider}"
        )


# Subscription Plans Management
@router.post("/plans", response_model=SubscriptionPlanRead, status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Create a new subscription plan."""
    try:
        plan = SubscriptionPlan(**plan_data.model_dump())
        session.add(plan)
        await session.commit()
        await session.refresh(plan)

        # Audit log
        security_manager.audit_log(
            action="subscription_plan_created",
            user_id=None,  # Admin action
            data={
                "plan_id": str(plan.id),
                "name": plan.name,
                "price": str(plan.price),
                "plan_type": plan.plan_type.value,
            }
        )

        return SubscriptionPlanRead.model_validate(plan)

    except Exception as e:
        logger.error(f"Subscription plan creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription plan"
        )


@router.get("/plans", response_model=List[SubscriptionPlanRead])
async def list_subscription_plans(
    plan_type: Optional[PlanType] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List available subscription plans."""
    query = select(SubscriptionPlan)

    if plan_type:
        query = query.where(SubscriptionPlan.plan_type == plan_type)
    if is_active is not None:
        query = query.where(SubscriptionPlan.is_active == is_active)

    query = query.offset(offset).limit(limit).order_by(SubscriptionPlan.created_at.desc())

    result = await session.exec(query)
    plans = result.all()

    return [SubscriptionPlanRead.model_validate(plan) for plan in plans]


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanRead)
async def get_subscription_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get subscription plan by ID."""
    result = await session.exec(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    return SubscriptionPlanRead.model_validate(plan)


@router.patch("/plans/{plan_id}", response_model=SubscriptionPlanRead)
async def update_subscription_plan(
    plan_id: UUID,
    plan_update: SubscriptionPlanUpdate,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Update subscription plan."""
    result = await session.exec(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.first()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    for field, value in plan_update.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)

    await session.commit()
    await session.refresh(plan)

    # Audit log
    security_manager.audit_log(
        action="subscription_plan_updated",
        user_id=None,
        data={
            "plan_id": str(plan.id),
            "updates": plan_update.model_dump(exclude_unset=True),
        }
    )

    return SubscriptionPlanRead.model_validate(plan)


# Subscription Management
@router.post("/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Create a new subscription."""
    try:
        # Verify plan exists
        plan_result = await session.exec(
            select(SubscriptionPlan).where(SubscriptionPlan.id == subscription_data.plan_id)
        )
        plan = plan_result.first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found"
            )

        if not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot subscribe to inactive plan"
            )

        # Create subscription with provider
        payment_provider = get_payment_provider(subscription_data.provider)

        # First, create or get customer
        customer_id = await payment_provider.create_customer(
            email=f"user_{subscription_data.user_id}@example.com",  # Get from user service
            metadata={"user_id": str(subscription_data.user_id)}
        )

        # Create subscription
        subscription_result = await payment_provider.create_subscription(
            customer_id=customer_id,
            price_id=plan.stripe_price_id if payment_provider.name == "stripe" else plan.paypal_plan_id,
            payment_method_id=subscription_data.default_payment_method_id,
            trial_period_days=plan.trial_period_days if plan.trial_period_days > 0 else None,
            metadata={
                "user_id": str(subscription_data.user_id),
                "plan_id": str(plan.id),
            }
        )

        if not subscription_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subscription creation failed: {subscription_result.error_message}"
            )

        # Create subscription record
        subscription = Subscription(
            **subscription_data.model_dump(),
            provider_subscription_id=subscription_result.provider_subscription_id,
            provider_customer_id=subscription_result.provider_customer_id,
            status=SubscriptionStatus(subscription_result.status),
            current_period_start=subscription_result.current_period_start or datetime.utcnow(),
            current_period_end=subscription_result.current_period_end or (
                datetime.utcnow() + timedelta(days=30)
            ),
        )

        session.add(subscription)
        await session.commit()
        await session.refresh(subscription)

        # Load plan relationship
        await session.refresh(subscription, ["plan"])

        # Audit log
        security_manager.audit_log(
            action="subscription_created",
            user_id=str(subscription_data.user_id),
            data={
                "subscription_id": str(subscription.id),
                "plan_id": str(plan.id),
                "provider": subscription_data.provider,
            }
        )

        return SubscriptionRead.model_validate(subscription)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )


@router.get("/", response_model=List[SubscriptionRead])
async def list_subscriptions(
    user_id: Optional[UUID] = Query(None),
    organization_id: Optional[UUID] = Query(None),
    status: Optional[SubscriptionStatus] = Query(None),
    plan_id: Optional[UUID] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List subscriptions with optional filtering."""
    query = select(Subscription).options(selectinload(Subscription.plan))

    if user_id:
        query = query.where(Subscription.user_id == user_id)
    if organization_id:
        query = query.where(Subscription.organization_id == organization_id)
    if status:
        query = query.where(Subscription.status == status)
    if plan_id:
        query = query.where(Subscription.plan_id == plan_id)

    query = query.offset(offset).limit(limit).order_by(Subscription.created_at.desc())

    result = await session.exec(query)
    subscriptions = result.all()

    return [SubscriptionRead.model_validate(sub) for sub in subscriptions]


@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(
    subscription_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get subscription by ID."""
    result = await session.exec(
        select(Subscription)
        .where(Subscription.id == subscription_id)
        .options(selectinload(Subscription.plan))
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    return SubscriptionRead.model_validate(subscription)


@router.patch("/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription(
    subscription_id: UUID,
    subscription_update: SubscriptionUpdate,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Update subscription."""
    result = await session.exec(
        select(Subscription)
        .where(Subscription.id == subscription_id)
        .options(selectinload(Subscription.plan))
    )
    subscription = result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    for field, value in subscription_update.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)

    await session.commit()
    await session.refresh(subscription)

    # Audit log
    security_manager.audit_log(
        action="subscription_updated",
        user_id=str(subscription.user_id),
        data={
            "subscription_id": str(subscription.id),
            "updates": subscription_update.model_dump(exclude_unset=True),
        }
    )

    return SubscriptionRead.model_validate(subscription)


@router.post("/{subscription_id}/cancel", response_model=SubscriptionRead)
async def cancel_subscription(
    subscription_id: UUID,
    at_period_end: bool = Query(True, description="Cancel at end of current period"),
    cancellation_reason: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Cancel a subscription."""
    try:
        result = await session.exec(
            select(Subscription)
            .where(Subscription.id == subscription_id)
            .options(selectinload(Subscription.plan))
        )
        subscription = result.first()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        if subscription.status in [SubscriptionStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription is already cancelled"
            )

        # Cancel with provider
        payment_provider = get_payment_provider(subscription.provider)
        success = await payment_provider.cancel_subscription(
            subscription.provider_subscription_id,
            at_period_end=at_period_end
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to cancel subscription with provider"
            )

        # Update subscription
        subscription.cancel_at_period_end = at_period_end
        subscription.cancellation_reason = cancellation_reason
        subscription.cancelled_at = datetime.utcnow()

        if not at_period_end:
            subscription.status = SubscriptionStatus.CANCELLED

        await session.commit()
        await session.refresh(subscription)

        # Audit log
        security_manager.audit_log(
            action="subscription_cancelled",
            user_id=str(subscription.user_id),
            data={
                "subscription_id": str(subscription.id),
                "at_period_end": at_period_end,
                "reason": cancellation_reason,
            }
        )

        return SubscriptionRead.model_validate(subscription)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/{subscription_id}/usage", response_model=UsageRecordRead)
async def record_usage(
    subscription_id: UUID,
    usage_data: UsageRecordCreate,
    session: AsyncSession = Depends(get_session),
):
    """Record usage for metered billing."""
    try:
        # Verify subscription exists
        sub_result = await session.exec(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = sub_result.first()

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )

        # Create usage record
        usage_record = UsageRecord(
            subscription_id=subscription_id,
            **usage_data.model_dump()
        )

        session.add(usage_record)
        await session.commit()
        await session.refresh(usage_record)

        return UsageRecordRead.model_validate(usage_record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Usage recording failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record usage"
        )


@router.get("/{subscription_id}/usage", response_model=List[UsageRecordRead])
async def list_usage_records(
    subscription_id: UUID,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List usage records for a subscription."""
    # Verify subscription exists
    sub_result = await session.exec(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    subscription = sub_result.first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Get usage records
    usage_result = await session.exec(
        select(UsageRecord)
        .where(UsageRecord.subscription_id == subscription_id)
        .offset(offset)
        .limit(limit)
        .order_by(UsageRecord.usage_date.desc())
    )
    usage_records = usage_result.all()

    return [UsageRecordRead.model_validate(record) for record in usage_records]


# Import selectinload here to avoid circular imports
try:
    from sqlalchemy.orm import selectinload
except ImportError:
    # Fallback for older versions
    from sqlmodel import selectinload