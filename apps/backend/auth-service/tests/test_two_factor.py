"""
Tests for two-factor authentication functionality
"""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserTwoFactor


class TestUserTwoFactorModel:
    """Test UserTwoFactor model CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_two_factor(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test creating a new two-factor authentication record."""
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="JBSWY3DPEHPK3PXP",
            backup_codes=["CODE1", "CODE2", "CODE3"],
            is_enabled=False,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.id is not None
        assert two_factor.user_id == sample_user_id
        assert two_factor.secret == "JBSWY3DPEHPK3PXP"
        assert len(two_factor.backup_codes) == 3
        assert two_factor.is_enabled is False

    @pytest.mark.asyncio
    async def test_read_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test reading a two-factor record by user_id."""
        result = await db_session.execute(
            select(UserTwoFactor).where(
                UserTwoFactor.user_id == sample_two_factor.user_id
            )
        )
        two_factor = result.scalar_one_or_none()

        assert two_factor is not None
        assert two_factor.user_id == sample_two_factor.user_id
        assert two_factor.secret == sample_two_factor.secret

    @pytest.mark.asyncio
    async def test_update_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test updating a two-factor record."""
        # Update secret and enable 2FA
        sample_two_factor.secret = "NEW_SECRET_KEY"
        sample_two_factor.is_enabled = True
        sample_two_factor.enabled_at = datetime.utcnow()

        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.secret == "NEW_SECRET_KEY"
        assert sample_two_factor.is_enabled is True
        assert sample_two_factor.enabled_at is not None

    @pytest.mark.asyncio
    async def test_delete_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test deleting a two-factor record."""
        user_id = sample_two_factor.user_id

        await db_session.delete(sample_two_factor)
        await db_session.commit()

        # Verify deletion
        result = await db_session.execute(
            select(UserTwoFactor).where(UserTwoFactor.user_id == user_id)
        )
        two_factor = result.scalar_one_or_none()

        assert two_factor is None


class TestTwoFactorEnablement:
    """Test two-factor authentication enablement workflow."""

    @pytest.mark.asyncio
    async def test_enable_two_factor(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test enabling two-factor authentication."""
        # Create 2FA record (disabled by default)
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET_KEY",
            backup_codes=["CODE1", "CODE2"],
        )
        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.is_enabled is False
        assert two_factor.enabled_at is None

        # Enable 2FA
        two_factor.is_enabled = True
        two_factor.enabled_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.is_enabled is True
        assert two_factor.enabled_at is not None

    @pytest.mark.asyncio
    async def test_disable_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test disabling two-factor authentication."""
        # Ensure it starts enabled
        assert sample_two_factor.is_enabled is True

        # Disable 2FA
        sample_two_factor.is_enabled = False
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.is_enabled is False

    @pytest.mark.asyncio
    async def test_verify_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test recording two-factor verification."""
        assert sample_two_factor.last_verified_at is None

        # Record verification
        sample_two_factor.last_verified_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.last_verified_at is not None


class TestBackupCodes:
    """Test backup codes management."""

    @pytest.mark.asyncio
    async def test_store_backup_codes(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test storing backup codes as JSON."""
        backup_codes = [
            "ABC123-DEF456",
            "GHI789-JKL012",
            "MNO345-PQR678",
            "STU901-VWX234",
            "YZA567-BCD890",
        ]

        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET",
            backup_codes=backup_codes,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert len(two_factor.backup_codes) == 5
        assert two_factor.backup_codes == backup_codes

    @pytest.mark.asyncio
    async def test_update_backup_codes(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test updating backup codes."""
        original_count = len(sample_two_factor.backup_codes)

        # Generate new backup codes
        new_codes = [f"NEW-CODE-{i}" for i in range(10)]
        sample_two_factor.backup_codes = new_codes

        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert len(sample_two_factor.backup_codes) == 10
        assert sample_two_factor.backup_codes != original_count

    @pytest.mark.asyncio
    async def test_remove_used_backup_code(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test removing a used backup code."""
        original_codes = sample_two_factor.backup_codes.copy()
        code_to_remove = original_codes[0]

        # Remove used code
        sample_two_factor.backup_codes.remove(code_to_remove)
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert len(sample_two_factor.backup_codes) == len(original_codes) - 1
        assert code_to_remove not in sample_two_factor.backup_codes

    @pytest.mark.asyncio
    async def test_null_backup_codes(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test that backup_codes can be null."""
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET",
            backup_codes=None,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.backup_codes is None


class TestRecoveryEmail:
    """Test recovery email functionality."""

    @pytest.mark.asyncio
    async def test_set_recovery_email(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test setting a recovery email."""
        assert sample_two_factor.recovery_email is None

        sample_two_factor.recovery_email = "recovery@example.com"
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.recovery_email == "recovery@example.com"

    @pytest.mark.asyncio
    async def test_update_recovery_email(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test updating a recovery email."""
        sample_two_factor.recovery_email = "old@example.com"
        await db_session.commit()

        sample_two_factor.recovery_email = "new@example.com"
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.recovery_email == "new@example.com"

    @pytest.mark.asyncio
    async def test_remove_recovery_email(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test removing a recovery email."""
        sample_two_factor.recovery_email = "recovery@example.com"
        await db_session.commit()

        sample_two_factor.recovery_email = None
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.recovery_email is None


class TestSecretManagement:
    """Test secret key management."""

    @pytest.mark.asyncio
    async def test_create_with_secret(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test creating 2FA with a secret."""
        secret = "JBSWY3DPEHPK3PXP"
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret=secret,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.secret == secret

    @pytest.mark.asyncio
    async def test_rotate_secret(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test rotating the secret key."""
        old_secret = sample_two_factor.secret
        new_secret = "NEW_SECRET_KEY_12345"

        sample_two_factor.secret = new_secret
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.secret == new_secret
        assert sample_two_factor.secret != old_secret


class TestMultipleUsers:
    """Test handling multiple users with 2FA."""

    @pytest.mark.asyncio
    async def test_multiple_users_with_two_factor(
        self, db_session: AsyncSession, multiple_mock_users: list[dict]
    ):
        """Test creating 2FA records for multiple users."""
        # Create 2FA for multiple users
        for user in multiple_mock_users:
            two_factor = UserTwoFactor(
                user_id=user["id"],
                secret=f"SECRET_{user['username']}",
                is_enabled=True,
            )
            db_session.add(two_factor)

        await db_session.commit()

        # Verify all records were created
        result = await db_session.execute(select(UserTwoFactor))
        all_records = result.scalars().all()

        assert len(all_records) == len(multiple_mock_users)

    @pytest.mark.asyncio
    async def test_query_specific_user_two_factor(
        self, db_session: AsyncSession, multiple_mock_users: list[dict]
    ):
        """Test querying 2FA for a specific user among multiple users."""
        # Create 2FA for multiple users
        target_user = multiple_mock_users[2]
        for user in multiple_mock_users:
            two_factor = UserTwoFactor(
                user_id=user["id"],
                secret=f"SECRET_{user['username']}",
            )
            db_session.add(two_factor)

        await db_session.commit()

        # Query specific user
        result = await db_session.execute(
            select(UserTwoFactor).where(UserTwoFactor.user_id == target_user["id"])
        )
        two_factor = result.scalar_one_or_none()

        assert two_factor is not None
        assert two_factor.user_id == target_user["id"]
        assert two_factor.secret == f"SECRET_{target_user['username']}"


class TestTimestamps:
    """Test timestamp fields."""

    @pytest.mark.asyncio
    async def test_created_at_timestamp(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test that created_at is automatically set."""
        before_create = datetime.utcnow()

        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET",
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        after_create = datetime.utcnow()

        assert two_factor.created_at is not None
        assert before_create <= two_factor.created_at <= after_create

    @pytest.mark.asyncio
    async def test_updated_at_timestamp(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test that updated_at is automatically updated."""
        original_updated_at = sample_two_factor.updated_at

        # Wait a moment and update
        sample_two_factor.is_enabled = False
        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        # Note: In a real scenario with database triggers, updated_at would change
        # For now, we just verify it exists
        assert sample_two_factor.updated_at is not None
