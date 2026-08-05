"""
E2E tests for user lifecycle flows.

Tests exercise full HTTP request/response via the client fixture
(TestClient with overridden dependencies). All app imports are
inside test functions to guarantee APP_ENV=test is set first.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest


@pytest.mark.e2e
class TestFullUserLifecycle:
    """Complete user lifecycle: register → get → login → delete → verify gone."""

    def test_full_user_lifecycle(self, client, mock_user_repository, sample_user_entity) -> None:
        """Register, fetch, login, delete, and confirm deletion."""
        user_id = str(sample_user_entity.id)
        # Step 1: Register → 201
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)

        register_resp = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "password": "StrongP@ss1",
            },
        )
        assert register_resp.status_code == 201
        register_data = register_resp.json()
        assert register_data["id"] == user_id
        assert register_data["fullname"] == "Test User"
        assert register_data["email"] == "test@example.com"

        # Step 2: Get by ID → 200, matches registered user
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        get_resp = client.get(f"/v1/user/{user_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["id"] == user_id
        assert get_data["fullname"] == "Test User"
        assert get_data["email"] == "test@example.com"

        # Step 3: Login → 200, access_token + name
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        with patch(
            "src.app.features.domain.value_objects.password.Password.verify",
            return_value=True,
        ):
            login_resp = client.post(
                "/api/v1/login",
                json={"email": "test@example.com", "password": "StrongP@ss1"},
            )
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        assert login_data["name"] == "Test"

        # Step 4: Delete → 204
        mock_user_repository.delete = AsyncMock(return_value=sample_user_entity)
        delete_resp = client.delete(f"/v1/user/{user_id}")
        assert delete_resp.status_code == 204
        assert delete_resp.content == b""

        # Step 5: Get deleted user → 404
        mock_user_repository.find_by_id = AsyncMock(return_value=None)
        get_gone_resp = client.get(f"/v1/user/{user_id}")
        assert get_gone_resp.status_code == 404
        assert "does not exist" in get_gone_resp.json()["detail"].lower()


@pytest.mark.e2e
class TestDuplicateRegistration:
    """Attempting to register with an existing email."""

    def test_duplicate_registration(self, client, mock_user_repository, sample_user_entity) -> None:
        """First registration succeeds; second with same email returns 409."""
        # First registration: no existing user → save succeeds
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)

        first_resp = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "password": "StrongP@ss1",
            },
        )
        assert first_resp.status_code == 201

        # Second registration: user already exists
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        second_resp = client.post(
            "/v1/user/register",
            json={
                "firstName": "Another",
                "lastName": "User",
                "email": "test@example.com",
                "password": "OtherP@ss1",
            },
        )
        assert second_resp.status_code == 409
        assert "already exists" in second_resp.json()["detail"].lower()


@pytest.mark.e2e
class TestLoginWithInvalidCredentials:
    """Login attempts that should be rejected."""

    def test_login_with_unregistered_email(self, client, mock_user_repository) -> None:
        """Login with an unknown email returns 401."""
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        response = client.post(
            "/api/v1/login",
            json={"email": "unknown@example.com", "password": "AnyPass1!"},
        )
        assert response.status_code == 401
        assert "invalid email or password" in response.json()["detail"].lower()

    def test_login_with_wrong_password(self, client, mock_user_repository, sample_user_entity) -> None:
        """Login with correct email but wrong password returns 401."""
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
        assert "invalid email or password" in response.json()["detail"].lower()

    def test_login_with_malformed_email(self, client) -> None:
        """Login with an invalid email format returns 422."""
        response = client.post(
            "/api/v1/login",
            json={"email": "not-an-email", "password": "ValidPass1!"},
        )
        assert response.status_code == 422


@pytest.mark.e2e
class TestPasswordResetFlow:
    """Forgot-password → reset-password lifecycle."""

    def test_password_reset_success(self, client, mock_user_repository, sample_user_entity) -> None:
        """Request reset with valid email → get token → reset password."""
        # Step 1: Forgot password → 200 with token
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock(return_value=sample_user_entity)

        forgot_resp = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"},
        )
        assert forgot_resp.status_code == 200
        forgot_data = forgot_resp.json()
        assert "token" in forgot_data
        assert forgot_data["message"] == "Password reset link sent to the frontend"
        reset_token = forgot_data["token"]

        # Step 2: Reset password with valid token → 200
        sample_user_entity.password_reset_expires_at = datetime.now() + timedelta(hours=1)
        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=sample_user_entity)
        mock_user_repository.update = AsyncMock(return_value=sample_user_entity)

        reset_resp = client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "password": "NewStrongP@ss1"},
        )
        assert reset_resp.status_code == 200
        assert reset_resp.json()["message"] == "Password has been reset successfully"

    def test_reset_password_with_invalid_token(self, client, mock_user_repository) -> None:
        """Reset password with an unrecognised token returns 404."""
        mock_user_repository.find_by_reset_token_hash = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "invalid-token-value", "password": "NewStrongP@ss1"},
        )
        assert response.status_code == 404
        assert "invalid or expired" in response.json()["detail"].lower()

    def test_forgot_password_with_unknown_email(self, client, mock_user_repository) -> None:
        """Request password reset for an email that does not exist returns 404."""
        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nobody@example.com"},
        )
        assert response.status_code == 404
        assert "no user found with email" in response.json()["detail"].lower()


@pytest.mark.e2e
class TestDeleteNonExistentUser:
    """DELETE on a user that does not exist."""

    def test_delete_non_existent_user(self, client, mock_user_repository) -> None:
        """Delete with a random UUID returns 404."""
        mock_user_repository.delete = AsyncMock(return_value=None)

        response = client.delete(f"/v1/user/{uuid4()}")
        assert response.status_code == 404
        assert "does not exist" in response.json()["detail"].lower()
