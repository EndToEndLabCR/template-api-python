import pytest
from dataclasses import FrozenInstanceError
import bcrypt
from src.app.features.domain.value_objects.password import Password


class TestPassword:
    """Unit tests for the Password value object."""

    # ------------------------------------------------------------------
    # Valid passwords
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_valid_password_meets_all_criteria(self) -> None:
        """A password meeting all complexity rules should be accepted."""
        pwd = Password("ValidP@ss1")
        assert pwd.value == "ValidP@ss1"

    @pytest.mark.unit
    def test_valid_password_minimal_length(self) -> None:
        """A password exactly 8 characters meeting all rules should be accepted."""
        pwd = Password("Abcd#123")
        assert pwd.value == "Abcd#123"

    @pytest.mark.unit
    def test_valid_password_long_and_complex(self) -> None:
        """A long complex password should be accepted."""
        pwd = Password("C0mpl3x!Pa$$word#2024")
        assert pwd.value == "C0mpl3x!Pa$$word#2024"

    @pytest.mark.unit
    def test_valid_password_with_multiple_special_chars(self) -> None:
        """A password with many special characters should be accepted."""
        pwd = Password("P@ssw0rd!#$%")
        assert pwd.value == "P@ssw0rd!#$%"

    # ------------------------------------------------------------------
    # Invalid passwords — too short
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_invalid_password_too_short(self) -> None:
        """A password shorter than 8 characters should raise ValueError."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            Password("Ab1!def")

    @pytest.mark.unit
    def test_invalid_password_empty(self) -> None:
        """An empty password should raise ValueError for length."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            Password("")

    # ------------------------------------------------------------------
    # Invalid passwords — missing character requirements
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_invalid_password_no_uppercase(self) -> None:
        """A password missing an uppercase letter should raise ValueError."""
        with pytest.raises(ValueError, match="at least one uppercase"):
            Password("lowercase1!")

    @pytest.mark.unit
    def test_invalid_password_no_lowercase(self) -> None:
        """A password missing a lowercase letter should raise ValueError."""
        with pytest.raises(ValueError, match="at least one lowercase"):
            Password("UPPERCASE1!")

    @pytest.mark.unit
    def test_invalid_password_no_digit(self) -> None:
        """A password missing a digit should raise ValueError."""
        with pytest.raises(ValueError, match="at least one digit"):
            Password("NoDigitsA!")

    @pytest.mark.unit
    def test_invalid_password_no_special_char(self) -> None:
        """A password missing a special character should raise ValueError."""
        with pytest.raises(ValueError, match="at least one special character"):
            Password("NoSpecial1A")

    @pytest.mark.unit
    def test_invalid_password_only_uppercase(self) -> None:
        """A password with only uppercase letters should raise ValueError."""
        with pytest.raises(ValueError):
            Password("ALLUPPERCASE1!")

    @pytest.mark.unit
    def test_invalid_password_only_lowercase(self) -> None:
        """A password with only lowercase letters should raise ValueError."""
        with pytest.raises(ValueError):
            Password("alllowercase1!")

    # ------------------------------------------------------------------
    # hash() method
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_hash_returns_string(self) -> None:
        """hash() should return a string."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert isinstance(hashed, str)

    @pytest.mark.unit
    def test_hash_starts_with_bcrypt_prefix(self) -> None:
        """The bcrypt hash should start with $2b$."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert hashed.startswith("$2b$")

    @pytest.mark.unit
    def test_hash_is_different_each_time(self) -> None:
        """Each call to hash() should produce a unique salt, hence a different hash."""
        pwd = Password("ValidP@ss1")
        hash1 = pwd.hash()
        hash2 = pwd.hash()
        assert hash1 != hash2

    @pytest.mark.unit
    def test_hash_valid_bcrypt_format(self) -> None:
        """The generated hash should be a valid bcrypt hash of the password."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert bcrypt.checkpw(b"ValidP@ss1", hashed.encode("utf-8"))

    @pytest.mark.unit
    def test_hash_length(self) -> None:
        """Bcrypt hash should be 60 characters long."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert len(hashed) == 60

    # ------------------------------------------------------------------
    # verify() static method
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_verify_correct_password(self) -> None:
        """verify() should return True for the correct password."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert Password.verify("ValidP@ss1", hashed) is True

    @pytest.mark.unit
    def test_verify_incorrect_password(self) -> None:
        """verify() should return False for an incorrect password."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert Password.verify("WrongP@ss1", hashed) is False

    @pytest.mark.unit
    def test_verify_wrong_case_password(self) -> None:
        """verify() should return False when the case differs."""
        pwd = Password("ValidP@ss1")
        hashed = pwd.hash()
        assert Password.verify("validp@ss1", hashed) is False

    @pytest.mark.unit
    def test_verify_with_externally_generated_hash(self) -> None:
        """verify() should work with a hash generated outside the class."""
        raw = b"ExternalP@ss1"
        external_hash = bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")
        assert Password.verify("ExternalP@ss1", external_hash) is True
        assert Password.verify("WrongP@ss1", external_hash) is False

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_str_returns_plaintext_value(self) -> None:
        """__str__ should return the plaintext password value."""
        pwd = Password("ValidP@ss1")
        assert str(pwd) == "ValidP@ss1"

    @pytest.mark.unit
    def test_repr_contains_value(self) -> None:
        """__repr__ should include the password value."""
        pwd = Password("TestP@ss1")
        assert "TestP@ss1" in repr(pwd)

    # ------------------------------------------------------------------
    # Frozen / immutability
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_immutable_value(self) -> None:
        """Password dataclass is frozen — assigning to .value should raise."""
        pwd = Password("ValidP@ss1")
        with pytest.raises(FrozenInstanceError):
            pwd.value = "hacked1!"  # type: ignore[misc]

    @pytest.mark.unit
    def test_equality_based_on_value(self) -> None:
        """Two Password instances with the same value should be equal."""
        pwd_a = Password("SameP@ss1")
        pwd_b = Password("SameP@ss1")
        assert pwd_a == pwd_b

    @pytest.mark.unit
    def test_inequality_different_values(self) -> None:
        """Two Password instances with different values should not be equal."""
        pwd_a = Password("AlphaP@ss1")
        pwd_b = Password("BetaP@ss1")
        assert pwd_a != pwd_b

    @pytest.mark.unit
    def test_hashable(self) -> None:
        """Frozen dataclass should be usable as a dict key."""
        pwd = Password("DictKey@1")
        lookup: dict[Password, str] = {pwd: "found"}
        assert lookup[Password("DictKey@1")] == "found"
