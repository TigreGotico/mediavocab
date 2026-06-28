"""ISO 639 / ISO 3166 helpers (spec: §6.7). Stdlib only."""
from __future__ import annotations

from mediavocab.text._iso_data import (
    LANGUAGES_639_1,
    LANG_3_TO_1,
    COUNTRIES_3166_1,
    LANGUAGE_NAME_TO_CODE,
    COUNTRY_NAME_TO_CODE,
)


def validate_language(code: str) -> str:
    """Validate ISO 639-1 (2-letter) or ISO 639-2 (3-letter). Returns
    normalised lowercase 2-letter code where possible, else raises ValueError.
    """
    if not code:
        raise ValueError("empty language code")
    c = code.strip().lower()
    if c in LANGUAGES_639_1:
        return c
    if c in LANG_3_TO_1:
        return LANG_3_TO_1[c]
    raise ValueError(f"unknown ISO 639 language code: {code!r}")


def validate_country(code: str) -> str:
    """Validate ISO 3166-1 alpha-2. Returns normalised uppercase code."""
    if not code:
        raise ValueError("empty country code")
    c = code.strip().upper()
    if c in COUNTRIES_3166_1:
        return c
    raise ValueError(f"unknown ISO 3166-1 alpha-2 country code: {code!r}")


def normalize_language(v: str) -> str:
    """Accept full language name, 2-letter, or 3-letter code; return 639-1."""
    if not v:
        raise ValueError("empty language input")
    s = v.strip().lower()
    if s in LANGUAGES_639_1:
        return s
    if s in LANG_3_TO_1:
        return LANG_3_TO_1[s]
    if s in LANGUAGE_NAME_TO_CODE:
        return LANGUAGE_NAME_TO_CODE[s]
    raise ValueError(f"unrecognised language: {v!r}")


def normalize_country(v: str) -> str:
    """Accept full country name or alpha-2 code; return uppercase alpha-2."""
    if not v:
        raise ValueError("empty country input")
    s = v.strip()
    if len(s) == 2 and s.upper() in COUNTRIES_3166_1:
        return s.upper()
    if s.lower() in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[s.lower()]
    raise ValueError(f"unrecognised country: {v!r}")
