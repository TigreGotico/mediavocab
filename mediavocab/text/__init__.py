"""Text utilities. Stdlib only — zero external dependencies."""
from mediavocab.text.normalize import (
    strip_diacritics,
    normalize,
    fuzzy_ratio,
    best_match,
    title_words,
)
from mediavocab.text.compare import (
    TITLE_MIN,
    ARTIST_MIN,
    YEAR_WINDOW,
    RUNTIME_TOLERANCE_S,
    compare,
    score,
    merge,
    work_hash,
)
from mediavocab.text.iso import (
    validate_language,
    validate_country,
    normalize_language,
    normalize_country,
)

__all__ = [
    "strip_diacritics", "normalize", "fuzzy_ratio", "best_match", "title_words",
    "TITLE_MIN", "ARTIST_MIN", "YEAR_WINDOW", "RUNTIME_TOLERANCE_S",
    "compare", "score", "merge", "work_hash",
    "validate_language", "validate_country",
    "normalize_language", "normalize_country",
]
