"""
Tests for database migrations and schema setup for auth-service
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.models import UserTwoFactor


class TestDatabaseSchema:
    """Test database schema and table creation."""

    @pytest.mark.asyncio
    async def test_user_two_factor_table_exists(self, engine: AsyncEngine):
        """Test that user_two_factor table is created."""
        async with engine.connect() as conn:
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            tables = inspector.get_table_names()
            assert "user_two_factor" in tables

    @pytest.mark.asyncio
    async def test_user_two_factor_columns(self, engine: AsyncEngine):
        """Test that user_two_factor table has all required columns."""
        async with engine.connect() as conn:
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            columns = {
                col["name"]: col
                for col in inspector.get_columns("user_two_factor")
            }

            # Check all required columns exist
            required_columns = [
                "id",
                "user_id",
                "secret",
                "backup_codes",
                "is_enabled",
                "enabled_at",
                "last_verified_at",
                "recovery_email",
                "created_at",
                "updated_at",
            ]

            for col_name in required_columns:
                assert col_name in columns, f"Column {col_name} not found"

    @pytest.mark.asyncio
    async def test_user_two_factor_primary_key(self, engine: AsyncEngine):
        """Test that id is the primary key."""
        async with engine.connect() as conn:
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            pk = inspector.get_pk_constraint("user_two_factor")
            assert pk["constrained_columns"] == ["id"]

    @pytest.mark.asyncio
    async def test_user_two_factor_unique_constraint(self, engine: AsyncEngine):
        """Test that user_id has unique constraint."""
        async with engine.connect() as conn:
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            unique_constraints = inspector.get_unique_constraints("user_two_factor")

            # Check if user_id is in unique constraints
            user_id_unique = any(
                "user_id" in constraint["column_names"]
                for constraint in unique_constraints
            )
            assert user_id_unique, "user_id should have unique constraint"

    @pytest.mark.asyncio
    async def test_user_two_factor_indexes(self, engine: AsyncEngine):
        """Test that proper indexes exist on user_two_factor table."""
        async with engine.connect() as conn:
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            indexes = inspector.get_indexes("user_two_factor")

            # Check if there's an index on user_id
            user_id_indexed = any(
                "user_id" in index["column_names"]
                for index in indexes
            )
            assert user_id_indexed, "user_id should be indexed"


class TestMigrationWithoutUsersTable:
    """Test that migrations work correctly when users table doesn't exist."""

    @pytest.mark.asyncio
    async def test_create_table_without_fk_constraint(self, engine: AsyncEngine):
        """
        Test that user_two_factor table can be created even when users table
        doesn't exist. This simulates the CI/CD test environment where each
        service has its own isolated database.
        """
        async with engine.connect() as conn:
            # Verify that users table does NOT exist (test isolation)
            inspector = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn)
            )
            tables = inspector.get_table_names()
            assert "users" not in tables, "users table should not exist in test env"

            # Verify that user_two_factor table DOES exist
            assert "user_two_factor" in tables

    @pytest.mark.asyncio
    async def test_fk_constraint_not_enforced_in_test(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """
        Test that we can create user_two_factor records even without users table.
        This validates that our EXCEPTION block in the migration works correctly.
        """
        # Create a UserTwoFactor record with a user_id that doesn't exist in users table
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="TEST_SECRET_KEY_12345",
            is_enabled=False,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        # Verify it was created successfully
        assert two_factor.id is not None
        assert two_factor.user_id == sample_user_id
        assert two_factor.secret == "TEST_SECRET_KEY_12345"


class TestDatabaseOperations:
    """Test basic database operations on user_two_factor table."""

    @pytest.mark.asyncio
    async def test_insert_user_two_factor(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test inserting a new user_two_factor record."""
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="JBSWY3DPEHPK3PXP",
            backup_codes=["CODE1", "CODE2", "CODE3"],
            is_enabled=True,
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.id is not None
        assert two_factor.user_id == sample_user_id
        assert two_factor.is_enabled is True
        assert len(two_factor.backup_codes) == 3

    @pytest.mark.asyncio
    async def test_query_user_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test querying user_two_factor records."""
        result = await db_session.execute(
            text("SELECT * FROM user_two_factor WHERE user_id = :user_id"),
            {"user_id": sample_two_factor.user_id}
        )
        row = result.fetchone()

        assert row is not None
        assert str(row.user_id) == sample_two_factor.user_id

    @pytest.mark.asyncio
    async def test_update_user_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test updating a user_two_factor record."""
        # Update the record
        sample_two_factor.is_enabled = False
        sample_two_factor.recovery_email = "recovery@example.com"

        await db_session.commit()
        await db_session.refresh(sample_two_factor)

        assert sample_two_factor.is_enabled is False
        assert sample_two_factor.recovery_email == "recovery@example.com"

    @pytest.mark.asyncio
    async def test_delete_user_two_factor(
        self, db_session: AsyncSession, sample_two_factor: UserTwoFactor
    ):
        """Test deleting a user_two_factor record."""
        user_id = sample_two_factor.user_id

        await db_session.delete(sample_two_factor)
        await db_session.commit()

        # Verify deletion
        result = await db_session.execute(
            text("SELECT * FROM user_two_factor WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.fetchone()
        assert row is None

    @pytest.mark.asyncio
    async def test_unique_user_id_constraint(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test that user_id unique constraint is enforced."""
        # Create first record
        two_factor1 = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET1",
            is_enabled=False,
        )
        db_session.add(two_factor1)
        await db_session.commit()

        # Try to create second record with same user_id
        two_factor2 = UserTwoFactor(
            user_id=sample_user_id,
            secret="SECRET2",
            is_enabled=False,
        )
        db_session.add(two_factor2)

        # Should raise an exception due to unique constraint
        with pytest.raises(Exception) as exc_info:
            await db_session.commit()

        # Verify it's a unique constraint violation
        assert "unique" in str(exc_info.value).lower() or "duplicate" in str(exc_info.value).lower()


class TestDefaultValues:
    """Test default values for columns."""

    @pytest.mark.asyncio
    async def test_default_is_enabled_false(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test that is_enabled defaults to False."""
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="TEST_SECRET",
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.is_enabled is False

    @pytest.mark.asyncio
    async def test_timestamps_auto_populated(
        self, db_session: AsyncSession, sample_user_id: str
    ):
        """Test that created_at and updated_at are automatically populated."""
        two_factor = UserTwoFactor(
            user_id=sample_user_id,
            secret="TEST_SECRET",
        )

        db_session.add(two_factor)
        await db_session.commit()
        await db_session.refresh(two_factor)

        assert two_factor.created_at is not None
        assert two_factor.updated_at is not None
