"""
Integration tests for user routes.

This module contains integration tests for the user API endpoints,
including edge cases and error scenarios for the 'Get User by ID' flow.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient

from src.app.app import fastApiApp
from src.app.features.application.services.user_service import UserService
from src.app.features.application.dtos.user_dto import UserResponse
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException


class TestUserRoutes:
    """Test suite for user routes integration tests."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(fastApiApp)

    @pytest.fixture
    def valid_user_id(self):
        """Generate a valid UUID string."""
        return str(uuid4())

    @pytest.fixture
    def mock_user_response(self, valid_user_id):
        """Create a mock UserResponse object."""
        return UserResponse(
            id=valid_user_id,
            fullname="John Doe",
            email="john.doe@example.com"
        )

    def test_get_user_by_id_success(self, client, valid_user_id, mock_user_response):
        """Test successful retrieval of user by ID."""
        # Arrange
        mock_service = AsyncMock(spec=UserService)
        mock_service.get_user_by_id.return_value = mock_user_response

        def mock_get_service():
            return mock_service

        # Apply the mock at the dependency level
        fastApiApp.dependency_overrides[
            __import__('src.app.features.presentation.web.dependencies', fromlist=['get_user_service']).get_user_service
        ] = mock_get_service

        try:
            # Act
            response = client.get(f"/v1/user/{valid_user_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == valid_user_id
            assert data["fullname"] == "John Doe"
            assert data["email"] == "john.doe@example.com"
        finally:
            # Clean up
            fastApiApp.dependency_overrides = {}

    def test_get_user_by_id_invalid_uuid(self, client):
        """Test that invalid UUID format returns 422 error (FastAPI validation)."""
        # Act
        response = client.get("/v1/user/invalid-uuid")

        # Assert
        # FastAPI returns 422 for invalid UUID format in path parameter
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_user_by_id_user_not_found(self, client, valid_user_id):
        """Test that non-existent user returns 404 error."""
        # Arrange
        mock_service = AsyncMock(spec=UserService)
        mock_service.get_user_by_id.side_effect = UserDoesNotExistException(valid_user_id)

        def mock_get_service():
            return mock_service

        fastApiApp.dependency_overrides[
            __import__('src.app.features.presentation.web.dependencies', fromlist=['get_user_service']).get_user_service
        ] = mock_get_service

        try:
            # Act
            response = client.get(f"/v1/user/{valid_user_id}")

            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert f"User with ID {valid_user_id} does not exist" in data["detail"]
        finally:
            # Clean up
            fastApiApp.dependency_overrides = {}

    def test_get_user_by_id_empty_uuid(self, client):
        """Test that empty UUID path parameter is handled correctly."""
        # Act
        response = client.get("/v1/user/")

        # Assert
        # FastAPI will return 404 for missing path parameter
        assert response.status_code == 404

    def test_get_user_by_id_malformed_uuid_format(self, client):
        """Test various malformed UUID formats."""
        malformed_uuids = [
            "123",
            "not-a-uuid",
            "12345678-1234-1234-1234",
            "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        ]

        for malformed_uuid in malformed_uuids:
            # Act
            response = client.get(f"/v1/user/{malformed_uuid}")

            # Assert
            # FastAPI validation returns 422 for invalid UUID format
            assert response.status_code == 422, f"Failed for UUID: {malformed_uuid}"
            data = response.json()
            assert "detail" in data

    def test_get_user_by_id_response_format(self, client, valid_user_id, mock_user_response):
        """Test that response follows the expected UserResponse format."""
        # Arrange
        mock_service = AsyncMock(spec=UserService)
        mock_service.get_user_by_id.return_value = mock_user_response

        def mock_get_service():
            return mock_service

        fastApiApp.dependency_overrides[
            __import__('src.app.features.presentation.web.dependencies', fromlist=['get_user_service']).get_user_service
        ] = mock_get_service

        try:
            # Act
            response = client.get(f"/v1/user/{valid_user_id}")

            # Assert
            assert response.status_code == 200
            data = response.json()
            # Check that required fields are present
            assert "id" in data
            assert "fullname" in data
            assert "email" in data
            # Check that types are correct
            assert isinstance(data["id"], str)
            assert isinstance(data["fullname"], str)
            assert isinstance(data["email"], str)
        finally:
            # Clean up
            fastApiApp.dependency_overrides = {}
