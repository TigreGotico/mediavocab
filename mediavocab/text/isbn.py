"""ISBN helpers — pure stdlib, no validation deps.

Used to canonicalise the ``isbn_10`` / ``isbn_13`` representations on
:class:`mediavocab.models.ExternalIds` and to test whether two ISBNs
identify the same edition.
"""
from __future__ import annotations

from typing import Optional


def _isbn_digits(value: str) -> str:
    """Strip hyphens and spaces; uppercase a trailing 'x' check digit."""
    return "".join(ch for ch in value.upper() if ch.isdigit() or ch == "X")


def normalize_isbn(value: str) -> Optional[str]:
    """Return a clean ISBN with no hyphens/spaces, or ``None`` if unrecognised.

    Accepts 10- or 13-digit ISBNs; preserves the trailing ``X`` check digit
    on ISBN-10. Does not verify the check digit — pass through any string
    of the right length so consumers can keep imperfectly-typed catalogue
    entries.
    """
    if not value:
        return None
    digits = _isbn_digits(value)
    if len(digits) in (10, 13):
        return digits
    return None


def isbn10_to_13(isbn10: str) -> Optional[str]:
    """Convert a 10-character ISBN to its 13-character form.

    Returns ``None`` on bad input.
    """
    digits = _isbn_digits(isbn10)
    if len(digits) != 10:
        return None
    body = "978" + digits[:9]
    try:
        total = sum((1 if i % 2 == 0 else 3) * int(c) for i, c in enumerate(body))
    except ValueError:
        return None
    check = (10 - total % 10) % 10
    return body + str(check)


def isbn13_to_10(isbn13: str) -> Optional[str]:
    """Convert a 978-prefixed 13-character ISBN to its 10-character form.

    Returns ``None`` for non-978 prefixes (979- ISBNs cannot be expressed
    as ISBN-10) or otherwise malformed input.
    """
    digits = _isbn_digits(isbn13)
    if len(digits) != 13 or not digits.startswith("978"):
        return None
    body = digits[3:12]
    total = sum((10 - i) * int(c) for i, c in enumerate(body))
    rem = (11 - total % 11) % 11
    check = "X" if rem == 10 else str(rem)
    return body + check
