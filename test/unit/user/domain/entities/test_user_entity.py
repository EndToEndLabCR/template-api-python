import pytest
from datetime import datetime, timedelta

from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.value_objects.email import Email
from src.shared.domain.value_objects.entity_id import EntityId


class TestUserEntity:
    """Unit tests for the UserEntity domain class."""

    # ------------------------------------------------------------------
    # Constructor — all fields
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_constructor_sets_all_fields(self, sample_user_entity) -> None:
        """Constructor should set all provided fields correctly."""
        assert sample_user_entity.first_name == "Test"
        assert sample_user_entity.last_name == "User"
        assert sample_user_entity.password_hash == "$2b$12$LJ3m4ys3LkDummyHashForTestingPurposes"
        assert sample_user_entity.email == Email("test@example.com")

    @pytest.mark.unit
    def test_constructor_with_all_optional_fields(self) -> None:
        """Constructor should accept and store optional password-reset fields."""
        expires_at = datetime(2025, 12, 31, 23, 59, 59)
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("reset@example.com"),
            first_name="Reset",
            last_name="User",
            password_hash="hash123",
            password_reset_token_hash="token_abc",
            password_reset_expires_at=expires_at,
        )
        assert user.password_reset_token_hash == "token_abc"
        assert user.password_reset_expires_at == expires_at

    # ------------------------------------------------------------------
    # Inheritance from BaseEntity
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_inherits_id_from_base_entity(self) -> None:
        """UserEntity should inherit id from BaseEntity as an EntityId."""
        user_id = EntityId.generate()
        user = UserEntity(
            id=user_id,
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
        )
        assert user.id == user_id
        assert isinstance(user.id, EntityId)

    @pytest.mark.unit
    def test_inherits_created_at_from_base_entity(self) -> None:
        """UserEntity should inherit created_at from BaseEntity."""
        created_at = datetime(2024, 3, 15, 10, 0, 0)
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
            created_at=created_at,
        )
        assert user.created_at == created_at
        assert isinstance(user.created_at, datetime)

    @pytest.mark.unit
    def test_inherits_updated_at_from_base_entity(self) -> None:
        """UserEntity should inherit updated_at from BaseEntity."""
        updated_at = datetime(2024, 6, 1, 14, 30, 0)
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
            updated_at=updated_at,
        )
        assert user.updated_at == updated_at
        assert isinstance(user.updated_at, datetime)

    # ------------------------------------------------------------------
    # Field mutability
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_fields_are_mutable(self) -> None:
        """All UserEntity fields should be assignable (mutable)."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("original@example.com"),
            first_name="Original",
            last_name="User",
            password_hash="hash1",
        )
        new_id = EntityId.generate()
        new_email = Email("updated@example.com")
        new_expires = datetime(2026, 1, 1, 0, 0, 0)

        user.id = new_id
        user.email = new_email
        user.first_name = "Updated"
        user.last_name = "Name"
        user.password_hash = "hash2"
        user.password_reset_token_hash = "new_token"
        user.password_reset_expires_at = new_expires

        assert user.id == new_id
        assert user.email == new_email
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.password_hash == "hash2"
        assert user.password_reset_token_hash == "new_token"
        assert user.password_reset_expires_at == new_expires

    # ------------------------------------------------------------------
    # Password-reset fields — optional / None by default
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_password_fields_are_optional_by_default(self) -> None:
        """password_reset_token_hash and password_reset_expires_at should default to None."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
        )
        assert user.password_reset_token_hash is None
        assert user.password_reset_expires_at is None

    @pytest.mark.unit
    def test_password_reset_token_hash_is_optional(self) -> None:
        """password_reset_token_hash should be settable and default to None."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
        )
        assert user.password_reset_token_hash is None

        user.password_reset_token_hash = "some_token"
        assert user.password_reset_token_hash == "some_token"

    @pytest.mark.unit
    def test_password_reset_expires_at_is_optional_and_nullable(self) -> None:
        """password_reset_expires_at should be settable to None and a datetime."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
        )
        assert user.password_reset_expires_at is None

        # Set to a datetime
        expires = datetime(2025, 12, 31, 23, 59, 59)
        user.password_reset_expires_at = expires
        assert user.password_reset_expires_at == expires

        # Reset to None
        user.password_reset_expires_at = None
        assert user.password_reset_expires_at is None

    # ------------------------------------------------------------------
    # mark_as_updated() — inherited from BaseEntity
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_mark_as_updated_inherited_and_works(self) -> None:
        """mark_as_updated() inherited from BaseEntity should update updated_at."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("test@example.com"),
            first_name="Test",
            last_name="User",
            password_hash="hash",
        )
        original_updated_at = user.updated_at
        user.mark_as_updated()
        assert user.updated_at >= original_updated_at

    @pytest.mark.unit
    def test_mark_as_updated_preserves_user_fields(self) -> None:
        """mark_as_updated() should not modify user-specific fields."""
        user = UserEntity(
            id=EntityId.generate(),
            email=Email("preserve@example.com"),
            first_name="Preserve",
            last_name="Test",
            password_hash="hash",
        )
        email_before = user.email
        first_before = user.first_name
        last_before = user.last_name
        hash_before = user.password_hash

        user.mark_as_updated()

        assert user.email == email_before
        assert user.first_name == first_before
        assert user.last_name == last_before
        assert user.password_hash == hash_before

    # ------------------------------------------------------------------
    # Value object types
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_email_is_email_value_object(self, sample_user_entity) -> None:
        """email field should be an Email value object instance."""
        assert isinstance(sample_user_entity.email, Email)

    @pytest.mark.unit
    def test_id_is_entity_id_value_object(self, sample_user_entity) -> None:
        """id field should be an EntityId value object instance."""
        assert isinstance(sample_user_entity.id, EntityId)

    # ------------------------------------------------------------------
    # Core field access
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_access_to_core_fields(self, sample_user_entity) -> None:
        """Core fields should be directly accessible on the entity."""
        assert sample_user_entity.email == Email("test@example.com")
        assert sample_user_entity.first_name == "Test"
        assert sample_user_entity.last_name == "User"
        assert sample_user_entity.password_hash == (
            "$2b$12$LJ3m4ys3LkDummyHashForTestingPurposes"
        )
