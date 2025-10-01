"""
PayPal payment provider for SkillForge AI Payment Service
PCI Compliant PayPal integration
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

import httpx
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersGetRequest, OrdersCaptureRequest
from paypalhttp import HttpError

from .base_provider import (
    BasePaymentProvider,
    PaymentProviderError,
    PaymentIntentData,
    PaymentResult,
    RefundResult,
    SubscriptionResult,
)

logger = logging.getLogger(__name__)


class PayPalPaymentProvider(BasePaymentProvider):
    """PayPal payment provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize PayPal provider."""
        super().__init__(config)

        # Set up PayPal environment
        if config.get("environment", "sandbox").lower() == "live":
            environment = LiveEnvironment(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            )
        else:
            environment = SandboxEnvironment(
                client_id=config["client_id"],
                client_secret=config["client_secret"]
            )

        self.client = PayPalHttpClient(environment)
        self.webhook_id = config.get("webhook_id")

    def _validate_config(self) -> None:
        """Validate PayPal configuration."""
        required_keys = ["client_id", "client_secret"]
        for key in required_keys:
            if key not in self.config or not self.config[key]:
                raise PaymentProviderError(f"Missing required PayPal config: {key}")

    @property
    def name(self) -> str:
        """Provider name."""
        return "paypal"

    @property
    def supported_currencies(self) -> List[str]:
        """List of supported currencies."""
        return [
            "USD", "EUR", "GBP", "AUD", "BRL", "CAD", "CHF", "DKK", "HKD", "INR",
            "JPY", "MXN", "NOK", "NZD", "PLN", "SEK", "SGD", "THB", "CZK", "HUF",
        ]

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentIntentData:
        """Create a PayPal order (equivalent to payment intent)."""
        try:
            request = OrdersCreateRequest()
            request.headers["Prefer"] = "return=representation"

            order_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": currency.upper(),
                        "value": str(amount)
                    }
                }],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "brand_name": "SkillForge AI",
                            "locale": "en-US",
                            "user_action": "PAY_NOW"
                        }
                    }
                }
            }

            if metadata:
                order_data["custom_id"] = json.dumps(metadata)

            request.request_body(order_data)

            response = self.client.execute(request)
            order = response.result

            # Extract approval URL for client-side redirect
            approval_url = None
            for link in order.links:
                if link.rel == "approve":
                    approval_url = link.href
                    break

            return PaymentIntentData(
                provider_intent_id=order.id,
                client_secret=approval_url,  # Using approval URL as client secret
                amount=amount,
                currency=currency,
                status=order.status.lower(),
                metadata=metadata or {},
            )

        except HttpError as e:
            logger.error(f"PayPal order creation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to create PayPal order: {str(e)}")

    async def confirm_payment(
        self,
        provider_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """Capture a PayPal order."""
        try:
            request = OrdersCaptureRequest(provider_intent_id)
            request.request_body({})

            response = self.client.execute(request)
            order = response.result

            # Extract payment details
            success = order.status == "COMPLETED"
            fee_amount = None
            net_amount = None

            if success and order.purchase_units:
                capture = order.purchase_units[0].payments.captures[0]
                if hasattr(capture, 'seller_receivable_breakdown'):
                    breakdown = capture.seller_receivable_breakdown
                    if hasattr(breakdown, 'paypal_fee'):
                        fee_amount = Decimal(breakdown.paypal_fee.value)
                    if hasattr(breakdown, 'net_amount'):
                        net_amount = Decimal(breakdown.net_amount.value)

            return PaymentResult(
                success=success,
                provider_payment_id=provider_intent_id,
                status=order.status.lower(),
                fee_amount=fee_amount,
                net_amount=net_amount,
                metadata={},
            )

        except HttpError as e:
            logger.error(f"PayPal order capture failed: {str(e)}")
            return PaymentResult(
                success=False,
                status="failed",
                error_message=str(e),
            )

    async def retrieve_payment(self, provider_payment_id: str) -> PaymentResult:
        """Retrieve PayPal order details."""
        try:
            request = OrdersGetRequest(provider_payment_id)
            response = self.client.execute(request)
            order = response.result

            success = order.status == "COMPLETED"
            fee_amount = None
            net_amount = None

            if success and order.purchase_units:
                captures = order.purchase_units[0].payments.captures
                if captures:
                    capture = captures[0]
                    if hasattr(capture, 'seller_receivable_breakdown'):
                        breakdown = capture.seller_receivable_breakdown
                        if hasattr(breakdown, 'paypal_fee'):
                            fee_amount = Decimal(breakdown.paypal_fee.value)
                        if hasattr(breakdown, 'net_amount'):
                            net_amount = Decimal(breakdown.net_amount.value)

            return PaymentResult(
                success=success,
                provider_payment_id=provider_payment_id,
                status=order.status.lower(),
                fee_amount=fee_amount,
                net_amount=net_amount,
                metadata={},
            )

        except HttpError as e:
            logger.error(f"PayPal order retrieval failed: {str(e)}")
            raise PaymentProviderError(f"Failed to retrieve PayPal order: {str(e)}")

    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RefundResult:
        """Refund a PayPal payment."""
        try:
            # First, get the order to find the capture ID
            order_request = OrdersGetRequest(provider_payment_id)
            order_response = self.client.execute(order_request)
            order = order_response.result

            if not order.purchase_units or not order.purchase_units[0].payments.captures:
                raise PaymentProviderError("No captures found for this order")

            capture_id = order.purchase_units[0].payments.captures[0].id

            # Create refund request
            refund_data = {}
            if amount:
                # Get original currency from order
                currency = order.purchase_units[0].amount.currency_code
                refund_data["amount"] = {
                    "value": str(amount),
                    "currency_code": currency
                }

            if reason:
                refund_data["note_to_payer"] = reason

            # PayPal refund API call (using raw HTTP since SDK doesn't include refunds)
            async with httpx.AsyncClient() as client:
                # Get access token first
                auth_response = await client.post(
                    f"{self._get_base_url()}/v1/oauth2/token",
                    auth=(self.config["client_id"], self.config["client_secret"]),
                    headers={"Accept": "application/json"},
                    data={"grant_type": "client_credentials"}
                )
                auth_data = auth_response.json()
                access_token = auth_data["access_token"]

                # Make refund request
                refund_response = await client.post(
                    f"{self._get_base_url()}/v2/payments/captures/{capture_id}/refund",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation"
                    },
                    json=refund_data
                )

                if refund_response.status_code == 201:
                    refund = refund_response.json()
                    return RefundResult(
                        success=True,
                        provider_refund_id=refund["id"],
                        amount=Decimal(refund["amount"]["value"]),
                        status=refund["status"].lower(),
                        metadata={}
                    )
                else:
                    error_data = refund_response.json()
                    return RefundResult(
                        success=False,
                        amount=amount or Decimal("0"),
                        status="failed",
                        error_message=error_data.get("message", "Unknown error")
                    )

        except Exception as e:
            logger.error(f"PayPal refund failed: {str(e)}")
            return RefundResult(
                success=False,
                amount=amount or Decimal("0"),
                status="failed",
                error_message=str(e)
            )

    def _get_base_url(self) -> str:
        """Get PayPal API base URL based on environment."""
        if self.config.get("environment", "sandbox").lower() == "live":
            return "https://api.paypal.com"
        else:
            return "https://api.sandbox.paypal.com"

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a PayPal customer (PayPal doesn't have direct customer creation).
        Returns email as identifier.
        """
        # PayPal doesn't have a direct customer creation API like Stripe
        # We'll return the email as the customer identifier
        return email

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionResult:
        """Create a PayPal subscription (requires pre-configured billing plan)."""
        try:
            # PayPal subscriptions require pre-configured billing plans
            # This is a simplified implementation
            subscription_data = {
                "plan_id": price_id,
                "subscriber": {
                    "email_address": customer_id  # Using email as customer_id
                },
                "application_context": {
                    "brand_name": "SkillForge AI",
                    "locale": "en-US",
                    "user_action": "SUBSCRIBE_NOW"
                }
            }

            if trial_period_days:
                # Add trial period configuration
                subscription_data["plan"] = {
                    "billing_cycles": [
                        {
                            "frequency": {
                                "interval_unit": "DAY",
                                "interval_count": trial_period_days
                            },
                            "tenure_type": "TRIAL",
                            "sequence": 1,
                            "total_cycles": 1,
                            "pricing_scheme": {
                                "fixed_price": {
                                    "value": "0",
                                    "currency_code": "USD"
                                }
                            }
                        }
                    ]
                }

            # Use raw HTTP for subscription creation
            async with httpx.AsyncClient() as client:
                # Get access token
                auth_response = await client.post(
                    f"{self._get_base_url()}/v1/oauth2/token",
                    auth=(self.config["client_id"], self.config["client_secret"]),
                    headers={"Accept": "application/json"},
                    data={"grant_type": "client_credentials"}
                )
                auth_data = auth_response.json()
                access_token = auth_data["access_token"]

                # Create subscription
                subscription_response = await client.post(
                    f"{self._get_base_url()}/v1/billing/subscriptions",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Prefer": "return=representation"
                    },
                    json=subscription_data
                )

                if subscription_response.status_code == 201:
                    subscription = subscription_response.json()
                    return SubscriptionResult(
                        success=True,
                        provider_subscription_id=subscription["id"],
                        provider_customer_id=customer_id,
                        status=subscription["status"].lower(),
                        metadata=metadata or {}
                    )
                else:
                    error_data = subscription_response.json()
                    return SubscriptionResult(
                        success=False,
                        status="failed",
                        error_message=error_data.get("message", "Unknown error")
                    )

        except Exception as e:
            logger.error(f"PayPal subscription creation failed: {str(e)}")
            return SubscriptionResult(
                success=False,
                status="failed",
                error_message=str(e)
            )

    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        at_period_end: bool = True,
    ) -> bool:
        """Cancel a PayPal subscription."""
        try:
            cancel_data = {
                "reason": "User requested cancellation"
            }

            async with httpx.AsyncClient() as client:
                # Get access token
                auth_response = await client.post(
                    f"{self._get_base_url()}/v1/oauth2/token",
                    auth=(self.config["client_id"], self.config["client_secret"]),
                    headers={"Accept": "application/json"},
                    data={"grant_type": "client_credentials"}
                )
                auth_data = auth_response.json()
                access_token = auth_data["access_token"]

                # Cancel subscription
                cancel_response = await client.post(
                    f"{self._get_base_url()}/v1/billing/subscriptions/{provider_subscription_id}/cancel",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=cancel_data
                )

                return cancel_response.status_code == 204

        except Exception as e:
            logger.error(f"PayPal subscription cancellation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to cancel subscription: {str(e)}")

    async def validate_webhook(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> Dict[str, Any]:
        """Validate PayPal webhook signature and parse payload."""
        try:
            # PayPal webhook validation is more complex and requires calling their API
            # For now, we'll do basic JSON parsing and return the payload
            # In production, implement proper signature validation

            payload_str = payload.decode('utf-8')
            webhook_data = json.loads(payload_str)

            # TODO: Implement proper PayPal webhook signature validation
            # This requires calling PayPal's webhook verification API

            return webhook_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid PayPal webhook payload: {str(e)}")
            raise PaymentProviderError("Invalid webhook payload")
        except Exception as e:
            logger.error(f"PayPal webhook validation failed: {str(e)}")
            raise PaymentProviderError(f"Webhook validation failed: {str(e)}")