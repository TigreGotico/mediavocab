"""Locale loader for mediavocab keyword vocabularies.

Backed by ``ovos-spec-tools`` (``LocaleResources``) which implements the
OVOS-INTENT-2 spec: UTF-8 `.voc` files, one phrase per line, blank lines
and ``#``-comment lines ignored, fallback chain through language families
to ``en-us``.

Fallback chain: ovos-spec-tools → language-only tag → en-us.

Usage:
    from mediavocab.locale import voc_regex, voc_set
    rx = voc_regex("cut_directors", lang="pt-pt")
    phrases = voc_set("cut_directors", lang="pt-pt")
"""
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ovos_spec_tools import LocaleResources

_LOCALE_DIR = Path(__file__).parent
DEFAULT_LANG: str = os.environ.get("MEDIAVOCAB_LANG", "en-us").lower()

_resources = LocaleResources(skill_locale=str(_LOCALE_DIR))


def get_default_lang() -> str:
    """Return the default language (read-only; set via ``MEDIAVOCAB_LANG`` env)."""
    return DEFAULT_LANG


@lru_cache(maxsize=512)
def _load_voc(name: str, lang: str) -> tuple:
    # Try requested language (ovos-spec-tools handles language-family fallback internally)
    vocs = _resources.vocabularies(lang)
    phrases = vocs.get(name)
    if phrases:
        return tuple(phrases)
    # Final fallback: en-us (the canonical source)
    if lang != "en-us":
        vocs_en = _resources.vocabularies("en-us")
        phrases = vocs_en.get(name)
        if phrases:
            return tuple(phrases)
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
    ``MEDIAVOCAB_LANG`` env (or ``"en-us"``). Thread-safe — backed by
    ``ovos-spec-tools`` ``LocaleResources``."""
    return _voc_regex(name, (lang or DEFAULT_LANG).lower())


def voc_set(name: str, lang: Optional[str] = None) -> frozenset:
    """Frozenset of lowercase phrases from the given .voc file."""
    return _voc_set(name, (lang or DEFAULT_LANG).lower())
