"""Tests for `MergeStrategy`, `IdentityConflict`, and §6.6 contract rules."""
import pytest

from mediavocab import MediaType, ReleaseStatus, Work
from mediavocab.text import (
    DEFAULT_STRATEGY,
    IdentityConflict,
    MergeStrategy,
    merge,
)


# ---------------------------------------------------------------------------
# MergeStrategy — defaults
# ---------------------------------------------------------------------------

def test_default_strategy_defaults():
    """Spec §6.6 — title 'longest', edition 'first', no priority."""
    s = MergeStrategy()
    assert s.title_strategy == "longest"
    assert s.edition_strategy == "first"
    assert s.provider_priority == []


# ---------------------------------------------------------------------------
# title_strategy
# ---------------------------------------------------------------------------

def test_title_strategy_longest_picks_longer():
    """Default ('longest') recovers the fuller title from abbreviated providers."""
    a = Work(title="Inception", media_type=MediaType.MOVIE)
    b = Work(title="Inception: The Full Title", media_type=MediaType.MOVIE)
    m = merge(a, b)
    assert m.title == "Inception: The Full Title"


def test_title_strategy_first_keeps_first():
    a = Work(title="Inception", media_type=MediaType.MOVIE)
    b = Work(title="Inception: The Full Title", media_type=MediaType.MOVIE)
    m = merge(a, b, strategy=MergeStrategy(title_strategy="first"))
    assert m.title == "Inception"


def test_title_strategy_handles_empty_titles():
    """A non-empty incoming title fills an (impossibly) empty base."""
    # title is required at construction so we exercise via model_copy.
    a = Work(title="x", media_type=MediaType.MOVIE).model_copy(update={"title": ""})
    b = Work(title="The Real Title", media_type=MediaType.MOVIE)
    m = merge(a, b)
    assert m.title == "The Real Title"


# ---------------------------------------------------------------------------
# edition_strategy — default 'first'
# ---------------------------------------------------------------------------

def test_edition_strategy_first_keeps_first():
    a = Work(title="x", media_type=MediaType.MOVIE, edition="Criterion")
    b = Work(title="x", media_type=MediaType.MOVIE, edition="Anniversary")
    m = merge(a, b)
    assert m.edition == "Criterion"   # first non-empty wins


def test_edition_strategy_longest():
    a = Work(title="x", media_type=MediaType.MOVIE, edition="Criterion")
    b = Work(title="x", media_type=MediaType.MOVIE, edition="Anniversary Edition")
    m = merge(a, b, strategy=MergeStrategy(edition_strategy="longest"))
    assert m.edition == "Anniversary Edition"


# ---------------------------------------------------------------------------
# release_status collapse (spec §6.6 rule 5)
# ---------------------------------------------------------------------------

def test_release_status_collapses_to_highest_confidence():
    """RELEASED > WITHDRAWN > ANNOUNCED > IN_PRODUCTION > CANCELLED > UNKNOWN."""
    a = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.IN_PRODUCTION)
    b = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.RELEASED)
    m = merge(a, b)
    assert m.release_status == ReleaseStatus.RELEASED


def test_release_status_keeps_higher_when_already_higher():
    a = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.WITHDRAWN)
    b = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.UNKNOWN)
    m = merge(a, b)
    assert m.release_status == ReleaseStatus.WITHDRAWN


def test_release_status_announced_beats_in_production():
    a = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.IN_PRODUCTION)
    b = Work(title="x", media_type=MediaType.MOVIE,
             release_status=ReleaseStatus.ANNOUNCED)
    m = merge(a, b)
    assert m.release_status == ReleaseStatus.ANNOUNCED


# ---------------------------------------------------------------------------
# Identity conflict (strict mode)
# ---------------------------------------------------------------------------

def test_strict_merge_raises_on_year_conflict():
    a = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
    b = Work(title="Inception", media_type=MediaType.MOVIE, year=1999)
    with pytest.raises(IdentityConflict) as exc_info:
        merge(a, b, strict=True)
    assert exc_info.value.field == "year"
    assert 2010 in exc_info.value.values
    assert 1999 in exc_info.value.values


def test_strict_merge_raises_on_media_type_conflict():
    a = Work(title="Hotline", media_type=MediaType.MUSIC)
    b = Work(title="Hotline", media_type=MediaType.MOVIE)
    with pytest.raises(IdentityConflict) as exc_info:
        merge(a, b, strict=True)
    assert exc_info.value.field == "media_type"


def test_strict_merge_passes_when_identity_agrees():
    """Identical identity fields — no exception, normal merge."""
    a = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
             content_genres=["sci_fi"])
    b = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
             content_genres=["thriller"])
    m = merge(a, b, strict=True)
    assert set(m.content_genres) == {"sci_fi", "thriller"}


def test_loose_merge_does_not_raise_on_year_conflict():
    """Default `strict=False` — first non-empty year wins, no exception."""
    a = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
    b = Work(title="Inception", media_type=MediaType.MOVIE, year=1999)
    m = merge(a, b)   # no IdentityConflict
    assert m.year == 2010


def test_identity_conflict_message_is_informative():
    a = Work(title="x", media_type=MediaType.MOVIE, year=2010)
    b = Work(title="x", media_type=MediaType.MOVIE, year=2020)
    with pytest.raises(IdentityConflict, match="year"):
        merge(a, b, strict=True)


# ---------------------------------------------------------------------------
# IdentityConflict is a ValueError (for callers that catch ValueError)
# ---------------------------------------------------------------------------

def test_identity_conflict_is_value_error():
    """IdentityConflict subclasses ValueError so generic try/except works."""
    a = Work(title="x", media_type=MediaType.MOVIE, year=2010)
    b = Work(title="x", media_type=MediaType.MOVIE, year=2020)
    with pytest.raises(ValueError):
        merge(a, b, strict=True)


# ---------------------------------------------------------------------------
# Top-level re-exports (spec §6.6 names accessible from mediavocab)
# ---------------------------------------------------------------------------

def test_mergestrategy_importable_from_top_level():
    import mediavocab
    assert mediavocab.MergeStrategy is MergeStrategy
    assert mediavocab.IdentityConflict is IdentityConflict
    assert mediavocab.DEFAULT_STRATEGY is DEFAULT_STRATEGY


def test_country_slot_importable_from_text():
    from mediavocab.text import country_slot
    from mediavocab import MediaType, Work
    w = Work(title="x", media_type=MediaType.MUSIC, publication_country="GB")
    assert country_slot(w) == "GB"
