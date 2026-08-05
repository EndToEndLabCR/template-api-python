"""
Tests for password routes (forgot-password, reset-password).

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest


class TestForgotPassword:
    """POST /api/v1/auth/forgot-password"""

    @pytest.mark.unit
    def test_forgot_password_with_valid_email_returns_200(
        self, client, mock_user_repository, sample_user_entity,
    ) -> None:
        """Forgot-password with a known email returns 200 + token."""
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock(return_value=sample_user_entity)

        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["message"] == "Password reset link sent to the frontend"

    @pytest.mark.unit
    def test_forgot_password_with_unknown_email_returns_404(
        self, client, mock_user_repository,
    ) -> None:
        """Forgot-password with an unknown email returns 404."""
        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "unknown@example.com"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "No user found with email" in data["detail"]

    @pytest.mark.unit
    def test_forgot_password_with_invalid_email_returns_422(self, client) -> None:
        """Forgot-password with an invalid email format returns 422."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422


class TestResetPassword:
    """POST /api/v1/auth/reset-password"""

    @pytest.mark.unit
    def test_reset_password_with_valid_token_returns_200(
        self, client, mock_user_repository, sample_user_entity,
    ) -> None:
        """Reset-password with a valid, non-expired token returns 200."""
        # Ensure the token expiry is in the future
        sample_user_entity.password_reset_expires_at = datetime.now() + timedelta(hours=1)

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock(return_value=sample_user_entity)

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "valid-token-value", "password": "NewStrongP@ss1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password has been reset successfully"

    @pytest.mark.unit
    def test_reset_password_with_invalid_token_returns_404(
        self, client, mock_user_repository,
    ) -> None:
        """Reset-password with an invalid token returns 404."""
        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid-token", "password": "NewStrongP@ss1"},
        )

        assert response.status_code == 404
        data = response.json()
        assert "Invalid or expired" in data["detail"]

    @pytest.mark.unit
    def test_reset_password_with_expired_token_returns_400(
        self, client, mock_user_repository, sample_user_entity,
    ) -> None:
        """Reset-password with an expired token returns 400."""
        # Set expiry in the past
        sample_user_entity.password_reset_expires_at = datetime.now() - timedelta(hours=1)

        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock(return_value=sample_user_entity)

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "expired-token", "password": "NewStrongP@ss1"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "expired" in data["detail"].lower()

    @pytest.mark.unit
    def test_reset_password_with_missing_fields_returns_422(self, client) -> None:
        """Reset-password with missing fields returns 422."""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "some-token"},
        )
        assert response.status_code == 422

    @pytest.mark.unit
    def test_reset_password_with_empty_body_returns_422(self, client) -> None:
        """Reset-password with an empty body returns 422."""
        response = client.post("/api/v1/auth/reset-password", json={})
        assert response.status_code == 422
