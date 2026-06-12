"""
Tests for PasswordService.

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.

NOTE: mock_user_repository uses ``spec`` (list of strings), which creates
regular Mock attributes, not AsyncMock.  Each async method must be
replaced with an explicit AsyncMock before use (same pattern as the
existing use-case tests).
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest


class TestPasswordService:
    """Suite of unit tests for PasswordService."""

    @pytest.mark.unit
    async def test_forgot_password_delegates_and_returns_response(
        self,
        password_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """forgot_password delegates to ForgotPasswordUseCase and returns a ForgotPasswordResponse."""
        from src.app.features.application.dtos.user_dto import ForgotPasswordResponse

        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock()

        result = await password_service.forgot_password(email="test@example.com")

        assert isinstance(result, ForgotPasswordResponse)
        assert result.message is not None
        assert result.token is not None
        # The use case should have set a token + expiry on the entity and saved it
        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.update.assert_awaited_once()

    @pytest.mark.unit
    async def test_reset_password_delegates_and_returns_response(
        self,
        password_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """reset_password delegates to ResetPasswordUseCase and returns a ResetPasswordResponse."""
        from src.app.features.application.dtos.user_dto import ResetPasswordResponse

        # The use case checks the token hash and expiry date.
        # Set a future expiry so the expiry check passes.
        sample_user_entity.password_reset_token_hash = "some_token_hash"
        sample_user_entity.password_reset_expires_at = datetime.now() + timedelta(hours=1)

        mock_user_repository.find_by_reset_token_hash = AsyncMock(
            return_value=sample_user_entity
        )
        mock_user_repository.update = AsyncMock()

        result = await password_service.reset_password(
            token="valid_token",
            password="NewStr0ng!",
        )

        assert isinstance(result, ResetPasswordResponse)
        assert result.message == "Password has been reset successfully"
        mock_user_repository.find_by_reset_token_hash.assert_awaited_once()
        mock_user_repository.update.assert_awaited_once()

    @pytest.mark.unit
    async def test_forgot_password_bubbles_exception(
        self,
        password_service,
        mock_user_repository,
    ) -> None:
        """forgot_password lets UserEmailNotFoundException propagate."""
        from src.app.features.application.exceptions.user_exception import UserEmailNotFoundException

        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        with pytest.raises(UserEmailNotFoundException):
            await password_service.forgot_password(email="unknown@example.com")

    @pytest.mark.unit
    async def test_reset_password_bubbles_invalid_token_exception(
        self,
        password_service,
        mock_user_repository,
    ) -> None:
        """reset_password lets InvalidResetTokenException propagate when token hash is unknown."""
        from src.app.features.application.exceptions.password_exception import InvalidResetTokenException

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=None)

        with pytest.raises(InvalidResetTokenException):
            await password_service.reset_password(
                token="bogus_token",
                password="NewStr0ng!",
            )

    @pytest.mark.unit
    async def test_reset_password_bubbles_expired_token_exception(
        self,
        password_service,
        mock_user_repository,
        sample_user_entity,
    ) -> None:
        """reset_password lets ExpiredResetTokenException propagate when token is expired."""
        from src.app.features.application.exceptions.password_exception import ExpiredResetTokenException

        # Set an already-expired timestamp so the use case raises
        sample_user_entity.password_reset_token_hash = "some_hash"
        sample_user_entity.password_reset_expires_at = datetime.now() - timedelta(hours=1)

        mock_user_repository.find_by_reset_token_hash = AsyncMock(
            return_value=sample_user_entity
        )

        with pytest.raises(ExpiredResetTokenException):
            await password_service.reset_password(
                token="expired_token",
                password="NewStr0ng!",
            )

    @pytest.mark.unit
    async def test_forgot_password_bubbles_value_error_for_invalid_email(
        self,
        password_service,
    ) -> None:
        """forgot_password lets ValueError propagate when email format is invalid."""
        with pytest.raises(ValueError, match="Invalid email format"):
            await password_service.forgot_password(email="not-an-email")
