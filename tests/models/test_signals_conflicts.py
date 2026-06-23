"""Tests for `compare_signals` — one test per conflict-emitting branch."""
from mediavocab import MediaType, Signals, VariantKind
from mediavocab.models.signals import compare_signals


def _f(s):
    return {c.signal for c in s}


def test_artist_mismatch():
    a = Signals(artist="Drake")
    b = Signals(artist="Adele")
    assert "artist" in _f(compare_signals(a, b))


def test_season_mismatch():
    a = Signals(season=1)
    b = Signals(season=2)
    assert "season" in _f(compare_signals(a, b))


def test_episode_mismatch():
    a = Signals(episode=3)
    b = Signals(episode=7)
    assert "episode" in _f(compare_signals(a, b))


def test_medium_mismatch():
    a = Signals(medium=MediaType.MOVIE)
    b = Signals(medium=MediaType.MUSIC)
    assert "medium" in _f(compare_signals(a, b))


def test_language_mismatch():
    a = Signals(language="en")
    b = Signals(language="fr")
    assert "language" in _f(compare_signals(a, b))


def test_variant_kind_mismatch():
    a = Signals(variant_kind=VariantKind.DIRECTORS)
    b = Signals(variant_kind=VariantKind.THEATRICAL)
    assert "variant_kind" in _f(compare_signals(a, b))


def test_region_mismatch():
    a = Signals(region="US")
    b = Signals(region="JP")
    assert "region" in _f(compare_signals(a, b))


def test_source_format_mismatch():
    a = Signals(source_format="35mm")
    b = Signals(source_format="DAB")
    assert "source_format" in _f(compare_signals(a, b))


def test_edition_mismatch():
    a = Signals(edition="Criterion")
    b = Signals(edition="Anniversary")
    assert "edition" in _f(compare_signals(a, b))


def test_fanedit_subtype_mismatch():
    a = Signals(fanedit_subtype="fanfix")
    b = Signals(fanedit_subtype="fanmix")
    assert "fanedit_subtype" in _f(compare_signals(a, b))


def test_country_mismatch():
    a = Signals(country="US")
    b = Signals(country="GB")
    assert "country" in _f(compare_signals(a, b))
