"""
Tests for auth routes (login endpoint).

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestLogin:
    """POST /api/v1/login"""

    @pytest.mark.unit
    def test_valid_credentials_returns_token(self, client, mock_user_repository, sample_user_entity) -> None:
        """Login with valid email + password returns 200 and an access token."""
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)

        with patch(
            "src.app.features.domain.value_objects.password.Password.verify",
            return_value=True,
        ):
            response = client.post(
                "/api/v1/login",
                json={"email": "test@example.com", "password": "ValidPass1!"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["name"] == "Test"

    @pytest.mark.unit
    def test_invalid_credentials_returns_401(self, client, mock_user_repository) -> None:
        """Login with unknown email returns 401."""
        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/login",
            json={"email": "unknown@example.com", "password": "AnyPass1!"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    @pytest.mark.unit
    def test_wrong_password_returns_401(self, client, mock_user_repository, sample_user_entity) -> None:
        """Login with wrong password returns 401."""
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)

        with patch(
            "src.app.features.domain.value_objects.password.Password.verify",
            return_value=False,
        ):
            response = client.post(
                "/api/v1/login",
                json={"email": "test@example.com", "password": "WrongPass1!"},
            )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    @pytest.mark.unit
    def test_invalid_email_format_returns_422(self, client) -> None:
        """Login with an invalid email format returns 422 (Pydantic validation)."""
        response = client.post(
            "/api/v1/login",
            json={"email": "not-an-email", "password": "ValidPass1!"},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    def test_empty_body_returns_422(self, client) -> None:
        """Login with an empty JSON body returns 422 (missing required fields)."""
        response = client.post("/api/v1/login", json={})
        assert response.status_code == 422

    @pytest.mark.unit
    def test_missing_content_type_returns_422(self, client) -> None:
        """Login without JSON content type returns 422."""
        response = client.post("/api/v1/login", data="not-json")
        assert response.status_code == 422
