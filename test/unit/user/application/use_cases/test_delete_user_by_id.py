"""
Unit tests for DeleteUserByIdUseCase.

Covers:
- Happy path: existing user deleted successfully
- User not found raises UserDoesNotExistException
- Malformed UUID raises ValueError

NOTE: mock_user_repository uses `spec` (list of strings), which creates
regular Mock attributes, not AsyncMock. Each async method must be
replaced with an explicit AsyncMock before use.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest


class TestDeleteUserByIdUseCase:

    @pytest.mark.unit
    async def test_delete_user_by_id_success(self, mock_user_repository):
        """Deleting an existing user should return True."""
        from src.app.features.application.use_cases.delete_user_by_id import DeleteUserByIdUseCase

        use_case = DeleteUserByIdUseCase(mock_user_repository)
        user_id = str(uuid4())

        mock_user_repository.delete = AsyncMock(return_value=True)

        result = await use_case.execute(user_id)

        assert result is True
        mock_user_repository.delete.assert_awaited_once()

    @pytest.mark.unit
    async def test_delete_user_by_id_not_found(self, mock_user_repository):
        """Deleting a non-existent user should raise UserDoesNotExistException."""
        from src.app.features.application.use_cases.delete_user_by_id import DeleteUserByIdUseCase
        from src.app.features.application.exceptions.user_exception import UserDoesNotExistException

        use_case = DeleteUserByIdUseCase(mock_user_repository)
        user_id = str(uuid4())

        mock_user_repository.delete = AsyncMock(return_value=None)

        with pytest.raises(UserDoesNotExistException, match=user_id):
            await use_case.execute(user_id)

        mock_user_repository.delete.assert_awaited_once()

    @pytest.mark.unit
    async def test_delete_user_by_id_invalid_uuid(self, mock_user_repository):
        """A malformed UUID string should raise ValueError."""
        from src.app.features.application.use_cases.delete_user_by_id import DeleteUserByIdUseCase

        use_case = DeleteUserByIdUseCase(mock_user_repository)

        with pytest.raises(ValueError, match="Invalid UUID"):
            await use_case.execute("not-a-valid-uuid")
