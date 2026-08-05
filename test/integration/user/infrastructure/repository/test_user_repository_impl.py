"""
Integration tests for UserRepositoryImpl.

Covers real repository logic:
- SQLAlchemy query construction (.get(), .execute() with select())
- Entity to model mapping via map_model_to_entity
- Error handling: DatabaseConnectionError, UserAlreadyExistsException, rollbacks
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

import pytest


# ---------------------------------------------------------------------------
# Helper: mock UserModel factory
# ---------------------------------------------------------------------------
def create_mock_user_model(**overrides):
    """Create a MagicMock that mimics a SQLAlchemy UserModel instance.

    Override any field by passing it as a keyword argument.
    Defaults produce a valid in-memory representation.
    """
    model = MagicMock()
    model.id = overrides.get("id", uuid4())
    model.email = overrides.get("email", "test@example.com")
    model.first_name = overrides.get("first_name", "Test")
    model.last_name = overrides.get("last_name", "User")
    model.password_hash = overrides.get("password_hash", "$2b$12$hash")
    model.password_reset_token_hash = overrides.get("password_reset_token_hash", None)
    model.password_reset_expires_at = overrides.get("password_reset_expires_at", None)
    model.created_at = overrides.get("created_at", datetime.now())
    model.updated_at = overrides.get("updated_at", datetime.now())
    return model


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_db_session():
    """Mocked SQLAlchemy AsyncSession.

    Async methods (get, execute, commit, refresh, rollback, delete, close)
    are ``AsyncMock`` so the implementation can ``await`` them.
    ``add`` is a plain ``MagicMock`` because ``AsyncSession.add()`` is synchronous.
    """
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def repo(mock_db_session):
    from src.app.features.infrastructure.repository.user_repository_impl import \
        UserRepositoryImpl
    return UserRepositoryImpl(mock_db_session)


# ===================================================================
# find_by_id
# ===================================================================
@pytest.mark.integration
class TestFindById:

    async def test_find_by_id_returns_mapped_entity(self, mock_db_session, repo):
        """Happy path: existing user is found and mapped to UserEntity."""
        from src.shared.domain.value_objects.entity_id import EntityId

        user_id = uuid4()
        user_model = create_mock_user_model(id=user_id)
        mock_db_session.get.return_value = user_model

        entity = await repo.find_by_id(EntityId(user_id))

        mock_db_session.get.assert_awaited_once()
        assert entity is not None
        assert entity.id.value == user_id
        assert entity.email.value == user_model.email
        assert entity.first_name == user_model.first_name
        assert entity.last_name == user_model.last_name
        assert entity.password_hash == user_model.password_hash

    async def test_find_by_id_returns_none_when_not_found(self, mock_db_session, repo):
        """When db_session.get returns None, the repo returns None."""
        from src.shared.domain.value_objects.entity_id import EntityId

        mock_db_session.get.return_value = None

        entity = await repo.find_by_id(EntityId(uuid4()))

        assert entity is None
        mock_db_session.get.assert_awaited_once()

    async def test_find_by_id_raises_database_connection_error(self, mock_db_session, repo):
        """OperationalError from db_session.get is wrapped in DatabaseConnectionError."""
        from sqlalchemy.exc import OperationalError
        from src.app.features.infrastructure.repository.user_repository_impl import \
            DatabaseConnectionError
        from src.shared.domain.value_objects.entity_id import EntityId

        op_error = OperationalError("SELECT ...", {}, Exception("connection refused"))
        mock_db_session.get.side_effect = op_error

        with pytest.raises(DatabaseConnectionError, match="Failed to connect to the database"):
            await repo.find_by_id(EntityId(uuid4()))


# ===================================================================
# find_by_email
# ===================================================================
@pytest.mark.integration
class TestFindByEmail:

    async def test_find_by_email_returns_mapped_entity(self, mock_db_session, repo):
        """Happy path: existing email returns a mapped UserEntity."""
        from src.app.features.domain.value_objects.email import Email

        user_model = create_mock_user_model()
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = user_model
        mock_db_session.execute.return_value = mock_execute_result

        entity = await repo.find_by_email(Email("test@example.com"))

        mock_db_session.execute.assert_awaited_once()
        assert entity is not None
        assert entity.email.value == "test@example.com"
        assert entity.first_name == user_model.first_name
        assert entity.last_name == user_model.last_name

    async def test_find_by_email_returns_none_when_not_found(self, mock_db_session, repo):
        """When execute returns no rows, the repo returns None."""
        from src.app.features.domain.value_objects.email import Email

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_execute_result

        entity = await repo.find_by_email(Email("unknown@example.com"))

        assert entity is None
        mock_db_session.execute.assert_awaited_once()


# ===================================================================
# find_by_reset_token_hash
# ===================================================================
@pytest.mark.integration
class TestFindByResetTokenHash:

    async def test_find_by_token_hash_returns_mapped_entity(self, mock_db_session, repo):
        """Happy path: matching token hash returns a mapped UserEntity."""
        user_model = create_mock_user_model(password_reset_token_hash="abc123hash")
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = user_model
        mock_db_session.execute.return_value = mock_execute_result

        entity = await repo.find_by_reset_token_hash("abc123hash")

        mock_db_session.execute.assert_awaited_once()
        assert entity is not None
        assert entity.password_reset_token_hash == "abc123hash"

    async def test_find_by_token_hash_returns_none_when_not_found(self, mock_db_session, repo):
        """When no user has the given token hash, returns None."""
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_execute_result

        entity = await repo.find_by_reset_token_hash("nonexistent_hash")

        assert entity is None
        mock_db_session.execute.assert_awaited_once()

    async def test_find_by_token_hash_raises_database_connection_error(self, mock_db_session, repo):
        """OperationalError from execute is wrapped in DatabaseConnectionError."""
        from sqlalchemy.exc import OperationalError
        from src.app.features.infrastructure.repository.user_repository_impl import \
            DatabaseConnectionError

        op_error = OperationalError("SELECT ...", {}, Exception("connection lost"))
        mock_db_session.execute.side_effect = op_error

        with pytest.raises(DatabaseConnectionError, match="Failed to connect to the database"):
            await repo.find_by_reset_token_hash("some_hash")


# ===================================================================
# save
# ===================================================================
@pytest.mark.integration
class TestSave:

    async def test_save_creates_user_successfully(self, mock_db_session, repo):
        """Happy path: user is saved, committed, refreshed, and returned as entity."""
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        user_id = uuid4()
        user_entity = UserEntity(
            id=EntityId(user_id),
            email=Email("newuser@example.com"),
            first_name="Jane",
            last_name="Doe",
            password_hash="$2b$12$realhash",
        )

        # No duplicate email
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_execute_result

        entity = await repo.save(user_entity)

        mock_db_session.execute.assert_awaited_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once()
        assert entity.id.value == user_id
        assert entity.email.value == "newuser@example.com"
        assert entity.first_name == "Jane"
        assert entity.last_name == "Doe"

    async def test_save_raises_on_duplicate_email(self, mock_db_session, repo):
        """When a user with the same email already exists, raises UserAlreadyExistsException."""
        from src.app.features.application.exceptions.user_exception import \
            UserAlreadyExistsException
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        user_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("dupe@example.com"),
            first_name="Dup",
            last_name="User",
            password_hash="$2b$12$hash",
        )

        # Duplicate email: execute returns an existing model
        existing = create_mock_user_model(email="dupe@example.com")
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = existing
        mock_db_session.execute.return_value = mock_execute_result

        with pytest.raises(UserAlreadyExistsException, match="dupe@example.com"):
            await repo.save(user_entity)

        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()

    async def test_save_rollback_and_raise_on_integrity_error(self, mock_db_session, repo):
        """IntegrityError from commit triggers rollback and raises UserAlreadyExistsException."""
        from sqlalchemy.exc import IntegrityError
        from src.app.features.application.exceptions.user_exception import \
            UserAlreadyExistsException
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        user_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("conflict@example.com"),
            first_name="Conflict",
            last_name="User",
            password_hash="$2b$12$hash",
        )

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_execute_result
        mock_db_session.commit.side_effect = IntegrityError(
            "INSERT ...", {}, Exception("duplicate key"),
        )

        with pytest.raises(UserAlreadyExistsException, match="conflict@example.com"):
            await repo.save(user_entity)

        mock_db_session.rollback.assert_awaited_once()

    async def test_save_rollback_and_raise_on_generic_error(self, mock_db_session, repo):
        """Any non-IntegrityError from commit triggers rollback and re-raises."""
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        user_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("error@example.com"),
            first_name="Error",
            last_name="User",
            password_hash="$2b$12$hash",
        )

        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_execute_result
        mock_db_session.commit.side_effect = RuntimeError("disk full")

        with pytest.raises(RuntimeError, match="disk full"):
            await repo.save(user_entity)

        mock_db_session.rollback.assert_awaited_once()


# ===================================================================
# update
# ===================================================================
@pytest.mark.integration
class TestUpdate:

    async def test_update_existing_user(self, mock_db_session, repo):
        """Happy path: existing user is updated, committed, refreshed, and returned."""
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        user_id = uuid4()
        existing_model = create_mock_user_model(
            id=user_id,
            email="old@example.com",
            first_name="Old",
            last_name="Name",
        )
        mock_db_session.get.return_value = existing_model

        updated_entity = UserEntity(
            id=EntityId(user_id),
            email=Email("new@example.com"),
            first_name="New",
            last_name="Name",
            password_hash="$2b$12$newhash",
            password_reset_token_hash="resettoken",
            password_reset_expires_at=datetime(2026, 6, 8, 12, 0, 0),
        )

        entity = await repo.update(updated_entity)

        mock_db_session.get.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once()
        assert entity is not None
        assert entity.id.value == user_id
        assert entity.email.value == "new@example.com"
        assert entity.first_name == "New"
        assert entity.last_name == "Name"
        assert entity.password_hash == "$2b$12$newhash"
        assert entity.password_reset_token_hash == "resettoken"

    async def test_update_returns_none_when_not_found(self, mock_db_session, repo):
        """When user does not exist, update returns None."""
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        mock_db_session.get.return_value = None

        updated_entity = UserEntity(
            id=EntityId(uuid4()),
            email=Email("ghost@example.com"),
            first_name="Ghost",
            last_name="User",
            password_hash="$2b$12$hash",
        )

        entity = await repo.update(updated_entity)

        assert entity is None
        mock_db_session.get.assert_awaited_once()
        mock_db_session.commit.assert_not_called()

    async def test_update_raises_database_connection_error(self, mock_db_session, repo):
        """OperationalError from get is wrapped in DatabaseConnectionError."""
        from sqlalchemy.exc import OperationalError
        from src.app.features.infrastructure.repository.user_repository_impl import \
            DatabaseConnectionError
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        op_error = OperationalError("UPDATE ...", {}, Exception("connection lost"))
        mock_db_session.get.side_effect = op_error

        updated_entity = UserEntity(
            id=EntityId(uuid4()),
            email=Email("fail@example.com"),
            first_name="Fail",
            last_name="User",
            password_hash="$2b$12$hash",
        )

        with pytest.raises(DatabaseConnectionError, match="Failed to connect to the database"):
            await repo.update(updated_entity)


# ===================================================================
# delete
# ===================================================================
@pytest.mark.integration
class TestDelete:

    async def test_delete_existing_user_returns_true(self, mock_db_session, repo):
        """Happy path: existing user is deleted and returns True."""
        from src.shared.domain.value_objects.entity_id import EntityId

        user_model = create_mock_user_model()
        mock_db_session.get.return_value = user_model

        result = await repo.delete(EntityId(uuid4()))

        assert result is True
        mock_db_session.get.assert_awaited_once()
        mock_db_session.delete.assert_awaited_once_with(user_model)
        mock_db_session.commit.assert_awaited_once()

    async def test_delete_non_existent_user_returns_false(self, mock_db_session, repo):
        """When user does not exist, delete returns False."""
        from src.shared.domain.value_objects.entity_id import EntityId

        mock_db_session.get.return_value = None

        result = await repo.delete(EntityId(uuid4()))

        assert result is False
        mock_db_session.get.assert_awaited_once()
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    async def test_delete_raises_database_connection_error(self, mock_db_session, repo):
        """OperationalError from get is wrapped in DatabaseConnectionError."""
        from sqlalchemy.exc import OperationalError
        from src.app.features.infrastructure.repository.user_repository_impl import \
            DatabaseConnectionError
        from src.shared.domain.value_objects.entity_id import EntityId

        op_error = OperationalError("DELETE ...", {}, Exception("connection lost"))
        mock_db_session.get.side_effect = op_error

        with pytest.raises(DatabaseConnectionError, match="Failed to connect to the database"):
            await repo.delete(EntityId(uuid4()))
