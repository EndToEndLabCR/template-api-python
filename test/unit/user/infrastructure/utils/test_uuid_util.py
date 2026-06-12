"""Unit tests for uuid_util — UUID string conversion utilities."""

from uuid import UUID

import pytest


class TestConvertUuidToStr:
    """Tests for convert_uuid_to_str."""

    @pytest.mark.unit
    def test_with_uuid_object_returns_string(self) -> None:
        """Should convert a UUID object to its string representation."""
        from src.shared.utils.uuid_util import convert_uuid_to_str

        uuid_obj = UUID("123e4567-e89b-12d3-a456-426614174000")
        result = convert_uuid_to_str(uuid_obj)
        assert result == "123e4567-e89b-12d3-a456-426614174000"
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_with_none_returns_none(self) -> None:
        """Should return None when given None."""
        from src.shared.utils.uuid_util import convert_uuid_to_str

        result = convert_uuid_to_str(None)
        assert result is None

    @pytest.mark.unit
    def test_with_random_uuid_returns_string(self) -> None:
        """Should convert any valid UUID object to a string."""
        from src.shared.utils.uuid_util import convert_uuid_to_str

        uuid_obj = UUID("00000000-0000-0000-0000-000000000000")
        result = convert_uuid_to_str(uuid_obj)
        assert result == "00000000-0000-0000-0000-000000000000"


class TestConvertStrToUuid:
    """Tests for convert_str_to_uuid."""

    @pytest.mark.unit
    def test_with_valid_string_returns_uuid(self) -> None:
        """Should convert a valid UUID string to a UUID object."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        result = convert_str_to_uuid("123e4567-e89b-12d3-a456-426614174000")
        assert isinstance(result, UUID)
        assert str(result) == "123e4567-e89b-12d3-a456-426614174000"

    @pytest.mark.unit
    def test_with_none_returns_none(self) -> None:
        """Should return None when given None."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        result = convert_str_to_uuid(None)
        assert result is None

    @pytest.mark.unit
    def test_with_empty_string_returns_none(self) -> None:
        """Empty string is falsy and should return None (function short-circuits)."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        result = convert_str_to_uuid("")
        assert result is None

    @pytest.mark.unit
    def test_with_invalid_format_raises_value_error(self) -> None:
        """Invalid UUID string format should raise ValueError."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        with pytest.raises(ValueError, match="Invalid UUID format: not-a-uuid"):
            convert_str_to_uuid("not-a-uuid")

    @pytest.mark.unit
    def test_with_partial_uuid_raises_value_error(self) -> None:
        """A partial UUID string should raise ValueError."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        with pytest.raises(ValueError, match="Invalid UUID format: 123e4567"):
            convert_str_to_uuid("123e4567")

    @pytest.mark.unit
    def test_with_hex_string_returns_uuid(self) -> None:
        """Should accept UUID hex string without dashes."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        result = convert_str_to_uuid("123e4567e89b12d3a456426614174000")
        assert isinstance(result, UUID)
        assert str(result) == "123e4567-e89b-12d3-a456-426614174000"

    @pytest.mark.unit
    def test_with_uppercase_hex_returns_uuid(self) -> None:
        """Should accept uppercase UUID hex string."""
        from src.shared.utils.uuid_util import convert_str_to_uuid

        result = convert_str_to_uuid("123E4567-E89B-12D3-A456-426614174000")
        assert isinstance(result, UUID)
        assert str(result) == "123e4567-e89b-12d3-a456-426614174000"


class TestRoundTrip:
    """Round-trip conversion tests."""

    @pytest.mark.unit
    def test_uuid_to_str_to_uuid(self) -> None:
        """UUID -> str -> UUID should return the original UUID."""
        from src.shared.utils.uuid_util import convert_uuid_to_str, convert_str_to_uuid

        original = UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        str_repr = convert_uuid_to_str(original)
        result = convert_str_to_uuid(str_repr)
        assert result == original
        assert isinstance(result, UUID)

    @pytest.mark.unit
    def test_str_to_uuid_to_str(self) -> None:
        """str -> UUID -> str should match the original string (lowercased)."""
        from src.shared.utils.uuid_util import convert_uuid_to_str, convert_str_to_uuid

        original_str = "cafebabe-dead-beef-1234-567890abcdef"
        uuid_obj = convert_str_to_uuid(original_str)
        result_str = convert_uuid_to_str(uuid_obj)
        assert result_str == original_str
        assert isinstance(result_str, str)

    @pytest.mark.unit
    def test_none_round_trip(self) -> None:
        """None -> convert_str_to_uuid -> None -> convert_uuid_to_str -> None."""
        from src.shared.utils.uuid_util import convert_uuid_to_str, convert_str_to_uuid

        assert convert_str_to_uuid(None) is None
        assert convert_uuid_to_str(None) is None
