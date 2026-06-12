"""
Unit tests for the DTO mapper module (user_dto_mapper.py).

Covers:
- map_entity_to_dto_user: field mapping, special characters in names
- map_create_request_to_entity: field trimming, email normalization,
  password hash passthrough, unique ID generation
- Round-trip: create request -> entity -> response preserves data
"""

import pytest


class TestMapEntityToDtoUser:
    """Tests for map_entity_to_dto_user."""

    @pytest.mark.unit
    def test_maps_all_fields_correctly(self) -> None:
        """Should map id to string, combine names to fullname, and stringify email."""
        from src.app.features.application.dtos.user_dto import UserResponse
        from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        entity_id = EntityId.generate()
        entity = UserEntity(
            id=entity_id,
            email=Email("john.doe@example.com"),
            first_name="John",
            last_name="Doe",
            password_hash="$2b$12$dummyhash",
        )

        result = map_entity_to_dto_user(entity)

        assert isinstance(result, UserResponse)
        assert result.id == str(entity_id)
        assert result.fullname == "John Doe"
        assert result.email == "john.doe@example.com"

    @pytest.mark.unit
    def test_handles_special_characters_in_names(self) -> None:
        """Names with accents, hyphens, and apostrophes should pass through unchanged."""
        from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        entity = UserEntity(
            id=EntityId.generate(),
            email=Email("jose@example.com"),
            first_name="José",
            last_name="García-López",
            password_hash="$2b$12$dummyhash",
        )

        result = map_entity_to_dto_user(entity)

        assert result.fullname == "José García-López"
        assert result.email == "jose@example.com"

    @pytest.mark.unit
    def test_handles_unicode_names(self) -> None:
        """CJK and other Unicode characters in names should be preserved."""
        from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        entity = UserEntity(
            id=EntityId.generate(),
            email=Email("wei@example.com"),
            first_name="伟",
            last_name="王",
            password_hash="$2b$12$dummyhash",
        )

        result = map_entity_to_dto_user(entity)

        assert result.fullname == "伟 王"
        assert result.email == "wei@example.com"

    @pytest.mark.unit
    def test_id_is_string_representation_of_uuid(self) -> None:
        """The mapped id should be the string form of the EntityId."""
        from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        entity_id = EntityId.generate()
        entity = UserEntity(
            id=entity_id,
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="$2b$12$dummyhash",
        )

        result = map_entity_to_dto_user(entity)

        assert result.id == str(entity_id)
        assert result.id == str(entity_id.value)

    @pytest.mark.unit
    def test_email_is_stringified(self) -> None:
        """The mapped email should be a plain string, not an Email object."""
        from src.app.features.application.dtos.user_dto_mapper import map_entity_to_dto_user
        from src.app.features.domain.entities.user_entity import UserEntity
        from src.app.features.domain.value_objects.email import Email
        from src.shared.domain.value_objects.entity_id import EntityId

        entity = UserEntity(
            id=EntityId.generate(),
            email=Email("user@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="$2b$12$dummyhash",
        )

        result = map_entity_to_dto_user(entity)

        assert isinstance(result.email, str)
        assert result.email == "user@example.com"


class TestMapCreateRequestToEntity:
    """Tests for map_create_request_to_entity."""

    @pytest.mark.unit
    def test_creates_valid_user_entity_with_trimmed_fields(self) -> None:
        """Should create a UserEntity with leading/trailing whitespace removed from names."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity
        from src.app.features.domain.entities.user_entity import UserEntity

        payload = UserCreateRequest(
            first_name="  John  ",
            last_name="  Doe  ",
            email="john@example.com",
            password="ValidP@ss1",
        )
        password_hash = "$2b$12$generatedhashfortesting"

        entity = map_create_request_to_entity(payload, password_hash)

        assert isinstance(entity, UserEntity)
        assert entity.first_name == "John"
        assert entity.last_name == "Doe"

    @pytest.mark.unit
    def test_lowercases_and_strips_email(self) -> None:
        """Email should be lowercased and stripped of surrounding whitespace."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="  JOHN.DOE@Example.COM  ",
            password="ValidP@ss1",
        )

        entity = map_create_request_to_entity(payload, "$2b$12$hash")

        assert entity.email.value == "john.doe@example.com"

    @pytest.mark.unit
    def test_stores_password_hash_as_is(self) -> None:
        """The password_hash parameter should be stored verbatim on the entity."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="ValidP@ss1",
        )
        password_hash = "$2b$12$exactHashValueToPreserve"

        entity = map_create_request_to_entity(payload, password_hash)

        assert entity.password_hash == "$2b$12$exactHashValueToPreserve"

    @pytest.mark.unit
    def test_entity_id_is_generated_each_call(self) -> None:
        """Each call should produce a UserEntity with a new unique EntityId."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="ValidP@ss1",
        )

        entity_a = map_create_request_to_entity(payload, "hash_a")
        entity_b = map_create_request_to_entity(payload, "hash_b")

        assert entity_a.id != entity_b.id
        assert str(entity_a.id) != str(entity_b.id)

    @pytest.mark.unit
    def test_generated_id_is_valid_uuid(self) -> None:
        """The generated EntityId should have a valid UUIDv4 value."""
        from uuid import UUID
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="ValidP@ss1",
        )

        entity = map_create_request_to_entity(payload, "$2b$12$hash")

        assert isinstance(entity.id.value, UUID)
        assert entity.id.value.version == 4

    @pytest.mark.unit
    def test_email_field_is_email_value_object(self) -> None:
        """The entity's email should be an Email value object instance."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import map_create_request_to_entity
        from src.app.features.domain.value_objects.email import Email

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="ValidP@ss1",
        )

        entity = map_create_request_to_entity(payload, "$2b$12$hash")

        assert isinstance(entity.email, Email)


class TestRoundTrip:
    """Round-trip: UserCreateRequest -> UserEntity -> UserResponse."""

    @pytest.mark.unit
    def test_create_request_to_entity_to_response_preserves_data(self) -> None:
        """Mapping from request to entity to response should preserve all user data."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import (
            map_create_request_to_entity,
            map_entity_to_dto_user,
        )

        payload = UserCreateRequest(
            first_name="  Jane  ",
            last_name="  Smith  ",
            email="  JANE.SMITH@Example.COM  ",
            password="StrongP@ss1",
        )
        password_hash = "$2b$12$bcryptHashRoundTrip"

        entity = map_create_request_to_entity(payload, password_hash)
        response = map_entity_to_dto_user(entity)

        # Full name is assembled from trimmed fields
        assert response.fullname == "Jane Smith"
        # Email is lowercased and stripped
        assert response.email == "jane.smith@example.com"
        # ID is a non-empty string representation of a UUID
        assert len(response.id) > 0
        assert response.id == str(entity.id)
        # Password hash is NOT present in the response (it should never leak)
        assert not hasattr(response, "password_hash")

    @pytest.mark.unit
    def test_multiple_round_trips_produce_unique_ids(self) -> None:
        """Consecutive round-trips should yield different IDs."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import (
            map_create_request_to_entity,
            map_entity_to_dto_user,
        )

        payload = UserCreateRequest(
            first_name="Alice",
            last_name="Johnson",
            email="alice@example.com",
            password="ValidP@ss1",
        )

        response_a = map_entity_to_dto_user(
            map_create_request_to_entity(payload, "hash_a")
        )
        response_b = map_entity_to_dto_user(
            map_create_request_to_entity(payload, "hash_b")
        )

        assert response_a.id != response_b.id

    @pytest.mark.unit
    def test_email_with_maximum_whitespace_normalization(self) -> None:
        """Leading/trailing whitespace and mixed case in email are normalized."""
        from src.app.features.application.dtos.user_dto import UserCreateRequest
        from src.app.features.application.dtos.user_dto_mapper import (
            map_create_request_to_entity,
            map_entity_to_dto_user,
        )

        payload = UserCreateRequest(
            first_name="Test",
            last_name="User",
            email="  USER@EXAMPLE.COM  ",
            password="ValidP@ss1",
        )

        entity = map_create_request_to_entity(payload, "hash")
        response = map_entity_to_dto_user(entity)

        assert response.email == "user@example.com"
