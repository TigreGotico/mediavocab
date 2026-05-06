"""Locale loader for mediavocab keyword vocabularies.

`.voc` files contain one plain phrase per line. Blank lines and lines
starting with `#` are ignored. The loader builds word-boundary alternation
regexes and frozensets from these files.

Fallback chain: exact match → language-only → en-us.

Concurrency
-----------
This module exposes **no mutable global state**. Every call accepts an
explicit ``lang`` parameter; when omitted, the default comes from the
``MEDIAVOCAB_LANG`` environment variable read once at import time
(falling back to ``"en-us"``). Concurrent callers in different tenants /
threads / requests should always pass ``lang=`` explicitly — the cache is
keyed on ``(name, lang)`` so different languages do not collide.

Usage:
    from mediavocab.locale import voc_regex
    rx = voc_regex("cut_directors", lang="pt-pt")
"""
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

_LOCALE_DIR = Path(__file__).parent
DEFAULT_LANG: str = os.environ.get("MEDIAVOCAB_LANG", "en-us").lower()


def get_default_lang() -> str:
    """Return the default language (read-only; set via ``MEDIAVOCAB_LANG`` env)."""
    return DEFAULT_LANG


def _fallback_chain(lang: str) -> list:
    chain = [lang]
    if "-" in lang:
        chain.append(lang.split("-")[0])
    if "en-us" not in chain:
        chain.append("en-us")
    return chain


@lru_cache(maxsize=512)
def _load_voc(name: str, lang: str) -> tuple:
    for candidate in _fallback_chain(lang):
        path = _LOCALE_DIR / candidate / f"{name}.voc"
        if path.exists():
            lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
            return tuple(
                line.strip()
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            )
    return ()


@lru_cache(maxsize=512)
def _voc_regex(name: str, lang: str) -> Optional[re.Pattern]:
    phrases = _load_voc(name, lang)
    if not phrases:
        return None
    sorted_phrases = sorted(phrases, key=len, reverse=True)
    alternation = "|".join(re.escape(p) for p in sorted_phrases)
    return re.compile(rf"\b(?:{alternation})\b", re.IGNORECASE)


@lru_cache(maxsize=512)
def _voc_set(name: str, lang: str) -> frozenset:
    return frozenset(p.lower() for p in _load_voc(name, lang))


def voc_regex(name: str, lang: Optional[str] = None) -> Optional[re.Pattern]:
    """Compiled regex for the given .voc file. ``lang`` defaults to
    ``MEDIAVOCAB_LANG`` env (or ``"en-us"``). Always thread-safe — no
    shared mutable state."""
    return _voc_regex(name, (lang or DEFAULT_LANG).lower())


def voc_set(name: str, lang: Optional[str] = None) -> frozenset:
    """Frozenset of lowercase phrases from the given .voc file. ``lang``
    defaults to ``MEDIAVOCAB_LANG`` env (or ``"en-us"``)."""
    return _voc_set(name, (lang or DEFAULT_LANG).lower())
