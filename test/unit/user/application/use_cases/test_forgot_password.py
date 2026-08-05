"""
Unit tests for ForgotPasswordUseCase.

Covers:
- Happy path: valid email generates reset token
- Email not found raises UserEmailNotFoundException
- Invalid email format raises ValueError

NOTE: mock_user_repository uses `spec` (list of strings), which creates
regular Mock attributes, not AsyncMock. Each async method must be
replaced with an explicit AsyncMock before use.
"""

from unittest.mock import AsyncMock

import pytest


class TestForgotPasswordUseCase:

    @pytest.mark.unit
    async def test_forgot_password_success(self, mock_user_repository, sample_user_entity):
        """A valid email for an existing user should generate a reset token."""
        from src.app.features.application.use_cases.forgot_password import ForgotPasswordUseCase

        use_case = ForgotPasswordUseCase(mock_user_repository)
        email = "test@example.com"

        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock()

        result = await use_case.execute(email)

        assert result.message == "Password reset link sent to the frontend"
        assert isinstance(result.token, str)
        assert len(result.token) > 0
        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.update.assert_awaited_once()

    @pytest.mark.unit
    async def test_forgot_password_email_not_found(self, mock_user_repository):
        """An email with no matching user should raise UserEmailNotFoundException."""
        from src.app.features.application.use_cases.forgot_password import ForgotPasswordUseCase
        from src.app.features.application.exceptions.user_exception import UserEmailNotFoundException

        use_case = ForgotPasswordUseCase(mock_user_repository)
        email = "unknown@example.com"

        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        with pytest.raises(UserEmailNotFoundException, match="unknown@example.com"):
            await use_case.execute(email)

        mock_user_repository.find_by_email.assert_awaited_once()
        mock_user_repository.update.assert_not_called()

    @pytest.mark.unit
    async def test_forgot_password_invalid_email(self, mock_user_repository):
        """A malformed email string should raise ValueError."""
        from src.app.features.application.use_cases.forgot_password import ForgotPasswordUseCase

        use_case = ForgotPasswordUseCase(mock_user_repository)

        with pytest.raises(ValueError, match="Invalid email format"):
            await use_case.execute("not-an-email")
