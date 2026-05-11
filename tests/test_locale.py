"""Tests for `mediavocab.locale` — vocabulary loader and fallback chain."""
from mediavocab.locale import (
    _fallback_chain,
    get_default_lang,
    voc_regex,
    voc_set,
)


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------

def test_fallback_chain_full_locale():
    """A full locale falls back through language-only to en-us."""
    chain = _fallback_chain("pt-pt")
    assert chain[0] == "pt-pt"
    assert "pt" in chain
    assert "en-us" in chain
    # en-us must always be terminal
    assert chain[-1] == "en-us"


def test_fallback_chain_language_only():
    """A language-only code falls back directly to en-us."""
    chain = _fallback_chain("fr")
    assert chain[0] == "fr"
    assert "en-us" in chain


def test_fallback_chain_en_us_includes_self_first():
    """When 'en-us' is the active lang, it's first in the chain."""
    chain = _fallback_chain("en-us")
    assert chain[0] == "en-us"


# ---------------------------------------------------------------------------
# voc_regex / voc_set
# ---------------------------------------------------------------------------

def test_voc_regex_loads_english_keywords():
    """en-us has a rich .voc set; pick a known one."""
    rx = voc_regex("cut_directors", lang="en-us")
    assert rx is not None
    assert rx.search("Blade Runner: The Director's Cut")


def test_voc_regex_falls_back_to_en_us():
    """A locale without its own .voc file should fall back to en-us."""
    rx_pt = voc_regex("cut_directors", lang="pt-pt")
    # If pt-pt doesn't ship this file, falls back to en-us match.
    assert rx_pt is not None


def test_voc_regex_returns_none_for_unknown_voc():
    """An unknown .voc name returns None across every locale."""
    assert voc_regex("absolutely_nonexistent_voc_name") is None


def test_voc_set_lowercases():
    """voc_set lowercases all phrases."""
    s = voc_set("cut_directors", lang="en-us")
    assert all(p == p.lower() for p in s)


# ---------------------------------------------------------------------------
# get_default_lang
# ---------------------------------------------------------------------------

def test_get_default_lang_returns_string():
    lang = get_default_lang()
    assert isinstance(lang, str)
    assert lang == lang.lower()


# ---------------------------------------------------------------------------
# Cache behaviour (smoke)
# ---------------------------------------------------------------------------

def test_voc_regex_is_cached():
    """Calling voc_regex twice for the same (name, lang) returns the same
    compiled regex (LRU cache)."""
    rx1 = voc_regex("cut_directors", lang="en-us")
    rx2 = voc_regex("cut_directors", lang="en-us")
    assert rx1 is rx2
