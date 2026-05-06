"""Text normalisation and fuzzy matching. Spec §7.1. Stdlib only."""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import List, Tuple


_FEAT_RE = re.compile(
    r"[\(\[]?\s*(?:feat\.?|ft\.?|featuring)\s+[^\)\]]*[\)\]]?",
    flags=re.IGNORECASE,
)
_BRACKETED_RE = re.compile(r"[\(\[\{][^\)\]\}]*[\)\]\}]")
_NON_WORD_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_WS_RE = re.compile(r"\s+")

# Common articles/stopwords across major European languages.
_STOPWORDS = frozenset({
    "the", "a", "an",
    "der", "die", "das", "den", "dem", "des",
    "le", "la", "les", "l",
    "el", "los", "las",
    "un", "una", "uno", "unas", "unos",
    "il", "lo", "i", "gli",
    "o", "os", "as",  # pt
})


def strip_diacritics(text: str) -> str:
    """NFKD decomposition, drop combining marks. 'café' → 'cafe'."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def normalize(text: str) -> str:
    """Full normalisation pipeline. Output is suitable for fuzzy comparison."""
    if not text:
        return ""
    s = strip_diacritics(text).lower()
    s = _FEAT_RE.sub(" ", s)
    s = _BRACKETED_RE.sub(" ", s)
    s = _NON_WORD_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def fuzzy_ratio(a: str, b: str) -> float:
    """SequenceMatcher ratio on normalize(a) vs normalize(b). [0.0, 1.0]."""
    na, nb = normalize(a), normalize(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def best_match(query: str, candidates: List[str]) -> Tuple[str, float]:
    """Return (best_candidate, score). Empty candidates → ("", 0.0)."""
    best, score = "", 0.0
    for c in candidates:
        r = fuzzy_ratio(query, c)
        if r > score:
            best, score = c, r
    return best, score


def title_words(text: str) -> List[str]:
    """Tokenise into meaningful words; strip stopwords/articles."""
    return [w for w in normalize(text).split() if w and w not in _STOPWORDS]
