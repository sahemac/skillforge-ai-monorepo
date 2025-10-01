"""
Stripe payment provider for SkillForge AI Payment Service
PCI Compliant Stripe integration
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime

import stripe
from stripe.error import StripeError

from .base_provider import (
    BasePaymentProvider,
    PaymentProviderError,
    PaymentIntentData,
    PaymentResult,
    RefundResult,
    SubscriptionResult,
)

logger = logging.getLogger(__name__)


class StripePaymentProvider(BasePaymentProvider):
    """Stripe payment provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Stripe provider."""
        super().__init__(config)
        stripe.api_key = self.config["secret_key"]

    def _validate_config(self) -> None:
        """Validate Stripe configuration."""
        required_keys = ["secret_key", "publishable_key"]
        for key in required_keys:
            if key not in self.config or not self.config[key]:
                raise PaymentProviderError(f"Missing required Stripe config: {key}")

    @property
    def name(self) -> str:
        """Provider name."""
        return "stripe"

    @property
    def supported_currencies(self) -> List[str]:
        """List of supported currencies."""
        return [
            "USD", "EUR", "GBP", "AUD", "BRL", "CAD", "CHF", "DKK", "HKD", "INR",
            "JPY", "MXN", "NOK", "NZD", "PLN", "SEK", "SGD", "THB",
        ]

    def _convert_amount_to_stripe(self, amount: Decimal, currency: str) -> int:
        """Convert decimal amount to Stripe's integer format."""
        # Most currencies use 2 decimal places, but some exceptions exist
        zero_decimal_currencies = ["JPY", "KRW", "CLP", "ISK", "UGX", "VND"]

        if currency.upper() in zero_decimal_currencies:
            return int(amount)
        else:
            return int(amount * 100)  # Convert to cents

    def _convert_amount_from_stripe(self, amount: int, currency: str) -> Decimal:
        """Convert Stripe integer amount to decimal."""
        zero_decimal_currencies = ["JPY", "KRW", "CLP", "ISK", "UGX", "VND"]

        if currency.upper() in zero_decimal_currencies:
            return Decimal(str(amount))
        else:
            return Decimal(str(amount)) / 100

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentIntentData:
        """Create a Stripe payment intent."""
        try:
            stripe_amount = self._convert_amount_to_stripe(amount, currency)

            intent_params = {
                "amount": stripe_amount,
                "currency": currency.lower(),
                "automatic_payment_methods": {"enabled": True},
                "metadata": metadata or {},
            }

            if customer_id:
                intent_params["customer"] = customer_id

            if payment_method_id:
                intent_params["payment_method"] = payment_method_id
                intent_params["confirmation_method"] = "manual"
                intent_params["confirm"] = True

            intent = stripe.PaymentIntent.create(**intent_params)

            return PaymentIntentData(
                provider_intent_id=intent.id,
                client_secret=intent.client_secret,
                amount=amount,
                currency=currency,
                status=intent.status,
                metadata=intent.metadata,
            )

        except StripeError as e:
            logger.error(f"Stripe payment intent creation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to create payment intent: {str(e)}")

    async def confirm_payment(
        self,
        provider_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """Confirm a Stripe payment intent."""
        try:
            confirm_params = {}
            if payment_method_id:
                confirm_params["payment_method"] = payment_method_id

            intent = stripe.PaymentIntent.confirm(
                provider_intent_id,
                **confirm_params
            )

            # Calculate fees if available
            fee_amount = None
            net_amount = None
            if intent.charges.data:
                charge = intent.charges.data[0]
                if charge.balance_transaction:
                    # Retrieve balance transaction for fee details
                    balance_transaction = stripe.BalanceTransaction.retrieve(
                        charge.balance_transaction
                    )
                    fee_amount = self._convert_amount_from_stripe(
                        balance_transaction.fee, intent.currency
                    )
                    net_amount = self._convert_amount_from_stripe(
                        balance_transaction.net, intent.currency
                    )

            return PaymentResult(
                success=intent.status == "succeeded",
                provider_payment_id=intent.id,
                status=intent.status,
                fee_amount=fee_amount,
                net_amount=net_amount,
                metadata=intent.metadata,
            )

        except StripeError as e:
            logger.error(f"Stripe payment confirmation failed: {str(e)}")
            return PaymentResult(
                success=False,
                status="failed",
                error_message=str(e),
            )

    async def retrieve_payment(self, provider_payment_id: str) -> PaymentResult:
        """Retrieve Stripe payment details."""
        try:
            intent = stripe.PaymentIntent.retrieve(provider_payment_id)

            fee_amount = None
            net_amount = None
            if intent.charges.data:
                charge = intent.charges.data[0]
                if charge.balance_transaction:
                    balance_transaction = stripe.BalanceTransaction.retrieve(
                        charge.balance_transaction
                    )
                    fee_amount = self._convert_amount_from_stripe(
                        balance_transaction.fee, intent.currency
                    )
                    net_amount = self._convert_amount_from_stripe(
                        balance_transaction.net, intent.currency
                    )

            return PaymentResult(
                success=intent.status == "succeeded",
                provider_payment_id=intent.id,
                status=intent.status,
                fee_amount=fee_amount,
                net_amount=net_amount,
                metadata=intent.metadata,
            )

        except StripeError as e:
            logger.error(f"Stripe payment retrieval failed: {str(e)}")
            raise PaymentProviderError(f"Failed to retrieve payment: {str(e)}")

    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RefundResult:
        """Refund a Stripe payment."""
        try:
            # First get the payment intent to get the charge ID
            intent = stripe.PaymentIntent.retrieve(provider_payment_id)
            if not intent.charges.data:
                raise PaymentProviderError("No charges found for this payment")

            charge_id = intent.charges.data[0].id

            refund_params = {
                "charge": charge_id,
                "metadata": metadata or {},
            }

            if amount:
                refund_params["amount"] = self._convert_amount_to_stripe(
                    amount, intent.currency
                )

            if reason:
                refund_params["reason"] = reason

            refund = stripe.Refund.create(**refund_params)

            return RefundResult(
                success=refund.status == "succeeded",
                provider_refund_id=refund.id,
                amount=self._convert_amount_from_stripe(refund.amount, intent.currency),
                status=refund.status,
                metadata=refund.metadata,
            )

        except StripeError as e:
            logger.error(f"Stripe refund failed: {str(e)}")
            return RefundResult(
                success=False,
                amount=amount or Decimal("0"),
                status="failed",
                error_message=str(e),
            )

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a Stripe customer."""
        try:
            customer_params = {
                "email": email,
                "metadata": metadata or {},
            }

            if name:
                customer_params["name"] = name

            customer = stripe.Customer.create(**customer_params)
            return customer.id

        except StripeError as e:
            logger.error(f"Stripe customer creation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to create customer: {str(e)}")

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionResult:
        """Create a Stripe subscription."""
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {},
                "expand": ["latest_invoice.payment_intent"],
            }

            if payment_method_id:
                subscription_params["default_payment_method"] = payment_method_id

            if trial_period_days:
                subscription_params["trial_period_days"] = trial_period_days

            subscription = stripe.Subscription.create(**subscription_params)

            return SubscriptionResult(
                success=subscription.status in ["active", "trialing"],
                provider_subscription_id=subscription.id,
                provider_customer_id=customer_id,
                status=subscription.status,
                current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                metadata=subscription.metadata,
            )

        except StripeError as e:
            logger.error(f"Stripe subscription creation failed: {str(e)}")
            return SubscriptionResult(
                success=False,
                status="failed",
                error_message=str(e),
            )

    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        at_period_end: bool = True,
    ) -> bool:
        """Cancel a Stripe subscription."""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    provider_subscription_id,
                    cancel_at_period_end=True
                )
                return subscription.cancel_at_period_end
            else:
                subscription = stripe.Subscription.delete(provider_subscription_id)
                return subscription.status == "canceled"

        except StripeError as e:
            logger.error(f"Stripe subscription cancellation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to cancel subscription: {str(e)}")

    async def validate_webhook(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> Dict[str, Any]:
        """Validate Stripe webhook signature and parse payload."""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, secret
            )
            return event

        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {str(e)}")
            raise PaymentProviderError("Invalid webhook payload")

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {str(e)}")
            raise PaymentProviderError("Invalid webhook signature")

    def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a Stripe Checkout session."""
        try:
            session_params = {
                "line_items": [{
                    "price": price_id,
                    "quantity": 1,
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata or {},
            }

            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_creation"] = "always"

            if trial_period_days:
                session_params["subscription_data"] = {
                    "trial_period_days": trial_period_days
                }

            session = stripe.checkout.Session.create(**session_params)
            return session.url

        except StripeError as e:
            logger.error(f"Stripe checkout session creation failed: {str(e)}")
            raise PaymentProviderError(f"Failed to create checkout session: {str(e)}")