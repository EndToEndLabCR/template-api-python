"""Unit tests for date_util — get_current_datetime and get_current_date."""

from datetime import datetime

import pytest


class TestGetCurrentDatetime:
    """Tests for get_current_datetime."""

    @pytest.mark.unit
    def test_returns_datetime_object(self) -> None:
        """Should return a datetime instance."""
        from src.shared.utils.date_util import get_current_datetime

        result = get_current_datetime()
        assert isinstance(result, datetime)

    @pytest.mark.unit
    def test_consecutive_calls_return_close_values(self) -> None:
        """Two calls within the same test should be within 1 second of each other."""
        from src.shared.utils.date_util import get_current_datetime

        dt1 = get_current_datetime()
        dt2 = get_current_datetime()
        diff = abs((dt2 - dt1).total_seconds())
        assert diff < 1.0, f"Difference was {diff}s, expected < 1s"


class TestGetCurrentDate:
    """Tests for get_current_date."""

    @pytest.mark.unit
    def test_returns_string(self) -> None:
        """Should return a string."""
        from src.shared.utils.date_util import get_current_date

        result = get_current_date()
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_returns_iso_format(self) -> None:
        """Should return date in YYYY-MM-DD ISO format."""
        from src.shared.utils.date_util import get_current_date

        result = get_current_date()
        # Basic ISO date regex: YYYY-MM-DD
        parts = result.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # year
        assert len(parts[1]) == 2  # month
        assert len(parts[2]) == 2  # day

        # Verify it's a valid date
        from datetime import date

        parsed = date.fromisoformat(result)
        assert isinstance(parsed, date)

    @pytest.mark.unit
    def test_matches_today(self) -> None:
        """Should return today's date."""
        from src.shared.utils.date_util import get_current_date

        result = get_current_date()
        expected = datetime.now().date().isoformat()
        assert result == expected


class TestDatetimeAndDateConsistency:
    """Tests that both functions return consistent values."""

    @pytest.mark.unit
    def test_date_matches_datetime_date_part(self) -> None:
        """get_current_date should match the date portion of get_current_datetime."""
        from src.shared.utils.date_util import get_current_datetime, get_current_date

        dt = get_current_datetime()
        date_str = get_current_date()
        assert dt.date().isoformat() == date_str
