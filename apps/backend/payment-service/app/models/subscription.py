"""
Subscription models for SkillForge AI Payment Service
Comprehensive subscription and billing cycle management
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import Index


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    UNPAID = "unpaid"
    PAUSED = "paused"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class BillingInterval(str, Enum):
    """Billing interval enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"


class PlanType(str, Enum):
    """Plan type enumeration."""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class SubscriptionPlanBase(SQLModel):
    """Base subscription plan model."""
    name: str = Field(max_length=100, description="Plan name")
    description: Optional[str] = Field(default=None, max_length=500, description="Plan description")
    plan_type: PlanType = Field(description="Type of plan")

    # Pricing
    price: Decimal = Field(decimal_places=2, max_digits=12, description="Plan price")
    currency: str = Field(max_length=3, description="ISO currency code")
    billing_interval: BillingInterval = Field(description="Billing frequency")

    # Features
    max_users: Optional[int] = Field(default=None, description="Maximum users allowed")
    max_projects: Optional[int] = Field(default=None, description="Maximum projects allowed")
    max_storage_gb: Optional[int] = Field(default=None, description="Storage limit in GB")

    # Trial
    trial_period_days: int = Field(default=0, description="Trial period in days")

    # Status
    is_active: bool = Field(default=True, description="Whether plan is available")

    # Provider integration
    stripe_price_id: Optional[str] = Field(default=None, max_length=255, description="Stripe price ID")
    paypal_plan_id: Optional[str] = Field(default=None, max_length=255, description="PayPal plan ID")

    # Metadata
    features: Optional[List[str]] = Field(default=None, sa_column=Column(JSON), description="List of features")
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class SubscriptionPlan(SubscriptionPlanBase, table=True):
    """Subscription plan table."""
    __tablename__ = "subscription_plans"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subscriptions: List["Subscription"] = Relationship(back_populates="plan")

    __table_args__ = (
        Index("idx_plans_plan_type", "plan_type"),
        Index("idx_plans_is_active", "is_active"),
        Index("idx_plans_stripe_price_id", "stripe_price_id"),
    )


class SubscriptionBase(SQLModel):
    """Base subscription model."""
    # Customer information
    user_id: UUID = Field(description="Subscriber user ID")
    organization_id: Optional[UUID] = Field(default=None, description="Organization ID for B2B")

    # Plan and pricing
    plan_id: UUID = Field(foreign_key="subscription_plans.id", description="Subscription plan")

    # Status and timing
    status: SubscriptionStatus = Field(default=SubscriptionStatus.INCOMPLETE)
    current_period_start: datetime = Field(description="Current billing period start")
    current_period_end: datetime = Field(description="Current billing period end")
    trial_start: Optional[datetime] = Field(default=None, description="Trial start date")
    trial_end: Optional[datetime] = Field(default=None, description="Trial end date")

    # Cancellation
    cancel_at_period_end: bool = Field(default=False, description="Cancel at end of current period")
    cancelled_at: Optional[datetime] = Field(default=None, description="Cancellation timestamp")
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)

    # Provider integration
    provider: str = Field(max_length=50, description="Payment provider")
    provider_subscription_id: Optional[str] = Field(default=None, max_length=255)
    provider_customer_id: Optional[str] = Field(default=None, max_length=255)

    # Billing
    default_payment_method_id: Optional[str] = Field(default=None, max_length=255)

    # Pricing overrides (for custom deals)
    custom_price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12)
    discount_percent: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=5)

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class Subscription(SubscriptionBase, table=True):
    """Subscription table."""
    __tablename__ = "subscriptions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    plan: SubscriptionPlan = Relationship(back_populates="subscriptions")
    invoices: List["Invoice"] = Relationship(back_populates="subscription")
    usage_records: List["UsageRecord"] = Relationship(back_populates="subscription")

    __table_args__ = (
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index("idx_subscriptions_plan_id", "plan_id"),
        Index("idx_subscriptions_current_period_end", "current_period_end"),
        Index("idx_subscriptions_provider_subscription_id", "provider_subscription_id"),
    )


class UsageRecordBase(SQLModel):
    """Base usage record model for metered billing."""
    subscription_id: UUID = Field(foreign_key="subscriptions.id")

    # Usage tracking
    quantity: int = Field(description="Usage quantity")
    unit: str = Field(max_length=50, description="Usage unit (seats, API calls, etc.)")

    # Timing
    usage_date: date = Field(description="Date of usage")
    billing_period_start: datetime = Field(description="Billing period start")
    billing_period_end: datetime = Field(description="Billing period end")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class UsageRecord(UsageRecordBase, table=True):
    """Usage record table for metered billing."""
    __tablename__ = "usage_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subscription: Subscription = Relationship(back_populates="usage_records")

    __table_args__ = (
        Index("idx_usage_records_subscription_id", "subscription_id"),
        Index("idx_usage_records_usage_date", "usage_date"),
        Index("idx_usage_records_billing_period", "billing_period_start", "billing_period_end"),
    )


# Pydantic schemas
class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan."""
    pass


class SubscriptionPlanUpdate(SQLModel):
    """Schema for updating a subscription plan."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None
    features: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionPlanRead(SubscriptionPlanBase):
    """Schema for reading a subscription plan."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a subscription."""
    pass


class SubscriptionUpdate(SQLModel):
    """Schema for updating a subscription."""
    status: Optional[SubscriptionStatus] = None
    cancel_at_period_end: Optional[bool] = None
    cancellation_reason: Optional[str] = None
    custom_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubscriptionRead(SubscriptionBase):
    """Schema for reading a subscription."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    plan: SubscriptionPlanRead


class UsageRecordCreate(UsageRecordBase):
    """Schema for creating a usage record."""
    pass


class UsageRecordRead(UsageRecordBase):
    """Schema for reading a usage record."""
    id: UUID
    created_at: datetime
    updated_at: datetime


# Import here to avoid circular imports
from .invoice import Invoice