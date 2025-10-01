"""
Base payment provider interface for SkillForge AI Payment Service
PCI Compliant payment processing abstraction
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class PaymentProviderError(Exception):
    """Base payment provider exception."""
    pass


class PaymentIntentData(BaseModel):
    """Payment intent data structure."""
    provider_intent_id: str
    client_secret: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    metadata: Dict[str, Any] = {}


class PaymentResult(BaseModel):
    """Payment processing result."""
    success: bool
    provider_payment_id: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    metadata: Dict[str, Any] = {}


class RefundResult(BaseModel):
    """Refund processing result."""
    success: bool
    provider_refund_id: Optional[str] = None
    amount: Decimal
    status: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class SubscriptionResult(BaseModel):
    """Subscription creation result."""
    success: bool
    provider_subscription_id: Optional[str] = None
    provider_customer_id: Optional[str] = None
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BasePaymentProvider(ABC):
    """Base class for payment providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize payment provider with configuration."""
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration."""
        pass

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentIntentData:
        """
        Create a payment intent.

        Args:
            amount: Payment amount
            currency: ISO currency code
            customer_id: Customer ID (optional)
            payment_method_id: Payment method ID (optional)
            metadata: Additional metadata

        Returns:
            PaymentIntentData with intent information

        Raises:
            PaymentProviderError: If intent creation fails
        """
        pass

    @abstractmethod
    async def confirm_payment(
        self,
        provider_intent_id: str,
        payment_method_id: Optional[str] = None,
    ) -> PaymentResult:
        """
        Confirm a payment intent.

        Args:
            provider_intent_id: Provider's payment intent ID
            payment_method_id: Payment method ID (if not attached to intent)

        Returns:
            PaymentResult with processing outcome

        Raises:
            PaymentProviderError: If payment confirmation fails
        """
        pass

    @abstractmethod
    async def retrieve_payment(self, provider_payment_id: str) -> PaymentResult:
        """
        Retrieve payment details.

        Args:
            provider_payment_id: Provider's payment ID

        Returns:
            PaymentResult with payment details

        Raises:
            PaymentProviderError: If retrieval fails
        """
        pass

    @abstractmethod
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RefundResult:
        """
        Refund a payment.

        Args:
            provider_payment_id: Provider's payment ID
            amount: Refund amount (optional, defaults to full refund)
            reason: Refund reason
            metadata: Additional metadata

        Returns:
            RefundResult with refund information

        Raises:
            PaymentProviderError: If refund fails
        """
        pass

    @abstractmethod
    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a customer in the provider.

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata

        Returns:
            Provider customer ID

        Raises:
            PaymentProviderError: If customer creation fails
        """
        pass

    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionResult:
        """
        Create a subscription.

        Args:
            customer_id: Provider customer ID
            price_id: Provider price/plan ID
            payment_method_id: Default payment method
            trial_period_days: Trial period length
            metadata: Additional metadata

        Returns:
            SubscriptionResult with subscription information

        Raises:
            PaymentProviderError: If subscription creation fails
        """
        pass

    @abstractmethod
    async def cancel_subscription(
        self,
        provider_subscription_id: str,
        at_period_end: bool = True,
    ) -> bool:
        """
        Cancel a subscription.

        Args:
            provider_subscription_id: Provider's subscription ID
            at_period_end: Cancel at end of current period

        Returns:
            True if cancellation was successful

        Raises:
            PaymentProviderError: If cancellation fails
        """
        pass

    @abstractmethod
    async def validate_webhook(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> Dict[str, Any]:
        """
        Validate webhook signature and parse payload.

        Args:
            payload: Raw webhook payload
            signature: Webhook signature
            secret: Webhook secret

        Returns:
            Parsed webhook data

        Raises:
            PaymentProviderError: If validation fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def supported_currencies(self) -> List[str]:
        """List of supported currencies."""
        pass