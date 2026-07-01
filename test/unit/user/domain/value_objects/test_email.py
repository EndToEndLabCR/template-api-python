import pytest
from dataclasses import FrozenInstanceError
from src.app.features.domain.value_objects.email import Email


class TestEmail:
    """Unit tests for the Email value object."""

    # ------------------------------------------------------------------
    # Valid email addresses
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_valid_standard_email(self) -> None:
        """A standard email address should be accepted."""
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    @pytest.mark.unit
    def test_valid_email_with_dots(self) -> None:
        """Email with dots in local part should be accepted."""
        email = Email("first.last@example.com")
        assert email.value == "first.last@example.com"

    @pytest.mark.unit
    def test_valid_email_with_plus(self) -> None:
        """Email with plus addressing should be accepted."""
        email = Email("user+tag@example.com")
        assert email.value == "user+tag@example.com"

    @pytest.mark.unit
    def test_valid_email_with_subdomain(self) -> None:
        """Email with subdomains should be accepted."""
        email = Email("user@sub.example.com")
        assert email.value == "user@sub.example.com"

    @pytest.mark.unit
    def test_valid_email_with_underscore(self) -> None:
        """Email with underscore in local part should be accepted."""
        email = Email("user_name@example.com")
        assert email.value == "user_name@example.com"

    @pytest.mark.unit
    def test_valid_email_with_digits(self) -> None:
        """Email with digits should be accepted."""
        email = Email("user123@example.com")
        assert email.value == "user123@example.com"

    @pytest.mark.unit
    def test_valid_email_with_percent_plus(self) -> None:
        """Email with percent and other special chars should be accepted."""
        email = Email("user%name+test@example.com")
        assert email.value == "user%name+test@example.com"

    # ------------------------------------------------------------------
    # Invalid email addresses
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_invalid_email_no_at_sign(self) -> None:
        """Email without @ should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("userexample.com")

    @pytest.mark.unit
    def test_invalid_email_no_domain(self) -> None:
        """Email without domain part should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@")

    @pytest.mark.unit
    def test_invalid_email_empty_string(self) -> None:
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("")

    @pytest.mark.unit
    def test_invalid_email_spaces(self) -> None:
        """Email with spaces should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user @example.com")

    @pytest.mark.unit
    def test_invalid_email_missing_tld(self) -> None:
        """Email without TLD should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@example")

    @pytest.mark.unit
    def test_invalid_email_double_at(self) -> None:
        """Email with two @ symbols should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@domain@example.com")

    @pytest.mark.unit
    def test_invalid_email_only_spaces(self) -> None:
        """Email containing only spaces should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("   ")

    @pytest.mark.unit
    def test_invalid_email_newline(self) -> None:
        """Email with newline character should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user\n@example.com")

    # ------------------------------------------------------------------
    # String representation
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_str_representation(self) -> None:
        """__str__ should return the raw email value."""
        email = Email("alice@example.com")
        assert str(email) == "alice@example.com"

    @pytest.mark.unit
    def test_repr_contains_value(self) -> None:
        """__repr__ should include the email value."""
        email = Email("bob@example.com")
        assert "bob@example.com" in repr(email)

    # ------------------------------------------------------------------
    # Frozen / immutability
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_immutable_value(self) -> None:
        """Email dataclass is frozen — assigning to .value should raise."""
        email = Email("charlie@example.com")
        with pytest.raises(FrozenInstanceError):
            email.value = "hacker@example.com"  # type: ignore[misc]

    @pytest.mark.unit
    def test_equality_based_on_value(self) -> None:
        """Two Email instances with the same value should be equal."""
        email_a = Email("same@example.com")
        email_b = Email("same@example.com")
        assert email_a == email_b

    @pytest.mark.unit
    def test_inequality_different_values(self) -> None:
        """Two Email instances with different values should not be equal."""
        email_a = Email("one@example.com")
        email_b = Email("two@example.com")
        assert email_a != email_b

    @pytest.mark.unit
    def test_hashable(self) -> None:
        """Frozen dataclass should be usable as a dict key."""
        email = Email("key@example.com")
        lookup: dict[Email, str] = {email: "found"}
        assert lookup[Email("key@example.com")] == "found"
