"""Text utilities. Stdlib only — zero external dependencies."""
from mediavocab.text.normalize import (
    NORMALISE_TITLE_VERSION,
    strip_diacritics,
    normalize,
    fuzzy_ratio,
    token_sort_ratio,
    best_match,
    title_words,
    normalise_title,
    normalise_edition,
    normalise_format,
    normalise_country,
    normalise_language,
)
from mediavocab.text.compare import (
    TITLE_MIN,
    ARTIST_MIN,
    YEAR_WINDOW,
    RUNTIME_TOLERANCE_S,
    RUNTIME_HASH_QUANTUM_S,
    QUANTUM_SKIP,
    IDENTITY_FIELDS,
    IdentityConflict,
    MergeStrategy,
    DEFAULT_STRATEGY,
    ScoreBreakdown,
    compare,
    score,
    score_breakdown,
    merge,
    merge_all,
    merge_releases,
    country_slot,
    work_hash,
    release_hash,
)
from mediavocab.text.iso import (
    validate_language,
    validate_country,
    normalize_language,
    normalize_country,
)
from mediavocab.text.isbn import (
    isbn10_to_13,
    isbn13_to_10,
    normalize_isbn,
)
from mediavocab.text.title_parse import parse_title, TitleParseResult
from mediavocab._iso_date import IsoDate, parse_iso_date

__all__ = [
    "NORMALISE_TITLE_VERSION",
    "strip_diacritics", "normalize", "fuzzy_ratio", "token_sort_ratio",
    "best_match", "title_words",
    "normalise_title", "normalise_edition", "normalise_format",
    "normalise_country", "normalise_language",
    "TITLE_MIN", "ARTIST_MIN", "YEAR_WINDOW",
    "RUNTIME_TOLERANCE_S", "RUNTIME_HASH_QUANTUM_S", "QUANTUM_SKIP",
    "IDENTITY_FIELDS",
    "IdentityConflict", "MergeStrategy", "DEFAULT_STRATEGY",
    "ScoreBreakdown", "compare", "score", "score_breakdown",
    "merge", "merge_all", "merge_releases",
    "country_slot",
    "work_hash", "release_hash",
    "validate_language", "validate_country",
    "normalize_language", "normalize_country",
    "isbn10_to_13", "isbn13_to_10", "normalize_isbn",
    "parse_title", "TitleParseResult",
    "IsoDate", "parse_iso_date",
]
