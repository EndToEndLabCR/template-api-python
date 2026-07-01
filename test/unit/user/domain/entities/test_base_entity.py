import pytest
from datetime import datetime

from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class TestBaseEntity:
    """Unit tests for the BaseEntity domain class."""

    # ------------------------------------------------------------------
    # Default constructor
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_default_constructor_generates_id_and_timestamps(self) -> None:
        """Default constructor should generate id, created_at, and updated_at."""
        entity = BaseEntity()

        assert isinstance(entity.id, EntityId)
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    @pytest.mark.unit
    def test_two_instances_have_different_ids_by_default(self) -> None:
        """Two default-constructed instances should have different IDs."""
        entity_a = BaseEntity()
        entity_b = BaseEntity()
        assert entity_a.id != entity_b.id

    # ------------------------------------------------------------------
    # Custom ID
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_constructor_accepts_custom_id(self) -> None:
        """Constructor should accept and store a custom EntityId."""
        custom_id = EntityId.generate()
        entity = BaseEntity(id=custom_id)
        assert entity.id == custom_id

    # ------------------------------------------------------------------
    # Custom timestamps
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_constructor_accepts_custom_created_at(self) -> None:
        """Constructor should accept a custom created_at datetime."""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        entity = BaseEntity(created_at=created_at)
        assert entity.created_at == created_at

    @pytest.mark.unit
    def test_constructor_accepts_custom_updated_at(self) -> None:
        """Constructor should accept a custom updated_at datetime."""
        updated_at = datetime(2024, 6, 15, 8, 30, 0)
        entity = BaseEntity(updated_at=updated_at)
        assert entity.updated_at == updated_at

    @pytest.mark.unit
    def test_constructor_accepts_both_custom_timestamps(self) -> None:
        """Constructor should accept custom created_at and updated_at together."""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        updated_at = datetime(2024, 6, 15, 8, 30, 0)
        entity = BaseEntity(created_at=created_at, updated_at=updated_at)
        assert entity.created_at == created_at
        assert entity.updated_at == updated_at

    # ------------------------------------------------------------------
    # mark_as_updated()
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_mark_as_updated_updates_updated_at(self) -> None:
        """mark_as_updated() should set updated_at to a newer or equal datetime."""
        entity = BaseEntity()
        original_updated_at = entity.updated_at
        entity.mark_as_updated()
        assert entity.updated_at >= original_updated_at

    @pytest.mark.unit
    def test_mark_as_updated_preserves_created_at(self) -> None:
        """mark_as_updated() should not modify created_at."""
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        entity = BaseEntity(created_at=created_at)
        entity.mark_as_updated()
        assert entity.created_at == created_at

    @pytest.mark.unit
    def test_mark_as_updated_preserves_id(self) -> None:
        """mark_as_updated() should not modify id."""
        entity = BaseEntity()
        original_id = entity.id
        entity.mark_as_updated()
        assert entity.id == original_id

    # ------------------------------------------------------------------
    # Equality / identity
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_equality_with_same_object(self) -> None:
        """Same BaseEntity instance should be equal to itself (identity)."""
        entity = BaseEntity()
        assert entity == entity

    @pytest.mark.unit
    def test_inequality_of_different_instances(self) -> None:
        """Different BaseEntity instances should not be equal."""
        entity_a = BaseEntity()
        entity_b = BaseEntity()
        assert entity_a != entity_b

    # ------------------------------------------------------------------
    # Type checks
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_created_at_and_updated_at_are_datetime_objects(self) -> None:
        """created_at and updated_at attributes should be datetime instances."""
        entity = BaseEntity()
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    @pytest.mark.unit
    def test_id_is_entity_id_object(self) -> None:
        """id attribute should be an EntityId instance."""
        entity = BaseEntity()
        assert isinstance(entity.id, EntityId)

    # ------------------------------------------------------------------
    # Timestamp independence (each call generates fresh timestamps)
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_created_at_and_updated_at_are_set_independently(self) -> None:
        """created_at and updated_at should be independently settable."""
        created_at = datetime(2023, 12, 1, 0, 0, 0)
        updated_at = datetime(2024, 6, 1, 12, 0, 0)
        entity = BaseEntity(created_at=created_at, updated_at=updated_at)
        assert entity.created_at != entity.updated_at
