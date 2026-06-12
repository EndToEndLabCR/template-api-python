"""
Unit tests for CreateUserUseCase.

Covers:
- Happy path: valid payload creates user successfully
- Duplicate email raises UserAlreadyExistsException
- Weak password raises ValueError
- Repository failure propagates exception

NOTE: mock_user_repository uses `spec` (list of strings), which creates
regular Mock attributes, not AsyncMock. Each async method must be
replaced with an explicit AsyncMock before use.
"""

from unittest.mock import AsyncMock

import pytest


class TestCreateUserUseCase:

    @pytest.mark.unit
    async def test_create_user_success(self, mock_user_repository):
        """Valid payload should create a user and return a UserResponse."""
        from src.app.features.application.use_cases.create_user import CreateUserUseCase
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        use_case = CreateUserUseCase(mock_user_repository)

        payload = UserCreateRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="ValidP@ss1",
        )

        created_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("john@example.com"),
            first_name="John",
            last_name="Doe",
            password_hash="$2b$12$dummyhashfortesting",
        )

        # Replace spec-created Mock attributes with proper AsyncMocks
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(return_value=created_entity)

        result = await use_case.execute(payload)

        assert result.id == str(created_entity.id)
        assert result.fullname == "John Doe"
        assert result.email == "john@example.com"
        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.save.assert_awaited_once()

    @pytest.mark.unit
    async def test_create_user_duplicate_email(self, mock_user_repository):
        """Creating a user with an already-registered email should raise."""
        from src.app.features.application.use_cases.create_user import CreateUserUseCase
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.exceptions.user_exception import UserAlreadyExistsException
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        use_case = CreateUserUseCase(mock_user_repository)

        payload = UserCreateRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="ValidP@ss1",
        )

        existing_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("john@example.com"),
            first_name="Existing",
            last_name="User",
            password_hash="$2b$12$dummyhash",
        )

        mock_user_repository.find_by_email = AsyncMock(return_value=existing_entity)

        with pytest.raises(UserAlreadyExistsException, match="john@example.com"):
            await use_case.execute(payload)

        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.unit
    async def test_create_user_invalid_password(self, mock_user_repository):
        """A payload with a weak password should raise ValueError."""
        from src.app.features.application.use_cases.create_user import CreateUserUseCase
        from src.app.features.application.dtos.user_dto import UserCreateRequest

        use_case = CreateUserUseCase(mock_user_repository)

        payload = UserCreateRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="weak",
        )

        with pytest.raises(ValueError, match="at least 8 characters"):
            await use_case.execute(payload)

        mock_user_repository.find_by_email.assert_not_called()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.unit
    async def test_create_user_repository_save_error(self, mock_user_repository):
        """A repository failure during save should propagate."""
        from src.app.features.application.use_cases.create_user import CreateUserUseCase
        from src.app.features.application.dtos.user_dto import UserCreateRequest

        use_case = CreateUserUseCase(mock_user_repository)

        payload = UserCreateRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="ValidP@ss1",
        )

        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(side_effect=Exception("DB connection error"))

        with pytest.raises(Exception, match="DB connection error"):
            await use_case.execute(payload)

        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.save.assert_awaited_once()
