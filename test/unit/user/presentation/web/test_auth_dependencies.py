"""
Tests for auth_dependencies (get_current_user).

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.

NOTE: These tests call get_current_user() directly with mocked
dependencies rather than going through the TestClient, because the
client fixture overrides get_current_user entirely.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException, status


class TestGetCurrentUser:
    """get_current_user dependency"""

    @pytest.mark.unit
    async def test_valid_token_returns_user_entity(self, sample_user_entity) -> None:
        """A valid Bearer token with an existing user returns the user entity."""
        credentials_mock = MagicMock()
        credentials_mock.credentials = "valid_token"
        session_mock = AsyncMock()

        with patch(
            "src.app.features.presentation.web.auth_dependencies.decode_access_token",
        ) as mock_decode:
            mock_decode.return_value = {"sub": str(sample_user_entity.id)}

            with patch(
                "src.app.features.presentation.web.auth_dependencies.UserRepositoryImpl",
            ) as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.find_by_id.return_value = sample_user_entity
                mock_repo_class.return_value = mock_repo

                from src.app.features.presentation.web.auth_dependencies import (
                    get_current_user,
                )

                result = await get_current_user(
                    credentials=credentials_mock,
                    session=session_mock,
                )

        assert result is sample_user_entity
        mock_decode.assert_called_once_with("valid_token")
        mock_repo.find_by_id.assert_awaited_once_with(
            str(sample_user_entity.id),
        )

    @pytest.mark.unit
    async def test_missing_sub_in_token_returns_401(self) -> None:
        """A valid token without a 'sub' claim raises HTTPException 401."""
        credentials_mock = MagicMock()
        credentials_mock.credentials = "token_no_sub"
        session_mock = AsyncMock()

        with patch(
            "src.app.features.presentation.web.auth_dependencies.decode_access_token",
        ) as mock_decode:
            mock_decode.return_value = {}  # no "sub" key

            with patch(
                "src.app.features.presentation.web.auth_dependencies.UserRepositoryImpl",
            ):
                from src.app.features.presentation.web.auth_dependencies import (
                    get_current_user,
                )

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials_mock,
                        session=session_mock,
                    )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.unit
    async def test_invalid_token_returns_401(self) -> None:
        """An invalid/expired token raises HTTPException 401."""
        credentials_mock = MagicMock()
        credentials_mock.credentials = "expired_token"
        session_mock = AsyncMock()

        with patch(
            "src.app.features.presentation.web.auth_dependencies.decode_access_token",
        ) as mock_decode:
            mock_decode.side_effect = jwt.PyJWTError("expired or invalid")

            from src.app.features.presentation.web.auth_dependencies import (
                get_current_user,
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    credentials=credentials_mock,
                    session=session_mock,
                )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.unit
    async def test_valid_token_non_existing_user_returns_401(
        self,
        sample_user_entity,
    ) -> None:
        """A valid token for a non-existing user raises HTTPException 401."""
        credentials_mock = MagicMock()
        credentials_mock.credentials = "valid_token"
        session_mock = AsyncMock()

        with patch(
            "src.app.features.presentation.web.auth_dependencies.decode_access_token",
        ) as mock_decode:
            mock_decode.return_value = {"sub": str(sample_user_entity.id)}

            with patch(
                "src.app.features.presentation.web.auth_dependencies.UserRepositoryImpl",
            ) as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.find_by_id.return_value = None
                mock_repo_class.return_value = mock_repo

                from src.app.features.presentation.web.auth_dependencies import (
                    get_current_user,
                )

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(
                        credentials=credentials_mock,
                        session=session_mock,
                    )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail
