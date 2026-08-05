"""
Unit tests for ResetPasswordUseCase.

Covers:
- Happy path: valid token with future expiry resets password
- Invalid token hash raises InvalidResetTokenException
- Expired token (past expiry) raises ExpiredResetTokenException
- Token with None expiry raises ExpiredResetTokenException

NOTE: mock_user_repository uses `spec` (list of strings), which creates
regular Mock attributes, not AsyncMock. Each async method must be
replaced with an explicit AsyncMock before use.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest


class TestResetPasswordUseCase:

    @pytest.mark.unit
    async def test_reset_password_success(self, mock_user_repository):
        """A valid non-expired token should reset the password successfully."""
        from src.app.features.application.use_cases.reset_password import ResetPasswordUseCase
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        use_case = ResetPasswordUseCase(mock_user_repository)

        user_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="$2b$12$oldhashfortesting",
            password_reset_token_hash="somehash",
            password_reset_expires_at=datetime.now() + timedelta(hours=1),
        )

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=user_entity)
        mock_user_repository.update = AsyncMock()

        result = await use_case.execute("valid-token", "NewV@lid1")

        assert result.message == "Password has been reset successfully"
        mock_user_repository.find_by_reset_token_hash.assert_awaited_once()
        mock_user_repository.update.assert_awaited_once()

    @pytest.mark.unit
    async def test_reset_password_invalid_token(self, mock_user_repository):
        """An unknown token hash should raise InvalidResetTokenException."""
        from src.app.features.application.use_cases.reset_password import ResetPasswordUseCase
        from src.app.features.application.exceptions.password_exception import InvalidResetTokenException

        use_case = ResetPasswordUseCase(mock_user_repository)

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=None)

        with pytest.raises(InvalidResetTokenException):
            await use_case.execute("invalid-token", "NewV@lid1")

        mock_user_repository.find_by_reset_token_hash.assert_awaited_once()
        mock_user_repository.update.assert_not_called()

    @pytest.mark.unit
    async def test_reset_password_expired_token(self, mock_user_repository):
        """A token past its expiry should raise ExpiredResetTokenException."""
        from src.app.features.application.use_cases.reset_password import ResetPasswordUseCase
        from src.app.features.application.exceptions.password_exception import ExpiredResetTokenException
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        use_case = ResetPasswordUseCase(mock_user_repository)

        expired_entity = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="$2b$12$oldhash",
            password_reset_token_hash="somehash",
            password_reset_expires_at=datetime.now() - timedelta(hours=1),
        )

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=expired_entity)

        with pytest.raises(ExpiredResetTokenException):
            await use_case.execute("expired-token", "NewV@lid1")

        mock_user_repository.find_by_reset_token_hash.assert_awaited_once()
        mock_user_repository.update.assert_not_called()

    @pytest.mark.unit
    async def test_reset_password_none_expiry(self, mock_user_repository):
        """A token with None expiry should raise ExpiredResetTokenException."""
        from src.app.features.application.use_cases.reset_password import ResetPasswordUseCase
        from src.app.features.application.exceptions.password_exception import ExpiredResetTokenException
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        use_case = ResetPasswordUseCase(mock_user_repository)

        entity_no_expiry = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="$2b$12$oldhash",
            password_reset_token_hash="somehash",
            password_reset_expires_at=None,
        )

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=entity_no_expiry)

        with pytest.raises(ExpiredResetTokenException):
            await use_case.execute("token-no-expiry", "NewV@lid1")

        mock_user_repository.find_by_reset_token_hash.assert_awaited_once()
        mock_user_repository.update.assert_not_called()
