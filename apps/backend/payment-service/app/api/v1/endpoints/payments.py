"""
Payment endpoints for SkillForge AI Payment Service
PCI Compliant payment processing API
"""

import logging
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import get_security_manager, PCISecurityManager
from app.core.payment_providers import StripePaymentProvider, PayPalPaymentProvider
from app.core.config import get_settings
from app.models import (
    Payment, PaymentCreate, PaymentRead, PaymentUpdate,
    PaymentRefund, PaymentRefundCreate, PaymentRefundRead,
    PaymentStatus, PaymentProvider
)

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()

router = APIRouter(prefix="/payments", tags=["payments"])


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


@router.post("/intents", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_payment_intent(
    amount: Decimal,
    currency: str,
    provider: PaymentProvider,
    user_id: UUID,
    organization_id: Optional[UUID] = None,
    payment_method_id: Optional[str] = None,
    description: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """
    Create a payment intent with the specified provider.

    This creates a payment intent that can be confirmed on the client side.
    No actual charge is made until the intent is confirmed.
    """
    try:
        # Validate currency support
        payment_provider = get_payment_provider(provider.value)
        if currency.upper() not in payment_provider.supported_currencies:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {currency} not supported by {provider.value}"
            )

        # Create payment intent with provider
        intent_data = await payment_provider.create_payment_intent(
            amount=amount,
            currency=currency.upper(),
            payment_method_id=payment_method_id,
            metadata={
                "user_id": str(user_id),
                "organization_id": str(organization_id) if organization_id else None,
                "description": description,
            }
        )

        # Create payment record in database (pending status)
        payment = Payment(
            amount=amount,
            currency=currency.upper(),
            description=description,
            user_id=user_id,
            organization_id=organization_id,
            provider=provider,
            provider_payment_id=intent_data.provider_intent_id,
            payment_method_id=payment_method_id,
            status=PaymentStatus.PENDING,
            provider_metadata=intent_data.metadata,
        )

        session.add(payment)
        await session.commit()
        await session.refresh(payment)

        # Audit log
        security_manager.audit_log(
            action="payment_intent_created",
            user_id=str(user_id),
            data={
                "payment_id": str(payment.id),
                "amount": str(amount),
                "currency": currency,
                "provider": provider.value,
            }
        )

        return {
            "payment_id": payment.id,
            "provider_intent_id": intent_data.provider_intent_id,
            "client_secret": intent_data.client_secret,
            "amount": amount,
            "currency": currency,
            "status": intent_data.status,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment intent creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.post("/{payment_id}/confirm", response_model=PaymentRead)
async def confirm_payment(
    payment_id: UUID,
    payment_method_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """
    Confirm a payment intent.

    This processes the actual payment and updates the payment status.
    """
    try:
        # Get payment record
        result = await session.exec(select(Payment).where(Payment.id == payment_id))
        payment = result.first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment cannot be confirmed in {payment.status} status"
            )

        # Confirm payment with provider
        payment_provider = get_payment_provider(payment.provider.value)
        result = await payment_provider.confirm_payment(
            provider_intent_id=payment.provider_payment_id,
            payment_method_id=payment_method_id,
        )

        # Update payment record
        update_data = PaymentUpdate(
            status=PaymentStatus.SUCCEEDED if result.success else PaymentStatus.FAILED,
            provider_payment_id=result.provider_payment_id,
            failed_reason=result.error_message if not result.success else None,
            fee_amount=result.fee_amount,
            net_amount=result.net_amount,
            provider_metadata=result.metadata,
        )

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)

        await session.commit()
        await session.refresh(payment)

        # Audit log
        security_manager.audit_log(
            action="payment_confirmed",
            user_id=str(payment.user_id),
            data={
                "payment_id": str(payment.id),
                "status": payment.status.value,
                "success": result.success,
            }
        )

        return PaymentRead.model_validate(payment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment confirmation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment"
        )


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get payment details by ID."""
    result = await session.exec(select(Payment).where(Payment.id == payment_id))
    payment = result.first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return PaymentRead.model_validate(payment)


@router.get("/", response_model=List[PaymentRead])
async def list_payments(
    user_id: Optional[UUID] = Query(None),
    organization_id: Optional[UUID] = Query(None),
    status: Optional[PaymentStatus] = Query(None),
    provider: Optional[PaymentProvider] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    """List payments with optional filtering."""
    query = select(Payment)

    if user_id:
        query = query.where(Payment.user_id == user_id)
    if organization_id:
        query = query.where(Payment.organization_id == organization_id)
    if status:
        query = query.where(Payment.status == status)
    if provider:
        query = query.where(Payment.provider == provider)

    query = query.offset(offset).limit(limit).order_by(Payment.created_at.desc())

    result = await session.exec(query)
    payments = result.all()

    return [PaymentRead.model_validate(payment) for payment in payments]


@router.post("/{payment_id}/refund", response_model=PaymentRefundRead)
async def refund_payment(
    payment_id: UUID,
    amount: Optional[Decimal] = None,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """
    Refund a payment (full or partial).

    If amount is not specified, a full refund is processed.
    """
    try:
        # Get payment record
        result = await session.exec(select(Payment).where(Payment.id == payment_id))
        payment = result.first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        if payment.status != PaymentStatus.SUCCEEDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only successful payments can be refunded"
            )

        if not payment.is_refundable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is not refundable"
            )

        # Check refund amount limits
        max_refundable = payment.amount - payment.refunded_amount
        if amount and amount > max_refundable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot refund {amount}. Maximum refundable amount: {max_refundable}"
            )

        # Process refund with provider
        payment_provider = get_payment_provider(payment.provider.value)
        refund_result = await payment_provider.refund_payment(
            provider_payment_id=payment.provider_payment_id,
            amount=amount,
            reason=reason,
            metadata={"payment_id": str(payment.id)}
        )

        if not refund_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund failed: {refund_result.error_message}"
            )

        # Create refund record
        refund = PaymentRefund(
            payment_id=payment.id,
            amount=refund_result.amount,
            reason=reason,
            provider_refund_id=refund_result.provider_refund_id,
            status=PaymentStatus.SUCCEEDED,
            metadata=refund_result.metadata,
        )

        session.add(refund)

        # Update payment refunded amount
        payment.refunded_amount += refund_result.amount
        if payment.refunded_amount >= payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED

        await session.commit()
        await session.refresh(refund)

        # Audit log
        security_manager.audit_log(
            action="payment_refunded",
            user_id=str(payment.user_id),
            data={
                "payment_id": str(payment.id),
                "refund_id": str(refund.id),
                "amount": str(refund_result.amount),
                "reason": reason,
            }
        )

        return PaymentRefundRead.model_validate(refund)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment refund failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund"
        )


@router.get("/{payment_id}/refunds", response_model=List[PaymentRefundRead])
async def list_payment_refunds(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """List all refunds for a payment."""
    # Verify payment exists
    payment_result = await session.exec(select(Payment).where(Payment.id == payment_id))
    payment = payment_result.first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Get refunds
    refunds_result = await session.exec(
        select(PaymentRefund)
        .where(PaymentRefund.payment_id == payment_id)
        .order_by(PaymentRefund.created_at.desc())
    )
    refunds = refunds_result.all()

    return [PaymentRefundRead.model_validate(refund) for refund in refunds]


@router.get("/{payment_id}/sync", response_model=PaymentRead)
async def sync_payment_with_provider(
    payment_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Sync payment status with payment provider.

    Useful for checking payment status when webhooks might have failed.
    """
    try:
        # Get payment record
        result = await session.exec(select(Payment).where(Payment.id == payment_id))
        payment = result.first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Retrieve payment from provider
        payment_provider = get_payment_provider(payment.provider.value)
        provider_result = await payment_provider.retrieve_payment(
            payment.provider_payment_id
        )

        # Update payment status if different
        if provider_result.status != payment.status.value:
            payment.status = PaymentStatus(provider_result.status)

            if provider_result.fee_amount:
                payment.fee_amount = provider_result.fee_amount
            if provider_result.net_amount:
                payment.net_amount = provider_result.net_amount

            await session.commit()
            await session.refresh(payment)

        return PaymentRead.model_validate(payment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync payment with provider"
        )