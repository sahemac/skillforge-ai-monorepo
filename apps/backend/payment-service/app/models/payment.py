"""
Payment models for SkillForge AI Payment Service
PCI Compliant payment processing models
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column, Text, JSON
from sqlalchemy import Index


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentProvider(str, Enum):
    """Payment provider enumeration."""
    STRIPE = "stripe"
    PAYPAL = "paypal"


class PaymentMethodType(str, Enum):
    """Payment method type enumeration."""
    CARD = "card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class PaymentBase(SQLModel):
    """Base payment model."""
    amount: Decimal = Field(decimal_places=2, max_digits=12, description="Payment amount")
    currency: str = Field(max_length=3, description="ISO currency code (EUR, USD, etc.)")
    description: Optional[str] = Field(default=None, max_length=500, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Additional metadata")

    # User and organization
    user_id: UUID = Field(description="User who initiated the payment")
    organization_id: Optional[UUID] = Field(default=None, description="Organization for B2B payments")

    # Provider specific
    provider: PaymentProvider = Field(description="Payment provider (Stripe, PayPal)")
    provider_payment_id: Optional[str] = Field(default=None, max_length=255, description="Provider's payment ID")
    provider_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Payment method
    payment_method_type: PaymentMethodType = Field(description="Type of payment method used")
    payment_method_id: Optional[str] = Field(default=None, max_length=255, description="Payment method ID (tokenized)")

    # Status and timing
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    failed_reason: Optional[str] = Field(default=None, max_length=500, description="Failure reason if applicable")
    processed_at: Optional[datetime] = Field(default=None, description="When payment was processed")

    # Financial details
    fee_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12, description="Processing fee")
    net_amount: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=12, description="Net amount after fees")

    # Refund information
    refunded_amount: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=12)
    is_refundable: bool = Field(default=True, description="Whether payment can be refunded")

    # Invoice relationship
    invoice_id: Optional[UUID] = Field(default=None, foreign_key="invoice.id", description="Associated invoice ID")


class Payment(PaymentBase, table=True):
    """Payment table with timestamps and UUID."""
    __tablename__ = "payments"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="Unique payment ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Relationships
    invoice: Optional["Invoice"] = Relationship(back_populates="payment")
    refunds: list["PaymentRefund"] = Relationship(back_populates="payment")

    __table_args__ = (
        Index("idx_payments_user_id", "user_id"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_provider", "provider"),
        Index("idx_payments_created_at", "created_at"),
        Index("idx_payments_provider_payment_id", "provider_payment_id"),
    )

    def __repr__(self) -> str:
        return f"Payment(id={self.id}, amount={self.amount}, status={self.status})"


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    pass


class PaymentUpdate(SQLModel):
    """Schema for updating a payment."""
    status: Optional[PaymentStatus] = None
    provider_payment_id: Optional[str] = None
    provider_metadata: Optional[Dict[str, Any]] = None
    failed_reason: Optional[str] = None
    processed_at: Optional[datetime] = None
    fee_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentRead(PaymentBase):
    """Schema for reading a payment."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    refunded_amount: Decimal


class PaymentRefundBase(SQLModel):
    """Base refund model."""
    amount: Decimal = Field(decimal_places=2, max_digits=12, description="Refund amount")
    reason: Optional[str] = Field(default=None, max_length=500, description="Refund reason")
    provider_refund_id: Optional[str] = Field(default=None, max_length=255, description="Provider's refund ID")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Refund status")
    processed_at: Optional[datetime] = Field(default=None, description="When refund was processed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class PaymentRefund(PaymentRefundBase, table=True):
    """Payment refund table."""
    __tablename__ = "payment_refunds"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_id: UUID = Field(foreign_key="payments.id", description="Associated payment")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    payment: Payment = Relationship(back_populates="refunds")

    __table_args__ = (
        Index("idx_refunds_payment_id", "payment_id"),
        Index("idx_refunds_status", "status"),
    )


class PaymentRefundCreate(PaymentRefundBase):
    """Schema for creating a refund."""
    payment_id: UUID


class PaymentRefundRead(PaymentRefundBase):
    """Schema for reading a refund."""
    id: UUID
    payment_id: UUID
    created_at: datetime
    updated_at: datetime


# Import here to avoid circular imports
from .invoice import Invoice