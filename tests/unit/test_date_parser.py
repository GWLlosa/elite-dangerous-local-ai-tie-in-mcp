"""
Unit tests for date parser utilities.

Tests flexible date parsing including ISO 8601 formats, natural language,
and relative date expressions.
"""

import pytest
from datetime import datetime, timedelta, timezone
from freezegun import freeze_time

from src.utils.date_parser import (
    parse_date,
    parse_date_range,
    format_date_range,
    DateParseError,
    _parse_relative_date,
    _is_date_only
)


class TestParseDateISO:
    """Test ISO 8601 date parsing."""

    def test_parse_iso_date_only(self):
        """Test parsing date without time (start of day)."""
        result = parse_date("2025-01-15", is_start=True)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 0
        assert result.minute == 0
        assert result.second == 0
        assert result.tzinfo == timezone.utc

    def test_parse_iso_date_only_end(self):
        """Test parsing date without time (end of day)."""
        result = parse_date("2025-01-15", is_start=False)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 23
        assert result.minute == 59
        assert result.second == 59
        assert result.tzinfo == timezone.utc

    def test_parse_iso_datetime_with_time(self):
        """Test parsing ISO datetime with time component."""
        result = parse_date("2025-01-15T10:30:45Z")
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45
        # Check timezone is UTC (compare offset, not object identity)
        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(0)

    def test_parse_iso_datetime_no_timezone(self):
        """Test parsing ISO datetime without timezone (assumes UTC)."""
        result = parse_date("2025-01-15T10:30:45")
        assert result.tzinfo == timezone.utc

    def test_parse_different_date_formats(self):
        """Test various valid ISO date formats."""
        dates = [
            "2025-01-01",
            "2025-12-31",
            "2024-02-29",  # Leap year
            "2025-01-15T00:00:00Z",
            "2025-01-15T23:59:59+00:00"
        ]
        for date_str in dates:
            result = parse_date(date_str)
            # Check timezone is UTC (compare offset, not object identity)
            assert result.tzinfo is not None
            assert result.utcoffset() == timedelta(0)


class TestParseDateNaturalLanguage:
    """Test natural language date parsing."""

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_today(self):
        """Test parsing 'today'."""
        result = parse_date("today", is_start=True)
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 5
        assert result.hour == 0
        assert result.minute == 0

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_date("yesterday", is_start=True)
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 4

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_date("tomorrow", is_start=True)
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 6

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_last_week(self):
        """Test parsing 'last week'."""
        result = parse_date("last week", is_start=True)
        expected = datetime(2025, 9, 28, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_last_month(self):
        """Test parsing 'last month'."""
        result = parse_date("last month", is_start=True)
        # last month = 30 days ago
        expected = datetime(2025, 9, 5, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_last_year(self):
        """Test parsing 'last year'."""
        result = parse_date("last year", is_start=True)
        # last year = 365 days ago
        expected = datetime(2024, 10, 5, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_start_of_week(self):
        """Test parsing 'start of week' (Monday)."""
        result = parse_date("start of week", is_start=True)
        # Oct 5, 2025 is Sunday, so start of week is Sept 29 (Monday)
        # Actually freezegun sets Sunday as Oct 5, weekday()=6
        # Monday of that week would be Sept 29
        assert result.weekday() == 0  # Monday

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_start_of_month(self):
        """Test parsing 'start of month'."""
        result = parse_date("start of month", is_start=True)
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 1

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_end_of_month(self):
        """Test parsing 'end of month'."""
        result = parse_date("end of month", is_start=True)
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 31  # October has 31 days


class TestParseDateRelative:
    """Test relative date expressions."""

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_days_ago(self):
        """Test parsing 'N days ago'."""
        result = parse_date("3 days ago", is_start=True)
        expected = datetime(2025, 10, 2, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_weeks_ago(self):
        """Test parsing 'N weeks ago'."""
        result = parse_date("2 weeks ago", is_start=True)
        expected = datetime(2025, 9, 21, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_months_ago(self):
        """Test parsing 'N months ago'."""
        result = parse_date("1 month ago", is_start=True)
        # 1 month = 30 days
        expected = datetime(2025, 9, 5, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_years_ago(self):
        """Test parsing 'N years ago'."""
        result = parse_date("1 year ago", is_start=True)
        expected = datetime(2024, 10, 5, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_singular_day_ago(self):
        """Test parsing '1 day ago' (singular)."""
        result = parse_date("1 day ago", is_start=True)
        expected = datetime(2025, 10, 4, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_days_from_now(self):
        """Test parsing 'N days from now'."""
        result = parse_date("3 days from now", is_start=True)
        expected = datetime(2025, 10, 8, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_weeks_from_now(self):
        """Test parsing 'N weeks from now'."""
        result = parse_date("2 weeks from now", is_start=True)
        expected = datetime(2025, 10, 19, 0, 0, 0, tzinfo=timezone.utc)
        assert result == expected


class TestParseDateErrors:
    """Test error handling in date parsing."""

    def test_parse_empty_string(self):
        """Test parsing empty string raises error."""
        with pytest.raises(DateParseError):
            parse_date("")

    def test_parse_invalid_format(self):
        """Test parsing invalid format raises error."""
        with pytest.raises(DateParseError):
            parse_date("not a date")

    def test_parse_invalid_iso_date(self):
        """Test parsing invalid ISO date raises error."""
        with pytest.raises(DateParseError):
            parse_date("2025-13-45")  # Invalid month and day


class TestParseDateRange:
    """Test date range parsing."""

    def test_parse_range_both_dates(self):
        """Test parsing date range with both start and end."""
        start, end = parse_date_range("2025-01-01", "2025-01-31")
        assert start.year == 2025
        assert start.month == 1
        assert start.day == 1
        assert start.hour == 0  # Start of day
        assert end.year == 2025
        assert end.month == 1
        assert end.day == 31
        assert end.hour == 23  # End of day

    def test_parse_range_only_start(self):
        """Test parsing date range with only start date."""
        start, end = parse_date_range("2025-01-01", None)
        assert start.year == 2025
        assert start.month == 1
        assert start.day == 1
        assert end is None

    def test_parse_range_only_end(self):
        """Test parsing date range with only end date."""
        start, end = parse_date_range(None, "2025-01-31")
        assert start is None
        assert end.year == 2025
        assert end.month == 1
        assert end.day == 31

    def test_parse_range_neither(self):
        """Test parsing date range with no dates."""
        start, end = parse_date_range(None, None)
        assert start is None
        assert end is None

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_range_natural_language(self):
        """Test parsing date range with natural language."""
        start, end = parse_date_range("last week", "today")
        assert start < end
        assert end.day == 5
        assert end.month == 10

    def test_parse_range_invalid_order(self):
        """Test parsing date range where start is after end."""
        with pytest.raises(ValueError, match="Start date .* cannot be after end date"):
            parse_date_range("2025-01-31", "2025-01-01")


class TestFormatDateRange:
    """Test date range formatting."""

    def test_format_both_dates(self):
        """Test formatting with both start and end dates."""
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        end = datetime(2025, 1, 31, tzinfo=timezone.utc)
        result = format_date_range(start, end)
        assert result == "2025-01-01 to 2025-01-31"

    def test_format_only_start(self):
        """Test formatting with only start date."""
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        result = format_date_range(start, None)
        assert result == "from 2025-01-01"

    def test_format_only_end(self):
        """Test formatting with only end date."""
        end = datetime(2025, 1, 31, tzinfo=timezone.utc)
        result = format_date_range(None, end)
        assert result == "until 2025-01-31"

    def test_format_neither(self):
        """Test formatting with no dates."""
        result = format_date_range(None, None)
        assert result == "all time"


class TestHelperFunctions:
    """Test helper functions."""

    def test_is_date_only_true(self):
        """Test identifying date-only strings."""
        assert _is_date_only("2025-01-15")
        assert _is_date_only("2025-12-31")

    def test_is_date_only_false(self):
        """Test identifying datetime strings."""
        assert not _is_date_only("2025-01-15T10:30:00Z")
        assert not _is_date_only("2025-01-15 10:30:00")
        assert not _is_date_only("10:30:00")

    @freeze_time("2025-10-05 14:30:00")
    def test_parse_relative_date_returns_none_for_invalid(self):
        """Test _parse_relative_date returns None for non-relative dates."""
        now = datetime.now(timezone.utc)
        result = _parse_relative_date("2025-01-15", now)
        assert result is None


class TestComprehensiveDateFormats:
    """Test comprehensive date format support."""

    @freeze_time("2025-10-05 14:30:00")
    def test_all_supported_formats(self):
        """Test all documented date formats are supported."""
        formats = [
            # ISO 8601
            "2025-01-15",
            "2025-01-15T10:30:00Z",
            "2025-01-15T10:30:00",
            # Natural language
            "today",
            "yesterday",
            "tomorrow",
            "last week",
            "last month",
            "last year",
            # Relative
            "1 day ago",
            "3 days ago",
            "1 week ago",
            "2 weeks ago",
            "two weeks ago",
            "1 month ago",
            "3 months ago",
            "1 year ago",
            "1 day from now",
            "3 days from now",
            "2 weeks from now",
            # Start/end of period
            "start of week",
            "start of month",
            "end of month"
        ]

        for date_str in formats:
            result = parse_date(date_str)
            assert result is not None
            # Check timezone is UTC (compare offset, not object identity)
            assert result.tzinfo is not None
            assert result.utcoffset() == timedelta(0)
