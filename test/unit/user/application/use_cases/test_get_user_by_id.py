"""
Unit tests for GetUserByIdUseCase.

Covers:
- Happy path: existing user found by UUID
- User not found raises UserDoesNotExistException
- Malformed UUID raises ValueError

NOTE: mock_user_repository uses `spec` (list of strings), which creates
regular Mock attributes, not AsyncMock. Each async method must be
replaced with an explicit AsyncMock before use.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest


class TestGetUserByIdUseCase:

    @pytest.mark.unit
    async def test_get_user_by_id_success(self, mock_user_repository, sample_user_entity):
        """An existing user should be retrieved and returned as a UserResponse."""
        from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase

        use_case = GetUserByIdUseCase(mock_user_repository)
        user_id = str(sample_user_entity.id)

        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)

        result = await use_case.execute(user_id)

        assert result.id == user_id
        expected_fullname = f"{sample_user_entity.first_name} {sample_user_entity.last_name}"
        assert result.fullname == expected_fullname
        assert result.email == str(sample_user_entity.email)
        mock_user_repository.find_by_id.assert_awaited_once()

    @pytest.mark.unit
    async def test_get_user_by_id_not_found(self, mock_user_repository):
        """A non-existent user ID should raise UserDoesNotExistException."""
        from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase
        from src.app.features.application.exceptions.user_exception import UserDoesNotExistException

        use_case = GetUserByIdUseCase(mock_user_repository)
        user_id = str(uuid4())

        mock_user_repository.find_by_id = AsyncMock(return_value=None)

        with pytest.raises(UserDoesNotExistException, match=user_id):
            await use_case.execute(user_id)

        mock_user_repository.find_by_id.assert_awaited_once()

    @pytest.mark.unit
    async def test_get_user_by_id_invalid_uuid(self, mock_user_repository):
        """A malformed UUID string should raise ValueError."""
        from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase

        use_case = GetUserByIdUseCase(mock_user_repository)

        with pytest.raises(ValueError, match="Invalid UUID"):
            await use_case.execute("not-a-valid-uuid")
