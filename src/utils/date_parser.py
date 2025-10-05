"""
Date parsing utilities for flexible date range queries.

Supports:
- ISO 8601 format: "2025-01-15", "2025-01-15T10:30:00Z"
- Natural language: "today", "yesterday", "last week", "last month"
- Relative expressions: "N days ago", "N weeks ago", "N months ago"
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import re
from dateutil.parser import parse as parse_iso


class DateParseError(ValueError):
    """Raised when a date string cannot be parsed."""
    pass


def parse_date(date_str: str, is_start: bool = True) -> datetime:
    """
    Parse flexible date string into timezone-aware datetime object.

    Args:
        date_str: Date string to parse
        is_start: If True, default to start of day (00:00:00);
                 if False, end of day (23:59:59)

    Returns:
        Timezone-aware datetime in UTC

    Raises:
        DateParseError: If date string cannot be parsed

    Examples:
        >>> parse_date("2025-01-15")
        datetime(2025, 1, 15, 0, 0, 0, tzinfo=timezone.utc)

        >>> parse_date("today", is_start=False)
        datetime(..., 23, 59, 59, 999999, tzinfo=timezone.utc)

        >>> parse_date("3 days ago")
        datetime(..., tzinfo=timezone.utc)
    """
    if not date_str:
        raise DateParseError("Date string cannot be empty")

    date_str = date_str.strip()
    date_str_lower = date_str.lower()
    now = datetime.now(timezone.utc)

    try:
        # Try natural language and relative dates first
        base_date = _parse_relative_date(date_str_lower, now)

        if base_date is not None:
            # For relative dates, set to start/end of day
            if is_start:
                return base_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                return base_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Try ISO 8601 format
        parsed = parse_iso(date_str)

        # Ensure timezone-aware
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        # If only date was provided (no time), set to start/end of day
        if _is_date_only(date_str):
            if is_start:
                parsed = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                parsed = parsed.replace(hour=23, minute=59, second=59, microsecond=999999)

        return parsed

    except (ValueError, TypeError) as e:
        raise DateParseError(f"Unable to parse date string '{date_str}': {e}")


def _parse_relative_date(date_str: str, now: datetime) -> Optional[datetime]:
    """
    Parse relative date expressions.

    Args:
        date_str: Lowercase date string
        now: Current datetime for reference

    Returns:
        Datetime object if parsed, None if not a relative date
    """
    # Simple relative dates
    if date_str == "today":
        return now
    elif date_str == "yesterday":
        return now - timedelta(days=1)
    elif date_str == "tomorrow":
        return now + timedelta(days=1)

    # Week/month relative dates
    elif date_str == "last week":
        return now - timedelta(weeks=1)
    elif date_str == "last month":
        return now - timedelta(days=30)
    elif date_str == "last year":
        return now - timedelta(days=365)

    # Start/end of period
    elif date_str == "start of week":
        days_since_monday = now.weekday()
        return now - timedelta(days=days_since_monday)
    elif date_str == "start of month":
        return now.replace(day=1)
    elif date_str == "end of month":
        # Go to first day of next month, then subtract one day
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        return next_month - timedelta(days=1)

    # "N days/weeks/months ago" pattern (also handles "two weeks ago")
    # First try to parse number words
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    match = re.match(r"(\w+)\s+(day|week|month|year)s?\s+ago", date_str)
    if match:
        count_str = match.group(1)
        unit = match.group(2)

        # Try to parse as number or number word
        try:
            count = int(count_str)
        except ValueError:
            count = number_words.get(count_str.lower())
            if count is None:
                return None

        if unit == "day":
            return now - timedelta(days=count)
        elif unit == "week":
            return now - timedelta(weeks=count)
        elif unit == "month":
            return now - timedelta(days=count * 30)
        elif unit == "year":
            return now - timedelta(days=count * 365)

    # "N days/weeks/months from now" pattern
    match = re.match(r"(\d+)\s+(day|week|month|year)s?\s+from\s+now", date_str)
    if match:
        count = int(match.group(1))
        unit = match.group(2)

        if unit == "day":
            return now + timedelta(days=count)
        elif unit == "week":
            return now + timedelta(weeks=count)
        elif unit == "month":
            return now + timedelta(days=count * 30)
        elif unit == "year":
            return now + timedelta(days=count * 365)

    return None


def _is_date_only(date_str: str) -> bool:
    """
    Check if date string contains only date (no time component).

    Args:
        date_str: Date string to check

    Returns:
        True if date only, False if includes time
    """
    # Simple heuristic: if contains 'T' or ':', likely has time
    return 'T' not in date_str and ':' not in date_str


def parse_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse start and end date strings into a date range.

    Args:
        start_date: Start date string (inclusive), or None for no start limit
        end_date: End date string (inclusive), or None for no end limit

    Returns:
        Tuple of (start_datetime, end_datetime), either may be None

    Raises:
        DateParseError: If date strings cannot be parsed
        ValueError: If start_date is after end_date

    Examples:
        >>> parse_date_range("2025-01-01", "2025-01-31")
        (datetime(2025, 1, 1, 0, 0, 0), datetime(2025, 1, 31, 23, 59, 59))

        >>> parse_date_range("last week", "yesterday")
        (datetime(...), datetime(...))

        >>> parse_date_range(start_date="2025-01-01")
        (datetime(2025, 1, 1, 0, 0, 0), None)
    """
    start_dt = None
    end_dt = None

    if start_date:
        start_dt = parse_date(start_date, is_start=True)

    if end_date:
        end_dt = parse_date(end_date, is_start=False)

    # Validate range
    if start_dt and end_dt and start_dt > end_dt:
        raise ValueError(
            f"Start date ({start_dt}) cannot be after end date ({end_dt})"
        )

    return start_dt, end_dt


def format_date_range(
    start_dt: Optional[datetime],
    end_dt: Optional[datetime]
) -> str:
    """
    Format a date range into a human-readable string.

    Args:
        start_dt: Start datetime or None
        end_dt: End datetime or None

    Returns:
        Formatted string like "2025-01-01 to 2025-01-31"

    Examples:
        >>> format_date_range(
        ...     datetime(2025, 1, 1, tzinfo=timezone.utc),
        ...     datetime(2025, 1, 31, tzinfo=timezone.utc)
        ... )
        '2025-01-01 to 2025-01-31'
    """
    if start_dt and end_dt:
        return f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
    elif start_dt:
        return f"from {start_dt.strftime('%Y-%m-%d')}"
    elif end_dt:
        return f"until {end_dt.strftime('%Y-%m-%d')}"
    else:
        return "all time"
