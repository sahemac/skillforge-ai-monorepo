"""
Security utilities for SkillForge AI Payment Service
PCI Compliance security measures
"""

import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
import hashlib
import hmac

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PCISecurityManager:
    """PCI DSS compliant security manager."""

    def __init__(self):
        """Initialize security manager."""
        self._cipher = None
        self._init_encryption()

    def _init_encryption(self):
        """Initialize encryption cipher."""
        if settings.ENCRYPTION_KEY:
            # Use provided key
            key = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode())
        else:
            # Generate a key from a password (in production, use proper key management)
            password = settings.SECRET_KEY.encode()
            salt = b'skillforge_payment_salt'  # In production, use random salt per environment
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))

        self._cipher = Fernet(key)

    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive data (PCI DSS requirement).

        Args:
            data: Sensitive data to encrypt

        Returns:
            Base64 encoded encrypted data
        """
        try:
            encrypted_data = self._cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.

        Args:
            encrypted_data: Base64 encoded encrypted data

        Returns:
            Decrypted data
        """
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def mask_card_number(self, card_number: str) -> str:
        """
        Mask credit card number for logging (PCI DSS requirement).
        Shows only last 4 digits.

        Args:
            card_number: Full card number

        Returns:
            Masked card number
        """
        if len(card_number) <= 4:
            return "*" * len(card_number)

        return "*" * (len(card_number) - 4) + card_number[-4:]

    def mask_email(self, email: str) -> str:
        """
        Mask email for logging (privacy protection).

        Args:
            email: Full email address

        Returns:
            Masked email
        """
        if '@' not in email:
            return email[:2] + "*" * (len(email) - 2)

        username, domain = email.split('@', 1)
        if len(username) <= 2:
            masked_username = "*" * len(username)
        else:
            masked_username = username[:2] + "*" * (len(username) - 2)

        return f"{masked_username}@{domain}"

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure token.

        Args:
            length: Token length in bytes

        Returns:
            Base64 encoded secure token
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode()

    def hash_webhook_signature(self, payload: bytes, secret: str) -> str:
        """
        Generate HMAC signature for webhook validation.

        Args:
            payload: Webhook payload
            secret: Webhook secret

        Returns:
            HMAC signature
        """
        return hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
        signature_header: str = "sha256="
    ) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Provided signature
            secret: Webhook secret
            signature_header: Signature header prefix

        Returns:
            True if signature is valid
        """
        try:
            expected_signature = self.hash_webhook_signature(payload, secret)

            # Remove signature header if present
            if signature.startswith(signature_header):
                signature = signature[len(signature_header):]

            # Use secure comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False

    def sanitize_payment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize payment data for logging (remove sensitive fields).

        Args:
            data: Payment data dictionary

        Returns:
            Sanitized data dictionary
        """
        sensitive_fields = {
            'card_number', 'cvv', 'cvc', 'security_code',
            'account_number', 'routing_number', 'bank_account',
            'ssn', 'social_security_number', 'tax_id'
        }

        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()

            if key_lower in sensitive_fields:
                sanitized[key] = "[REDACTED]"
            elif key_lower == 'email' and isinstance(value, str):
                sanitized[key] = self.mask_email(value)
            elif 'card' in key_lower and isinstance(value, str) and len(value) > 10:
                sanitized[key] = self.mask_card_number(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_payment_data(value)
            else:
                sanitized[key] = value

        return sanitized

    def audit_log(self, action: str, user_id: Optional[str], data: Dict[str, Any]):
        """
        Create audit log entry for PCI compliance.

        Args:
            action: Action performed
            user_id: User who performed action
            data: Additional data (will be sanitized)
        """
        sanitized_data = self.sanitize_payment_data(data)

        audit_entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": settings.PROJECT_NAME,
            "data": sanitized_data
        }

        # In production, send to dedicated audit log system
        logger.info(f"AUDIT: {audit_entry}")


# Global security manager instance
security_manager = PCISecurityManager()


def get_security_manager() -> PCISecurityManager:
    """Get security manager instance."""
    return security_manager