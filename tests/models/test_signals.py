"""Tests for ``mediavocab.models.Signals`` + companions."""
import pytest

from mediavocab import (
    MediaType, Signals, SignalConflict, VariantKind,
)
from mediavocab.models.signals import (
    compare_signals, match_quality, merge_signals, signal_hash,
)


# ---------------------------------------------------------------------------
# compare_signals — overlapping disagreement only
# ---------------------------------------------------------------------------

def test_no_overlap_is_match():
    a = Signals(title="Inception")
    b = Signals(year=2010)
    assert compare_signals(a, b) == []


def test_title_fuzzy_below_threshold_conflicts():
    a = Signals(title="Inception")
    b = Signals(title="Interstellar")
    out = compare_signals(a, b)
    assert any(c.signal == "title" for c in out)


def test_title_fuzzy_above_threshold_matches():
    a = Signals(title="The Matrix")
    b = Signals(title="The Matrix.")  # punctuation only
    assert compare_signals(a, b) == []


def test_diacritic_fold_in_title():
    assert compare_signals(Signals(title="Café"), Signals(title="cafe")) == []
    assert compare_signals(Signals(title="Pokémon"), Signals(title="Pokemon")) == []


def test_year_outside_window_conflicts():
    out = compare_signals(Signals(year=2010), Signals(year=2015))
    assert len(out) == 1
    assert out[0].signal == "year"


def test_year_inside_window_matches():
    # default YEAR_WINDOW = 1
    assert compare_signals(Signals(year=2010), Signals(year=2011)) == []


def test_runtime_uses_per_media_tolerance():
    # EPISODIC_SERIES tolerance = 30s in mediavocab; same delta MUSIC = 3s ⇒ conflict
    same_delta_episodic = compare_signals(
        Signals(runtime=2400.0, medium=MediaType.EPISODIC_SERIES),
        Signals(runtime=2425.0, medium=MediaType.EPISODIC_SERIES),
    )
    assert same_delta_episodic == []
    same_delta_music = compare_signals(
        Signals(runtime=200.0, medium=MediaType.MUSIC),
        Signals(runtime=225.0, medium=MediaType.MUSIC),
    )
    assert any(c.signal == "runtime" for c in same_delta_music)


def test_medium_mismatch_conflicts():
    out = compare_signals(
        Signals(medium=MediaType.MOVIE),
        Signals(medium=MediaType.EPISODIC_SERIES),
    )
    assert any(c.signal == "medium" for c in out)


def test_country_case_insensitive():
    assert compare_signals(Signals(country="us"), Signals(country="US")) == []
    out = compare_signals(Signals(country="US"), Signals(country="GB"))
    assert any(c.signal == "country" for c in out)


def test_variant_kind_mismatch_conflicts():
    out = compare_signals(
        Signals(variant_kind=VariantKind.DIRECTORS),
        Signals(variant_kind=VariantKind.THEATRICAL),
    )
    assert any(c.signal == "variant_kind" for c in out)


def test_fanedit_subtype_mismatch_conflicts():
    out = compare_signals(
        Signals(fanedit_subtype="fanfix"),
        Signals(fanedit_subtype="fanmix"),
    )
    assert any(c.signal == "fanedit_subtype" for c in out)


# ---------------------------------------------------------------------------
# merge_signals — first-non-empty wins; content_genres unioned
# ---------------------------------------------------------------------------

def test_merge_first_non_empty_wins():
    a = Signals(title="A", year=2010)
    b = Signals(title="B", artist="x")
    out = merge_signals(a, b)
    assert out.title == "A"
    assert out.year == 2010
    assert out.artist == "x"


def test_merge_unions_content_genres():
    a = Signals(content_genres=["anime", "horror"])
    b = Signals(content_genres=["horror", "thriller"])
    out = merge_signals(a, b)
    assert out.content_genres == ["anime", "horror", "thriller"]


def test_merge_include_variants_or():
    assert merge_signals(Signals(), Signals(include_variants=True)).include_variants is True
    assert merge_signals(Signals(), Signals()).include_variants is False


# ---------------------------------------------------------------------------
# match_quality
# ---------------------------------------------------------------------------

def test_match_quality_perfect():
    a = Signals(title="Inception", year=2010, medium=MediaType.MOVIE)
    assert match_quality(a, a) == 1.0


def test_match_quality_year_mismatch_halves():
    a = Signals(title="X", year=2010, medium=MediaType.MOVIE)
    b = Signals(title="X", year=2020, medium=MediaType.MOVIE)
    assert match_quality(a, b) == 0.5


def test_match_quality_medium_mismatch_halves():
    a = Signals(title="X", medium=MediaType.MOVIE)
    b = Signals(title="X", medium=MediaType.EPISODIC_SERIES)
    assert match_quality(a, b) == 0.5


def test_match_quality_unknown_fields_dont_penalise():
    assert match_quality(Signals(), Signals(title="X")) == 1.0


# ---------------------------------------------------------------------------
# signal_hash — stable across identical inputs, distinct across non-identical
# ---------------------------------------------------------------------------

def test_signal_hash_stable():
    a = Signals(title="Inception", year=2010, medium=MediaType.MOVIE)
    assert signal_hash(a) == signal_hash(a.model_copy(deep=True))


def test_signal_hash_distinct_on_year():
    a = Signals(title="X", year=2010)
    b = Signals(title="X", year=2011)
    assert signal_hash(a) != signal_hash(b)


def test_signal_hash_normalises_title():
    """Whitespace and case in title shouldn't affect the hash."""
    assert signal_hash(Signals(title="The Matrix")) == signal_hash(Signals(title="the   matrix"))


def test_signal_hash_distinct_on_fanedit_subtype():
    a = Signals(title="X", fanedit_subtype="fanfix")
    b = Signals(title="X", fanedit_subtype="fanmix")
    assert signal_hash(a) != signal_hash(b)
