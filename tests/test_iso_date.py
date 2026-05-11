"""Tests for `mediavocab._iso_date` — the ISO-8601 boundary type."""
import pytest

from mediavocab._iso_date import iso_compare, parse_iso_date


# ---------------------------------------------------------------------------
# parse_iso_date — accepted forms
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "2025",
    "2025-09",
    "2025-09-05",
    "2025-09-05T19:00:00",
    "2025-09-05T19:00:00Z",
    "2025-09-05T19:00:00+01:00",
    "2025-09-05T19:00:00-04:30",
    "2025-09-05T19:00:00.123456+00:00",
])
def test_parse_accepts_valid_iso_forms(s):
    assert parse_iso_date(s) == s


def test_parse_accepts_empty_and_none():
    """Absence is not a value (A2) — empty / None pass through."""
    assert parse_iso_date("") == ""
    assert parse_iso_date(None) is None


# ---------------------------------------------------------------------------
# parse_iso_date — rejected forms
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "not-a-date",
    "2025/09/05",            # wrong separator
    "2025-13-01",            # invalid month
    "2025-02-30",            # Feb 30
    "2025-09-05T25:00:00",   # invalid hour
    "2025-09-05T19:60:00",   # invalid minute
    "20250905",              # no separators
    "Sep 5 2025",
])
def test_parse_rejects_invalid(s):
    with pytest.raises(ValueError):
        parse_iso_date(s)


def test_parse_rejects_non_string():
    with pytest.raises(TypeError):
        parse_iso_date(20250905)   # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# iso_compare
# ---------------------------------------------------------------------------

def test_compare_full_datetimes():
    assert iso_compare("2025-09-05T10:00:00Z", "2025-09-05T12:00:00Z") == -1
    assert iso_compare("2025-09-05T10:00:00Z", "2025-09-05T10:00:00Z") == 0
    assert iso_compare("2025-09-05T12:00:00Z", "2025-09-05T10:00:00Z") == 1


def test_compare_dates():
    assert iso_compare("2024-12-31", "2025-01-01") == -1
    assert iso_compare("2025-01-01", "2025-01-01") == 0


def test_compare_year_only_vs_full_date():
    """Year-only compares as the first day of that year."""
    assert iso_compare("2025", "2025-06-15") == -1
    assert iso_compare("2025-06-15", "2025") == 1


def test_compare_year_month_vs_year():
    assert iso_compare("2025-03", "2025") == 1   # 2025-03-01 > 2025-01-01
    assert iso_compare("2025", "2025-03") == -1


def test_compare_naive_and_aware_treated_as_utc():
    """When one side has tz and the other doesn't, the naive side is assumed UTC."""
    assert iso_compare("2025-09-05T10:00:00", "2025-09-05T10:00:00Z") == 0


def test_compare_across_timezones():
    """11:00 UTC == 12:00 +01:00."""
    assert iso_compare("2025-09-05T11:00:00Z", "2025-09-05T12:00:00+01:00") == 0


def test_compare_invalid_raises():
    with pytest.raises(ValueError):
        iso_compare("not-a-date", "2025")
