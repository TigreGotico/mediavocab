"""ISO-8601 date / datetime boundary type.

Pydantic field validator + reusable annotated alias for fields that
carry "an ISO-8601 date or datetime, possibly with a timezone." Used
on Release availability windows, Programme slots, Schedule windows,
fetched_at timestamps — anywhere mediavocab persists a wire-format
date string instead of a typed ``datetime``.

Why a string and not :class:`~datetime.datetime`?

- Sources hand us partial data ("2025", "2025-09") that ``datetime``
  cannot represent.
- Round-trip-stable serialisation: the string is the canonical form
  for cross-source dedup hashes; reformatting via ``datetime.isoformat()``
  drops the input precision and breaks hash equality.

The validator only enforces *parseability*: a non-empty value must
parse as either an ISO-8601 date or datetime. We never normalise.
Empty / ``None`` is always allowed — absence is not a value (axiom 3).
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
    "unknown", not invalid (spec axiom 3).
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
