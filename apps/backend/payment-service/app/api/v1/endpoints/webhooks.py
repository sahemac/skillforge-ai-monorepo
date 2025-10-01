"""
Webhook endpoints for SkillForge AI Payment Service
Secure webhook processing for Stripe and PayPal
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlmodel.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_security_manager, PCISecurityManager
from app.core.payment_providers import StripePaymentProvider, PayPalPaymentProvider
from app.core.config import get_settings
from app.models import WebhookEvent, WebhookEventCreate, Payment, Subscription
from sqlmodel import select

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook secret not configured"
        )

    try:
        payload = await request.body()

        # Initialize Stripe provider for webhook validation
        stripe_provider = StripePaymentProvider({
            "secret_key": settings.STRIPE_SECRET_KEY,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        })

        # Validate webhook signature and parse event
        event_data = await stripe_provider.validate_webhook(
            payload=payload,
            signature=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )

        # Check if event was already processed (idempotency)
        event_result = await session.exec(
            select(WebhookEvent).where(WebhookEvent.event_id == event_data["id"])
        )
        existing_event = event_result.first()

        if existing_event:
            if existing_event.processed:
                return {"status": "already_processed"}
            else:
                # Update processing attempts
                existing_event.processing_attempts += 1
                webhook_event = existing_event
        else:
            # Create new webhook event record
            webhook_event = WebhookEvent(
                event_id=event_data["id"],
                event_type=event_data["type"],
                provider="stripe",
                data=event_data,
            )
            session.add(webhook_event)

        # Process the event
        try:
            await process_stripe_event(event_data, session, security_manager)

            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to process Stripe webhook: {str(e)}")
            webhook_event.last_error = str(e)
            webhook_event.processing_attempts += 1

            # Don't raise the exception - return success to Stripe
            # Failed events can be reprocessed later

        await session.commit()

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Stripe webhook handling failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook"
        )


@router.post("/paypal")
async def handle_paypal_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
    security_manager: PCISecurityManager = Depends(get_security_manager),
):
    """Handle PayPal webhook events."""
    try:
        payload = await request.body()

        # Initialize PayPal provider for webhook validation
        paypal_provider = PayPalPaymentProvider({
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET,
            "environment": settings.PAYPAL_ENVIRONMENT,
            "webhook_id": settings.PAYPAL_WEBHOOK_ID,
        })

        # Validate webhook (basic validation for now)
        event_data = await paypal_provider.validate_webhook(
            payload=payload,
            signature="",  # PayPal has different signature validation
            secret=""
        )

        # Check if event was already processed
        event_id = event_data.get("id", "")
        event_result = await session.exec(
            select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        )
        existing_event = event_result.first()

        if existing_event and existing_event.processed:
            return {"status": "already_processed"}

        # Create or update webhook event record
        if existing_event:
            existing_event.processing_attempts += 1
            webhook_event = existing_event
        else:
            webhook_event = WebhookEvent(
                event_id=event_id,
                event_type=event_data.get("event_type", ""),
                provider="paypal",
                data=event_data,
            )
            session.add(webhook_event)

        # Process the event
        try:
            await process_paypal_event(event_data, session, security_manager)

            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to process PayPal webhook: {str(e)}")
            webhook_event.last_error = str(e)
            webhook_event.processing_attempts += 1

        await session.commit()

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"PayPal webhook handling failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook"
        )


async def process_stripe_event(
    event_data: Dict[str, Any],
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Process Stripe webhook events."""
    event_type = event_data["type"]
    data_object = event_data["data"]["object"]

    if event_type == "payment_intent.succeeded":
        await handle_payment_succeeded(data_object, "stripe", session, security_manager)

    elif event_type == "payment_intent.payment_failed":
        await handle_payment_failed(data_object, "stripe", session, security_manager)

    elif event_type == "invoice.payment_succeeded":
        await handle_subscription_payment_succeeded(data_object, session, security_manager)

    elif event_type == "customer.subscription.created":
        await handle_subscription_created(data_object, "stripe", session, security_manager)

    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(data_object, "stripe", session, security_manager)

    elif event_type == "customer.subscription.deleted":
        await handle_subscription_cancelled(data_object, "stripe", session, security_manager)

    else:
        logger.info(f"Unhandled Stripe event type: {event_type}")


async def process_paypal_event(
    event_data: Dict[str, Any],
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Process PayPal webhook events."""
    event_type = event_data.get("event_type", "")
    resource = event_data.get("resource", {})

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        await handle_payment_succeeded(resource, "paypal", session, security_manager)

    elif event_type == "PAYMENT.CAPTURE.DENIED":
        await handle_payment_failed(resource, "paypal", session, security_manager)

    elif event_type == "BILLING.SUBSCRIPTION.CREATED":
        await handle_subscription_created(resource, "paypal", session, security_manager)

    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        await handle_subscription_cancelled(resource, "paypal", session, security_manager)

    else:
        logger.info(f"Unhandled PayPal event type: {event_type}")


async def handle_payment_succeeded(
    payment_data: Dict[str, Any],
    provider: str,
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle successful payment."""
    provider_payment_id = payment_data.get("id")

    # Find payment in database
    result = await session.exec(
        select(Payment).where(Payment.provider_payment_id == provider_payment_id)
    )
    payment = result.first()

    if payment:
        payment.status = "succeeded"
        payment.processed_at = datetime.utcnow()

        # Update fee information if available
        if provider == "stripe" and "charges" in payment_data:
            charges = payment_data["charges"]["data"]
            if charges:
                charge = charges[0]
                if "balance_transaction" in charge:
                    # Would need to fetch balance transaction for fee details
                    pass

        await session.commit()

        security_manager.audit_log(
            action="payment_succeeded_webhook",
            user_id=str(payment.user_id),
            data={
                "payment_id": str(payment.id),
                "provider": provider,
                "provider_payment_id": provider_payment_id,
            }
        )


async def handle_payment_failed(
    payment_data: Dict[str, Any],
    provider: str,
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle failed payment."""
    provider_payment_id = payment_data.get("id")

    result = await session.exec(
        select(Payment).where(Payment.provider_payment_id == provider_payment_id)
    )
    payment = result.first()

    if payment:
        payment.status = "failed"
        payment.failed_reason = payment_data.get("failure_reason", "Payment failed")

        await session.commit()

        security_manager.audit_log(
            action="payment_failed_webhook",
            user_id=str(payment.user_id),
            data={
                "payment_id": str(payment.id),
                "provider": provider,
                "reason": payment.failed_reason,
            }
        )


async def handle_subscription_created(
    subscription_data: Dict[str, Any],
    provider: str,
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle subscription created."""
    provider_subscription_id = subscription_data.get("id")

    result = await session.exec(
        select(Subscription).where(
            Subscription.provider_subscription_id == provider_subscription_id
        )
    )
    subscription = result.first()

    if subscription:
        subscription.status = "active" if subscription_data.get("status") == "active" else "trialing"
        await session.commit()


async def handle_subscription_updated(
    subscription_data: Dict[str, Any],
    provider: str,
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle subscription updated."""
    provider_subscription_id = subscription_data.get("id")

    result = await session.exec(
        select(Subscription).where(
            Subscription.provider_subscription_id == provider_subscription_id
        )
    )
    subscription = result.first()

    if subscription:
        # Update subscription status
        status_mapping = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "cancelled",
            "unpaid": "unpaid",
        }

        new_status = status_mapping.get(subscription_data.get("status", ""), subscription.status)
        subscription.status = new_status

        await session.commit()


async def handle_subscription_cancelled(
    subscription_data: Dict[str, Any],
    provider: str,
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle subscription cancelled."""
    provider_subscription_id = subscription_data.get("id")

    result = await session.exec(
        select(Subscription).where(
            Subscription.provider_subscription_id == provider_subscription_id
        )
    )
    subscription = result.first()

    if subscription:
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        await session.commit()


async def handle_subscription_payment_succeeded(
    invoice_data: Dict[str, Any],
    session: AsyncSession,
    security_manager: PCISecurityManager,
):
    """Handle successful subscription payment."""
    subscription_id = invoice_data.get("subscription")

    if subscription_id:
        result = await session.exec(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.first()

        if subscription and subscription.status != "active":
            subscription.status = "active"
            await session.commit()


# Add required import
from datetime import datetime