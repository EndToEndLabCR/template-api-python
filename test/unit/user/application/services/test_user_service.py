"""
Tests for UserService.

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.

NOTE: mock_user_repository uses ``spec`` (list of strings), which creates
regular Mock attributes, not AsyncMock.  Each async method must be
replaced with an explicit AsyncMock before use (same pattern as the
existing use-case tests).
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestUserService:
    """Suite of unit tests for UserService."""

    @pytest.mark.unit
    async def test_create_user_delegates_to_use_case_and_returns_result(
        self,
        user_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """create_user delegates to CreateUserUseCase and returns a UserResponse."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest, UserResponse

        # The use case checks for duplicates first
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="StrongP@ss1",
        )

        result = await user_service.create_user(payload)

        assert isinstance(result, UserResponse)
        assert result.email == "test@example.com"
        assert result.fullname == "Test User"
        mock_user_repository.save.assert_awaited_once()

    @pytest.mark.unit
    async def test_get_user_by_id_delegates_and_returns_result(
        self,
        user_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """get_user_by_id delegates to GetUserByIdUseCase and returns a UserResponse."""
        from src.app.features.application.dtos.user_dto import UserResponse

        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        user_id = str(sample_user_entity.id)

        result = await user_service.get_user_by_id(user_id)

        assert isinstance(result, UserResponse)
        assert result.email == "test@example.com"
        mock_user_repository.find_by_id.assert_awaited_once()

    @pytest.mark.unit
    async def test_delete_user_by_id_delegates_and_returns_true(
        self,
        user_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """delete_user_by_id delegates to DeleteUserByIdUseCase and returns True."""
        mock_user_repository.delete = AsyncMock(return_value=sample_user_entity)
        user_id = str(sample_user_entity.id)

        result = await user_service.delete_user_by_id(user_id)

        assert result is True
        mock_user_repository.delete.assert_awaited_once()

    @pytest.mark.unit
    async def test_authenticate_user_with_valid_credentials_returns_user(
        self,
        user_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """authenticate_user returns the user entity when email + password are valid."""
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)

        with patch(
            "src.app.features.domain.value_objects.password.Password.verify",
            return_value=True,
        ):
            result = await user_service.authenticate_user(
                email="test@example.com",
                password="correct_password",
            )

        assert result is sample_user_entity
        mock_user_repository.find_by_email.assert_awaited_once()

    @pytest.mark.unit
    async def test_authenticate_user_with_unregistered_email_raises_exception(
        self,
        user_service,
        mock_user_repository,
    ) -> None:
        """authenticate_user raises InvalidCredentialsException when the email is not found."""
        from src.app.features.application.exceptions.auth_exception import InvalidCredentialsException

        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        with pytest.raises(InvalidCredentialsException) as exc_info:
            await user_service.authenticate_user(
                email="unknown@example.com",
                password="any_password",
            )

        assert "Invalid email or password" in str(exc_info.value)

    @pytest.mark.unit
    async def test_authenticate_user_with_wrong_password_raises_exception(
        self,
        user_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """authenticate_user raises InvalidCredentialsException when the password is wrong."""
        from src.app.features.application.exceptions.auth_exception import InvalidCredentialsException

        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)

        with patch(
            "src.app.features.domain.value_objects.password.Password.verify",
            return_value=False,
        ):
            with pytest.raises(InvalidCredentialsException) as exc_info:
                await user_service.authenticate_user(
                    email="test@example.com",
                    password="wrong_password",
                )

        assert "Invalid email or password" in str(exc_info.value)

    @pytest.mark.unit
    async def test_authenticate_user_when_user_not_found_raises_exception(
        self,
        user_service,
        mock_user_repository,
    ) -> None:
        """authenticate_user raises InvalidCredentialsException when no user exists for the email."""
        from src.app.features.application.exceptions.auth_exception import InvalidCredentialsException

        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        with pytest.raises(InvalidCredentialsException):
            await user_service.authenticate_user(
                email="nonexistent@example.com",
                password="does_not_matter",
            )
