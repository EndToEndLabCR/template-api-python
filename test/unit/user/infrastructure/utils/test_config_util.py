"""Unit tests for config_util — get_config_value helper."""

import pytest


class TestGetConfigValue:
    """Tests for get_config_value."""

    @pytest.mark.unit
    def test_returns_value_for_existing_key(self) -> None:
        """Should return the value for a key that exists in the dict."""
        from src.shared.utils.config_util import get_config_value

        config = {"host": "localhost", "port": 8080}
        result = get_config_value(config, "host")
        assert result == "localhost"

    @pytest.mark.unit
    def test_returns_default_for_missing_key(self) -> None:
        """Should return the default when key is missing."""
        from src.shared.utils.config_util import get_config_value

        config = {"host": "localhost"}
        result = get_config_value(config, "port", default=3000)
        assert result == 3000

    @pytest.mark.unit
    def test_raises_value_error_for_missing_key_no_default(self) -> None:
        """Should raise ValueError when key is missing and no default given."""
        from src.shared.utils.config_util import get_config_value

        config = {"host": "localhost"}
        with pytest.raises(ValueError, match="Missing required configuration key: 'port'"):
            get_config_value(config, "port")

    @pytest.mark.unit
    def test_returns_none_default_explicitly(self) -> None:
        """Should return None when default=None and key is present with None value."""
        from src.shared.utils.config_util import get_config_value

        config = {"host": None}
        with pytest.raises(ValueError, match="Missing required configuration key: 'host'"):
            get_config_value(config, "host")

    # ------------------------------------------------------------------
    # expected_type casting
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_casts_to_int(self) -> None:
        """Should cast string value to int when expected_type=int."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": "8080"}
        result = get_config_value(config, "port", expected_type=int)
        assert result == 8080
        assert isinstance(result, int)

    @pytest.mark.unit
    def test_casts_to_bool(self) -> None:
        """Should cast value to bool when expected_type=bool."""
        from src.shared.utils.config_util import get_config_value

        config = {"debug": "true"}
        result = get_config_value(config, "debug", expected_type=bool)
        assert result is True

    @pytest.mark.unit
    def test_casts_to_str(self) -> None:
        """Should cast numeric value to str when expected_type=str."""
        from src.shared.utils.config_util import get_config_value

        config = {"name": 42}
        result = get_config_value(config, "name", expected_type=str)
        assert result == "42"
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_raises_type_error_when_cast_fails_int(self) -> None:
        """Should raise TypeError when value cannot be cast to int."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": "not-a-number"}
        with pytest.raises(TypeError, match="Configuration key 'port' must be of type int"):
            get_config_value(config, "port", expected_type=int)

    @pytest.mark.unit
    def test_raises_type_error_when_cast_fails_float(self) -> None:
        """Should raise TypeError when value cannot be cast to float."""
        from src.shared.utils.config_util import get_config_value

        config = {"ratio": "invalid-float"}
        with pytest.raises(TypeError, match="Configuration key 'ratio' must be of type float"):
            get_config_value(config, "ratio", expected_type=float)

    @pytest.mark.unit
    def test_passes_through_already_correct_type(self) -> None:
        """Should pass through value unchanged if already the expected type."""
        from src.shared.utils.config_util import get_config_value

        config = {"workers": 4}
        result = get_config_value(config, "workers", expected_type=int)
        assert result == 4
        assert isinstance(result, int)

    # ------------------------------------------------------------------
    # Port validation
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_validates_port_range_valid(self) -> None:
        """Should accept valid port numbers (1-65535)."""
        from src.shared.utils.config_util import get_config_value

        for valid_port in [1, 80, 443, 3000, 65535]:
            config = {"port": valid_port}
            result = get_config_value(config, "port")
            assert result == valid_port

    @pytest.mark.unit
    def test_raises_value_error_for_port_zero(self) -> None:
        """Port 0 is invalid and should raise ValueError."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": 0}
        with pytest.raises(
            ValueError,
            match="Configuration key 'port' must be a valid port number \\(1-65535\\), got 0",
        ):
            get_config_value(config, "port")

    @pytest.mark.unit
    def test_raises_value_error_for_negative_port(self) -> None:
        """Negative port numbers are invalid and should raise ValueError."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": -1}
        with pytest.raises(
            ValueError,
            match="Configuration key 'port' must be a valid port number \\(1-65535\\), got -1",
        ):
            get_config_value(config, "port")

    @pytest.mark.unit
    def test_raises_value_error_for_port_too_high(self) -> None:
        """Port > 65535 is invalid and should raise ValueError."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": 70000}
        with pytest.raises(
            ValueError,
            match="Configuration key 'port' must be a valid port number \\(1-65535\\), got 70000",
        ):
            get_config_value(config, "port")

    @pytest.mark.unit
    def test_raises_value_error_for_port_after_cast(self) -> None:
        """Port validation should run after type casting."""
        from src.shared.utils.config_util import get_config_value

        config = {"port": "0"}
        with pytest.raises(
            ValueError,
            match="Configuration key 'port' must be a valid port number \\(1-65535\\), got 0",
        ):
            get_config_value(config, "port", expected_type=int)

    # ------------------------------------------------------------------
    # Non-port keys with edge values
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_non_port_key_accepts_zero(self) -> None:
        """Non-port keys should accept 0 as a valid value."""
        from src.shared.utils.config_util import get_config_value

        config = {"timeout": 0}
        result = get_config_value(config, "timeout")
        assert result == 0

    @pytest.mark.unit
    def test_non_port_key_accepts_negative(self) -> None:
        """Non-port keys should accept negative values."""
        from src.shared.utils.config_util import get_config_value

        config = {"offset": -1}
        result = get_config_value(config, "offset")
        assert result == -1

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_empty_config_dict(self) -> None:
        """Empty config dict should raise ValueError for any key."""
        from src.shared.utils.config_util import get_config_value

        with pytest.raises(ValueError, match="Missing required configuration key: 'key'"):
            get_config_value({}, "key")

    @pytest.mark.unit
    def test_boolean_false_is_not_none(self) -> None:
        """False should not be treated as None/missing."""
        from src.shared.utils.config_util import get_config_value

        config = {"enabled": False}
        result = get_config_value(config, "enabled")
        assert result is False

    @pytest.mark.unit
    def test_empty_string_is_not_none(self) -> None:
        """Empty string should not be treated as None/missing."""
        from src.shared.utils.config_util import get_config_value

        config = {"name": ""}
        result = get_config_value(config, "name")
        assert result == ""
