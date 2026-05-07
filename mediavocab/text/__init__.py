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
from mediavocab.text.classify import classify_video, classify_video_dict, extract_tags
from mediavocab._iso_date import IsoDate, parse_iso_date

__all__ = [
    "strip_diacritics", "normalize", "fuzzy_ratio", "best_match", "title_words",
    "TITLE_MIN", "ARTIST_MIN", "YEAR_WINDOW", "RUNTIME_TOLERANCE_S",
    "compare", "score", "merge", "work_hash", "release_hash",
    "validate_language", "validate_country",
    "normalize_language", "normalize_country",
    "isbn10_to_13", "isbn13_to_10", "normalize_isbn",
    "parse_title", "TitleParseResult",
    "classify_video", "classify_video_dict", "extract_tags",
    "IsoDate", "parse_iso_date",
]
