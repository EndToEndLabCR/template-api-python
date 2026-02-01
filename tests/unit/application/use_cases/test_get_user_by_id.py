"""
Unit tests for GetUserByIdUseCase.

This module contains comprehensive tests for the GetUserByIdUseCase,
including edge cases like invalid UUID formats and non-existent users.
"""
import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException
from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.value_objects.email import Email
from src.shared.domain.value_objects.entity_id import EntityId


class TestGetUserByIdUseCase:
    """Test suite for GetUserByIdUseCase."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_user_repository):
        """Create a GetUserByIdUseCase instance with mocked dependencies."""
        return GetUserByIdUseCase(mock_user_repository)

    @pytest.fixture
    def valid_user_id(self):
        """Generate a valid UUID string."""
        return str(uuid4())

    @pytest.fixture
    def mock_user_entity(self, valid_user_id):
        """Create a mock user entity."""
        entity_id = EntityId.from_string(valid_user_id)
        email = Email("john.doe@example.com")
        return UserEntity(
            id=entity_id,
            email=email,
            first_name="John",
            last_name="Doe"
        )

    @pytest.mark.asyncio
    async def test_execute_successful_retrieval(
        self, use_case, mock_user_repository, valid_user_id, mock_user_entity
    ):
        """Test successful user retrieval by ID."""
        # Arrange
        mock_user_repository.find_by_id.return_value = mock_user_entity

        # Act
        result = await use_case.execute(valid_user_id)

        # Assert
        assert result is not None
        assert result.id == valid_user_id
        assert result.fullname == "John Doe"
        assert result.email == "john.doe@example.com"
        mock_user_repository.find_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_user_not_found(self, use_case, mock_user_repository, valid_user_id):
        """Test that UserDoesNotExistException is raised when user is not found."""
        # Arrange
        mock_user_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserDoesNotExistException) as exc_info:
            await use_case.execute(valid_user_id)

        assert exc_info.value.user_id == valid_user_id
        assert f"User with ID {valid_user_id} does not exist" in str(exc_info.value)
        mock_user_repository.find_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_invalid_uuid_format(self, use_case, mock_user_repository):
        """Test that ValueError is raised for invalid UUID format."""
        # Arrange
        invalid_user_id = "not-a-valid-uuid"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await use_case.execute(invalid_user_id)

        assert "Invalid UUID format" in str(exc_info.value)
        mock_user_repository.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_empty_string_uuid(self, use_case, mock_user_repository):
        """Test that ValueError is raised for empty string UUID."""
        # Arrange
        empty_user_id = ""

        # Act & Assert
        with pytest.raises(ValueError):
            await use_case.execute(empty_user_id)

        mock_user_repository.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_repository_exception(
        self, use_case, mock_user_repository, valid_user_id
    ):
        """Test that repository exceptions are propagated."""
        # Arrange
        mock_user_repository.find_by_id.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await use_case.execute(valid_user_id)

        assert "Database connection error" in str(exc_info.value)
        mock_user_repository.find_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_calls_repository_with_correct_entity_id(
        self, use_case, mock_user_repository, valid_user_id, mock_user_entity
    ):
        """Test that the use case calls repository with properly formatted EntityId."""
        # Arrange
        mock_user_repository.find_by_id.return_value = mock_user_entity

        # Act
        await use_case.execute(valid_user_id)

        # Assert
        call_args = mock_user_repository.find_by_id.call_args[0][0]
        assert isinstance(call_args, EntityId)
        assert str(call_args.value) == valid_user_id
