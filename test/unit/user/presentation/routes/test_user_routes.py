"""
Tests for user routes (register, get by ID, delete).

All app imports are inside test functions to guarantee env vars
(APP_ENV=test) are set before any application code is loaded.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest


class TestCreateUser:
    """POST /v1/user/register"""

    @pytest.mark.unit
    def test_register_with_valid_data_returns_201(self, client, mock_user_repository, sample_user_entity) -> None:
        """Register with valid data returns 201 and the created user."""
        mock_user_repository.find_by_email = AsyncMock(return_value=None)
        mock_user_repository.save = AsyncMock(return_value=sample_user_entity)

        response = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "newuser@example.com",
                "password": "StrongP@ss1",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"

    @pytest.mark.unit
    def test_register_with_duplicate_email_returns_409(self, client, mock_user_repository, sample_user_entity) -> None:
        """Register with an existing email returns 409."""
        mock_user_repository.find_by_email = AsyncMock(return_value=sample_user_entity)

        response = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "existing@example.com",
                "password": "StrongP@ss1",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"]

    @pytest.mark.unit
    def test_register_with_weak_password_returns_400(self, client, mock_user_repository) -> None:
        """Register with a weak password returns 400."""
        response = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "newuser@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @pytest.mark.unit
    def test_register_with_invalid_email_returns_422(self, client) -> None:
        """Register with an invalid email returns 422 (Pydantic validation)."""
        response = client.post(
            "/v1/user/register",
            json={
                "firstName": "Test",
                "lastName": "User",
                "email": "not-an-email",
                "password": "StrongP@ss1",
            },
        )
        assert response.status_code == 422

    @pytest.mark.unit
    def test_register_with_missing_fields_returns_422(self, client) -> None:
        """Register with missing required fields returns 422."""
        response = client.post(
            "/v1/user/register",
            json={"firstName": "Test"},
        )
        assert response.status_code == 422


class TestGetUserById:
    """GET /v1/user/{user_id}"""

    @pytest.mark.unit
    def test_get_existing_user_returns_200(self, client, mock_user_repository, sample_user_entity) -> None:
        """Get user by ID for an existing user returns 200 + user data."""
        mock_user_repository.find_by_id = AsyncMock(return_value=sample_user_entity)
        user_id = str(sample_user_entity.id)

        response = client.get(f"/v1/user/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["fullname"] == "Test User"
        assert data["id"] == user_id

    @pytest.mark.unit
    def test_get_non_existing_user_returns_404(self, client, mock_user_repository) -> None:
        """Get user by ID for a non-existing user returns 404."""
        mock_user_repository.find_by_id = AsyncMock(return_value=None)

        response = client.get(f"/v1/user/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "does not exist" in data["detail"]

    @pytest.mark.unit
    def test_get_user_with_invalid_uuid_returns_422(self, client) -> None:
        """Get user by ID with a non-UUID path param returns 422 (FastAPI validation)."""
        response = client.get("/v1/user/not-a-uuid")
        assert response.status_code == 422


class TestDeleteUserById:
    """DELETE /v1/user/{user_id}"""

    @pytest.mark.unit
    def test_delete_existing_user_returns_204(self, client, mock_user_repository, sample_user_entity) -> None:
        """Delete user by ID for an existing user returns 204 with no body."""
        mock_user_repository.delete = AsyncMock(return_value=sample_user_entity)
        user_id = str(sample_user_entity.id)

        response = client.delete(f"/v1/user/{user_id}")

        assert response.status_code == 204
        assert response.content == b""

    @pytest.mark.unit
    def test_delete_non_existing_user_returns_404(self, client, mock_user_repository) -> None:
        """Delete user by ID for a non-existing user returns 404."""
        mock_user_repository.delete = AsyncMock(return_value=None)

        response = client.delete(f"/v1/user/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "does not exist" in data["detail"]

    @pytest.mark.unit
    def test_delete_user_with_invalid_uuid_returns_422(self, client) -> None:
        """Delete user by ID with a non-UUID path param returns 422 (FastAPI validation)."""
        response = client.delete("/v1/user/not-a-uuid")
        assert response.status_code == 422
