"""Tests for `mediavocab.locale` — vocabulary loader backed by ovos-spec-tools."""
from mediavocab.locale import (
    get_default_lang,
    voc_regex,
    voc_set,
)


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
    # If pt-pt doesn't ship this file, falls back via ovos-spec-tools smart fallback.
    assert rx_pt is not None


def test_voc_regex_returns_none_for_unknown_voc():
    """An unknown .voc name returns None."""
    assert voc_regex("absolutely_nonexistent_voc_name") is None


def test_voc_set_lowercases():
    """voc_set lowercases all phrases."""
    s = voc_set("cut_directors", lang="en-us")
    assert all(p == p.lower() for p in s)


def test_voc_set_extended_edition():
    s = voc_set("cut_extended", lang="en-us")
    assert "extended cut" in s
    assert "special edition" in s


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
