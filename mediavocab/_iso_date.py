"""ISO-8601 date / datetime boundary type.

Pydantic field validator + reusable annotated alias for fields that
carry "an ISO-8601 date or datetime, possibly with a timezone." Used
on ``Release.release_date`` and on ``AvailabilityWindow`` start / end
boundaries (which carry broadcast slots in datetime form, spec §5.5) —
anywhere mediavocab persists a wire-format date string instead of a
typed ``datetime``.

Why a string and not :class:`~datetime.datetime`?

- Sources hand us partial data ("2025", "2025-09") that ``datetime``
  cannot represent.
- Round-trip-stable serialisation: the string is the canonical form
  for cross-source dedup hashes; reformatting via ``datetime.isoformat()``
  drops the input precision and breaks hash equality.

The validator only enforces *parseability*: a non-empty value must
parse as either an ISO-8601 date or datetime. We never normalise.
Empty / ``None`` is always allowed — absence is not a value (A2).
"""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import AfterValidator


_ISO_DATE_RE = re.compile(
    r"^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+\-]\d{2}:?\d{2})?)?)?)?$"
)


def parse_iso_date(value: Optional[str]) -> Optional[str]:
    """Validate an ISO-8601 date / datetime string, return it unchanged.

    Accepts:

    - Full datetime with offset:           ``2025-09-05T19:00:00+01:00``
    - Datetime in UTC with ``Z`` suffix:   ``2025-09-05T19:00:00Z``
    - Datetime without offset:             ``2025-09-05T19:00:00``
    - Date:                                ``2025-09-05``
    - Year-month:                          ``2025-09``
    - Year only:                           ``2025``

    Empty string and ``None`` are passed through unchanged — they mean
    "unknown", not invalid (A2).
    """
    if value is None or value == "":
        return value
    if not isinstance(value, str):
        raise TypeError(f"ISO date must be a string, got {type(value).__name__}")
    if not _ISO_DATE_RE.match(value):
        raise ValueError(
            f"not a valid ISO-8601 date / datetime: {value!r}. "
            "Expected forms: YYYY, YYYY-MM, YYYY-MM-DD, "
            "YYYY-MM-DDTHH:MM[:SS[.fff]][Z|±HH:MM]."
        )
    # Round-trip via stdlib for the longer forms — catches things the
    # regex would let pass (Feb 30, 25:00, etc.).
    if "T" in value:
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"unparseable ISO datetime {value!r}: {exc}") from exc
    elif len(value) == 10:
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"unparseable ISO date {value!r}: {exc}") from exc
    return value


# Reusable Pydantic annotation. Use as ``IsoDate`` or
# ``Optional[IsoDate]`` on every model field that carries an ISO-8601
# date or datetime string.
IsoDate = Annotated[str, AfterValidator(parse_iso_date)]


def iso_compare(a: str, b: str) -> int:
    """Compare two ISO-8601 date / datetime strings semantically.

    Returns -1 if ``a < b``, 0 if equal, +1 if ``a > b``. Year-only values
    compare as the first day of that year; year-month as the first day of that
    month; date-only as midnight. Datetime values with timezone are compared
    in UTC; datetimes without a timezone are treated as naive (lexically
    valid but compared in their stated wall-clock).

    Raises ``ValueError`` if either side is not a valid ISO-8601 form.
    """
    parse_iso_date(a)
    parse_iso_date(b)

    def _to_dt(v: str) -> datetime:
        if "T" in v:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        if len(v) == 10:
            return datetime.fromisoformat(v + "T00:00:00")
        if len(v) == 7:
            return datetime.fromisoformat(v + "-01T00:00:00")
        # year only
        return datetime.fromisoformat(v + "-01-01T00:00:00")

    da, db = _to_dt(a), _to_dt(b)
    # Normalise tz-naive vs tz-aware: if one has tz, assume the other is UTC.
    if (da.tzinfo is None) != (db.tzinfo is None):
        from datetime import timezone
        if da.tzinfo is None:
            da = da.replace(tzinfo=timezone.utc)
        if db.tzinfo is None:
            db = db.replace(tzinfo=timezone.utc)
    if da < db:
        return -1
    if da > db:
        return 1
    return 0
