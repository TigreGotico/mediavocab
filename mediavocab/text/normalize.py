"""Text normalisation and fuzzy matching. Spec §7.1. Stdlib only.

``NORMALISE_TITLE_VERSION`` pins the behaviour of :func:`normalise_title`.
The ``work_hash`` and ``release_hash`` stability contract (§6.3) depends on
this function being frozen: any semantic change to ``normalise_title`` MUST
increment this constant and constitutes a breaking change requiring a major
version bump.
"""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import List, Tuple


#: Version pin for normalise_title() behaviour.
#: Increment when the normalisation pipeline changes in a way that would
#: alter existing work_hash values.
NORMALISE_TITLE_VERSION: int = 1

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


def token_sort_ratio(a: str, b: str) -> float:
    """Sort tokens alphabetically before comparing. [0.0, 1.0].

    Handles leading articles and word-order variants:
    ``token_sort_ratio("The Dark Knight", "Dark Knight, The")`` → ≥ 0.95

    Normalises both strings first (diacritics, punctuation, lowercasing),
    splits on whitespace, sorts the token lists, rejoins, then runs
    SequenceMatcher. More robust than ``fuzzy_ratio`` for media titles
    where articles, subtitles, and word-order differ across providers.
    """
    na, nb = normalize(a), normalize(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    sa = " ".join(sorted(na.split()))
    sb = " ".join(sorted(nb.split()))
    return SequenceMatcher(None, sa, sb).ratio()


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


# ---------------------------------------------------------------------------
# Identity-input primitives (spec §6.1)
# ---------------------------------------------------------------------------

def normalise_title(s: str) -> str:
    """Full `normalize` pipeline (§6.1). Empty input → empty output.
    Used as a `work_hash` / `release_hash` input."""
    return normalize(s or "")


def normalise_edition(s: str) -> str:
    """Same as `normalise_title` — used for `edition`, `source_format`,
    and any free-text identity tag where typos / spacing variants should
    collide (§6.1)."""
    return normalize(s or "")


def normalise_format(s: str) -> str:
    """Lowercase, ASCII-stripped, whitespace-collapsed, no punctuation.
    `"Blu-ray"` → `"bluray"`; `"320 kbps"` → `"320kbps"`;
    `"H.265"` → `"h265"` (§6.1)."""
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


# Canonical short-forms for the free-text Release.codec / Release.container
# fields (T6). These stay strings — there is no controlled enum — but
# providers emit the same codec under many spellings ("mp3", "audio/mpeg",
# "MPEG-1 Layer III") and bare `normalise_format` does not collide them, so
# release-level dedup is unreliable without an alias map.
_CODEC_ALIASES = {
    "audiompeg": "mp3", "mpeg": "mp3", "mpeg1layeriii": "mp3", "mp3": "mp3",
    "audioaac": "aac", "mp4a": "aac", "aac": "aac", "aaclc": "aac",
    "heaac": "heaac", "heaacv2": "heaac",
    "audioopus": "opus", "opus": "opus",
    "audioogg": "vorbis", "oggvorbis": "vorbis", "vorbis": "vorbis",
    "audioflac": "flac", "flac": "flac",
    "alac": "alac",
    "audiowav": "pcm", "wav": "pcm", "pcm": "pcm", "lpcm": "pcm",
    "ac3": "ac3", "eac3": "eac3",
    "avc": "h264", "h264": "h264", "x264": "h264",
    "hevc": "h265", "h265": "h265", "x265": "h265",
    "vp9": "vp9", "av1": "av1",
}

_CONTAINER_ALIASES = {
    "mp3": "mp3",
    "m4a": "m4a", "mp4a": "m4a",
    "mp4": "mp4", "videomp4": "mp4",
    "mkv": "mkv", "matroska": "mkv",
    "webm": "webm",
    "ogg": "ogg", "oga": "ogg",
    "flac": "flac",
    "wav": "wav",
    "avi": "avi",
    "ts": "mpegts", "mpegts": "mpegts", "m2ts": "mpegts",
    "m3u8": "hls", "hls": "hls",
    "applicationxmpegurl": "hls", "applicationvndapplempegurl": "hls",
    "audiompegurl": "hls", "vndapplempegurl": "hls",
}


def normalise_codec(s: str) -> str:
    """Canonicalise a free-text codec string for release-level dedup.

    Maps MIME types and common synonyms to a stable short-form
    (`"audio/mpeg"`, `"MPEG-1 Layer III"`, `"mp3"` → `"mp3"`). Unknown
    codecs fall through to bare `normalise_format`. Empty → empty."""
    key = normalise_format(s)
    return _CODEC_ALIASES.get(key, key)


def normalise_container(s: str) -> str:
    """Canonicalise a free-text container/format string for release-level
    dedup. (`"M4A"`, `"mp4a"` → `"m4a"`; `"application/x-mpegURL"`,
    `".m3u8"` → `"hls"`). Unknown containers fall through to bare
    `normalise_format`. Empty → empty."""
    key = normalise_format(s)
    return _CONTAINER_ALIASES.get(key, key)


def normalise_country(s: str) -> str:
    """ISO 3166-1 alpha-2 uppercase via `text.iso.normalize_country` (§6.1).
    Empty / None → empty; unrecognised input raises `ValueError`."""
    if not s:
        return ""
    from mediavocab.text.iso import normalize_country
    return normalize_country(s)


def normalise_language(s: str) -> str:
    """ISO 639-1 lowercase via `text.iso.normalize_language` (§6.1).
    Empty / None → empty; unrecognised input raises `ValueError`."""
    if not s:
        return ""
    from mediavocab.text.iso import normalize_language
    return normalize_language(s)
