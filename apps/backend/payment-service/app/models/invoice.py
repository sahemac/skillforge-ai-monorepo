"""
Invoice models for SkillForge AI Payment Service
Comprehensive invoice and billing management
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Text
from sqlalchemy import Index


class InvoiceStatus(str, Enum):
    """Invoice status enumeration."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    VOID = "void"
    PARTIAL = "partial"


class InvoiceType(str, Enum):
    """Invoice type enumeration."""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE = "usage"
    CREDIT_NOTE = "credit_note"


class TaxType(str, Enum):
    """Tax type enumeration."""
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    NONE = "none"


class InvoiceBase(SQLModel):
    """Base invoice model."""
    # Customer information
    user_id: UUID = Field(description="Invoice recipient user ID")
    organization_id: Optional[UUID] = Field(default=None, description="Organization ID for B2B")

    # Invoice details
    invoice_number: str = Field(max_length=50, unique=True, description="Unique invoice number")
    invoice_type: InvoiceType = Field(description="Type of invoice")
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Invoice status")

    # Subscription relationship (if applicable)
    subscription_id: Optional[UUID] = Field(default=None, foreign_key="subscriptions.id")

    # Dates
    issue_date: date = Field(description="Invoice issue date")
    due_date: date = Field(description="Payment due date")
    paid_date: Optional[date] = Field(default=None, description="Date invoice was paid")

    # Financial details
    currency: str = Field(max_length=3, description="ISO currency code")
    subtotal: Decimal = Field(decimal_places=2, max_digits=12, description="Subtotal before tax")
    tax_amount: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=12)
    tax_rate: Optional[Decimal] = Field(default=None, decimal_places=4, max_digits=6, description="Tax rate as percentage")
    tax_type: TaxType = Field(default=TaxType.NONE, description="Type of tax applied")
    discount_amount: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=12)
    total_amount: Decimal = Field(decimal_places=2, max_digits=12, description="Total amount including tax")

    # Customer details (stored for invoice permanence)
    customer_name: str = Field(max_length=200, description="Customer name")
    customer_email: str = Field(max_length=255, description="Customer email")
    billing_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Company details
    company_name: Optional[str] = Field(default=None, max_length=200)
    company_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    tax_number: Optional[str] = Field(default=None, max_length=50, description="VAT/Tax number")

    # Notes and terms
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    terms: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Provider integration
    provider_invoice_id: Optional[str] = Field(default=None, max_length=255)

    # PDF generation
    pdf_url: Optional[str] = Field(default=None, max_length=500, description="URL to PDF file")
    pdf_generated_at: Optional[datetime] = Field(default=None, description="When PDF was generated")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class Invoice(InvoiceBase, table=True):
    """Invoice table."""
    __tablename__ = "invoices"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    subscription: Optional["Subscription"] = Relationship(back_populates="invoices")
    payment: Optional["Payment"] = Relationship(back_populates="invoice")
    line_items: List["InvoiceLineItem"] = Relationship(back_populates="invoice", cascade_delete=True)

    __table_args__ = (
        Index("idx_invoices_user_id", "user_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_subscription_id", "subscription_id"),
        Index("idx_invoices_due_date", "due_date"),
        Index("idx_invoices_invoice_number", "invoice_number"),
    )

    def __repr__(self) -> str:
        return f"Invoice(number={self.invoice_number}, total={self.total_amount}, status={self.status})"


class InvoiceLineItemBase(SQLModel):
    """Base invoice line item model."""
    description: str = Field(max_length=500, description="Item description")
    quantity: Decimal = Field(decimal_places=2, max_digits=10, description="Quantity")
    unit_price: Decimal = Field(decimal_places=2, max_digits=12, description="Price per unit")
    amount: Decimal = Field(decimal_places=2, max_digits=12, description="Total amount (quantity * unit_price)")

    # Product information
    product_name: Optional[str] = Field(default=None, max_length=200)
    product_sku: Optional[str] = Field(default=None, max_length=100)

    # Discounts
    discount_amount: Decimal = Field(default=Decimal('0.00'), decimal_places=2, max_digits=12)
    discount_rate: Optional[Decimal] = Field(default=None, decimal_places=4, max_digits=6)

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class InvoiceLineItem(InvoiceLineItemBase, table=True):
    """Invoice line item table."""
    __tablename__ = "invoice_line_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    invoice_id: UUID = Field(foreign_key="invoices.id", description="Parent invoice")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    invoice: Invoice = Relationship(back_populates="line_items")

    __table_args__ = (
        Index("idx_line_items_invoice_id", "invoice_id"),
    )


class WebhookEventBase(SQLModel):
    """Base webhook event model."""
    event_id: str = Field(max_length=255, unique=True, description="Provider event ID")
    event_type: str = Field(max_length=100, description="Type of event")
    provider: str = Field(max_length=50, description="Payment provider")

    # Event data
    data: Dict[str, Any] = Field(sa_column=Column(JSON), description="Raw event data")
    processed: bool = Field(default=False, description="Whether event was processed")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")

    # Error handling
    processing_attempts: int = Field(default=0, description="Number of processing attempts")
    last_error: Optional[str] = Field(default=None, max_length=1000, description="Last processing error")

    # Related objects
    related_object_type: Optional[str] = Field(default=None, max_length=50)
    related_object_id: Optional[UUID] = Field(default=None, description="Related object UUID")


class WebhookEvent(WebhookEventBase, table=True):
    """Webhook event table."""
    __tablename__ = "webhook_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("idx_webhook_events_event_id", "event_id"),
        Index("idx_webhook_events_provider", "provider"),
        Index("idx_webhook_events_processed", "processed"),
        Index("idx_webhook_events_event_type", "event_type"),
    )


# Pydantic schemas
class InvoiceCreate(InvoiceBase):
    """Schema for creating an invoice."""
    line_items: List[InvoiceLineItemBase] = Field(description="Invoice line items")


class InvoiceUpdate(SQLModel):
    """Schema for updating an invoice."""
    status: Optional[InvoiceStatus] = None
    paid_date: Optional[date] = None
    notes: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceLineItemRead(InvoiceLineItemBase):
    """Schema for reading an invoice line item."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class InvoiceRead(InvoiceBase):
    """Schema for reading an invoice."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    line_items: List[InvoiceLineItemRead] = []


class InvoiceSummary(SQLModel):
    """Summary schema for invoice lists."""
    id: UUID
    invoice_number: str
    customer_name: str
    total_amount: Decimal
    status: InvoiceStatus
    due_date: date
    created_at: datetime


class WebhookEventCreate(WebhookEventBase):
    """Schema for creating a webhook event."""
    pass


class WebhookEventRead(WebhookEventBase):
    """Schema for reading a webhook event."""
    id: UUID
    created_at: datetime
    updated_at: datetime


# Import here to avoid circular imports
from .payment import Payment
from .subscription import Subscription