import pytest
from uuid import UUID, uuid4
from dataclasses import FrozenInstanceError
from src.shared.domain.value_objects.entity_id import EntityId


class TestEntityId:
    """Unit tests for the EntityId value object."""

    # ------------------------------------------------------------------
    # generate()
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_generate_returns_entity_id(self) -> None:
        """generate() should return an EntityId instance."""
        entity_id = EntityId.generate()
        assert isinstance(entity_id, EntityId)

    @pytest.mark.unit
    def test_generate_value_is_uuid(self) -> None:
        """The .value of a generated EntityId should be a UUID."""
        entity_id = EntityId.generate()
        assert isinstance(entity_id.value, UUID)

    @pytest.mark.unit
    def test_generate_value_is_valid_uuid(self) -> None:
        """The .value should be a valid UUID (version 4)."""
        entity_id = EntityId.generate()
        # UUIDv4 has version field = 4 (byte 6, high nibble)
        assert entity_id.value.version == 4

    @pytest.mark.unit
    def test_generate_produces_unique_ids(self) -> None:
        """Two generated EntityIds should be different."""
        id_a = EntityId.generate()
        id_b = EntityId.generate()
        assert id_a != id_b
        assert id_a.value != id_b.value

    # ------------------------------------------------------------------
    # from_string()
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_from_string_valid_uuid(self) -> None:
        """from_string with a valid UUID string should return an EntityId."""
        raw = str(uuid4())
        entity_id = EntityId.from_string(raw)
        assert isinstance(entity_id, EntityId)
        assert str(entity_id.value) == raw

    @pytest.mark.unit
    def test_from_string_with_hyphens(self) -> None:
        """from_string should accept the standard 8-4-4-4-12 format."""
        valid_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        entity_id = EntityId.from_string(valid_uuid)
        assert str(entity_id.value) == valid_uuid

    @pytest.mark.unit
    def test_from_string_without_hyphens(self) -> None:
        """from_string should accept a 32-hex-digit UUID string without hyphens."""
        raw = uuid4().hex  # 32 hex chars, no hyphens
        entity_id = EntityId.from_string(raw)
        # UUID class normalizes to hyphenated format
        assert entity_id.value.hex == raw

    @pytest.mark.unit
    def test_from_string_uppercase(self) -> None:
        """from_string should accept uppercase hex characters."""
        raw = str(uuid4()).upper()
        entity_id = EntityId.from_string(raw)
        # UUID class normalizes to lowercase
        assert str(entity_id.value) == raw.lower()

    @pytest.mark.unit
    def test_from_string_round_trip(self) -> None:
        """generate() then from_string(str(...)) should yield an equal EntityId."""
        original = EntityId.generate()
        reconstructed = EntityId.from_string(str(original))
        assert original == reconstructed

    # ------------------------------------------------------------------
    # from_string() — invalid inputs
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_from_string_invalid_format_raises(self) -> None:
        """from_string with a non-UUID string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            EntityId.from_string("not-a-uuid")

    @pytest.mark.unit
    def test_from_string_empty_string_raises(self) -> None:
        """from_string with an empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            EntityId.from_string("")

    @pytest.mark.unit
    def test_from_string_too_short_raises(self) -> None:
        """from_string with a truncated hex string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            EntityId.from_string("abc123")

    @pytest.mark.unit
    def test_from_string_with_spaces_raises(self) -> None:
        """from_string with spaces around the UUID should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            EntityId.from_string("  a1b2c3d4-e5f6-7890-abcd-ef1234567890  ")

    @pytest.mark.unit
    def test_from_string_hex_with_garbage(self) -> None:
        """from_string with valid hex plus extra characters should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            EntityId.from_string(uuid4().hex + "zzz")

    # ------------------------------------------------------------------
    # Direct construction EntityId(value)
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_direct_construction_with_uuid(self) -> None:
        """EntityId can be constructed directly with a UUID instance."""
        uid = uuid4()
        entity_id = EntityId(uid)
        assert entity_id.value == uid

    @pytest.mark.unit
    def test_constructor_rejects_non_uuid(self) -> None:
        """EntityId(value) with a non-UUID should raise ValueError."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            EntityId("not-a-uuid")  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_constructor_rejects_none(self) -> None:
        """EntityId(value) with None should raise ValueError."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            EntityId(None)  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_constructor_rejects_int(self) -> None:
        """EntityId(value) with an integer should raise ValueError."""
        with pytest.raises(ValueError, match="must be a valid UUID"):
            EntityId(12345)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_str_returns_uuid_string(self) -> None:
        """__str__ should return the UUID as a string in standard form."""
        raw = uuid4()
        entity_id = EntityId(raw)
        assert str(entity_id) == str(raw)

    @pytest.mark.unit
    def test_repr_contains_uuid(self) -> None:
        """__repr__ should include the UUID value."""
        raw = uuid4()
        entity_id = EntityId(raw)
        assert str(raw) in repr(entity_id)

    # ------------------------------------------------------------------
    # Frozen / immutability
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_immutable_value(self) -> None:
        """EntityId dataclass is frozen — assigning to .value should raise."""
        entity_id = EntityId.generate()
        new_uuid = uuid4()
        with pytest.raises(FrozenInstanceError):
            entity_id.value = new_uuid  # type: ignore[misc]

    @pytest.mark.unit
    def test_equality_based_on_value(self) -> None:
        """Two EntityId instances with the same UUID should be equal."""
        uid = uuid4()
        id_a = EntityId(uid)
        id_b = EntityId(uid)
        assert id_a == id_b

    @pytest.mark.unit
    def test_inequality_different_values(self) -> None:
        """Two EntityId instances with different UUIDs should not be equal."""
        id_a = EntityId.generate()
        id_b = EntityId.generate()
        assert id_a != id_b

    @pytest.mark.unit
    def test_hashable(self) -> None:
        """Frozen dataclass should be usable as a dict key."""
        uid = uuid4()
        entity_id = EntityId(uid)
        lookup: dict[EntityId, str] = {entity_id: "found"}
        assert lookup[EntityId(uid)] == "found"
