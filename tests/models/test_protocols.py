"""Tests for ``mediavocab.models.protocols``."""
from typing import ClassVar, Optional, Set

from mediavocab import (
    MediaType, MetadataProvider, ProviderMatch, ResolutionConflict,
    Signals,
)
from mediavocab.models.protocols import provider_matches


# ---------------------------------------------------------------------------
# Concrete providers — exercise the Protocol surface without inheritance
# ---------------------------------------------------------------------------

class _AnimeOnlyProvider:
    name: ClassVar[str] = "anime_only"
    media: ClassVar[Set[MediaType]] = {MediaType.EPISODIC_SERIES, MediaType.MOVIE}
    genre_filter: ClassVar[Set[str]] = {"anime"}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        return ProviderMatch(provider=self.name, confidence=1.0,
                             signals=signals)

    def matches(self, signals: Signals) -> bool:
        return provider_matches(self, signals)


class _UniversalProvider:
    name: ClassVar[str] = "universal"
    media: ClassVar[Set[MediaType]] = set()
    genre_filter: ClassVar[Set[str]] = set()

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        return None

    def matches(self, signals: Signals) -> bool:
        return provider_matches(self, signals)


# ---------------------------------------------------------------------------
# runtime_checkable Protocol
# ---------------------------------------------------------------------------

def test_concrete_provider_is_metadata_provider():
    """No inheritance required — duck typing via Protocol."""
    assert isinstance(_AnimeOnlyProvider(), MetadataProvider)
    assert isinstance(_UniversalProvider(), MetadataProvider)


def test_provider_match_default_factory():
    pm = ProviderMatch(provider="x", confidence=0.5)
    assert pm.signals == Signals()
    assert pm.external_ids.is_empty()


def test_provider_match_confidence_bounds():
    import pytest
    with pytest.raises(Exception):
        ProviderMatch(provider="x", confidence=1.5)
    with pytest.raises(Exception):
        ProviderMatch(provider="x", confidence=-0.1)


# ---------------------------------------------------------------------------
# provider_matches — reference dispatcher gate
# ---------------------------------------------------------------------------

def test_universal_matches_anything():
    p = _UniversalProvider()
    assert provider_matches(p, Signals(medium=MediaType.MOVIE)) is True
    assert provider_matches(p, Signals(medium=MediaType.MUSIC)) is True
    assert provider_matches(p, Signals()) is True


def test_anime_provider_requires_genre():
    p = _AnimeOnlyProvider()
    # Right media + right genre → match.
    assert provider_matches(p, Signals(
        medium=MediaType.EPISODIC_SERIES, content_genres=["anime"])) is True
    # Right media but no genre tag → no match.
    assert provider_matches(p, Signals(
        medium=MediaType.EPISODIC_SERIES)) is False
    # Wrong media → no match.
    assert provider_matches(p, Signals(
        medium=MediaType.MOVIE, content_genres=["anime"])) is True   # MOVIE is in media set
    assert provider_matches(p, Signals(
        medium=MediaType.MUSIC, content_genres=["anime"])) is False


def test_unknown_medium_passes_media_gate():
    """When ``signals.medium`` is None the media gate is skipped."""
    p = _AnimeOnlyProvider()
    assert provider_matches(p, Signals(content_genres=["anime"])) is True


def test_genre_filter_with_partial_overlap():
    """Any tag in the filter present in content_genres → match."""
    p = _AnimeOnlyProvider()
    assert provider_matches(p, Signals(
        medium=MediaType.MOVIE,
        content_genres=["anime", "horror"])) is True


# ---------------------------------------------------------------------------
# ResolutionConflict
# ---------------------------------------------------------------------------

def test_resolution_conflict_default_fields():
    rc = ResolutionConflict(provider="x", against="local")
    assert rc.fields == []


def test_resolution_conflict_with_field_list():
    from mediavocab import SignalConflict
    rc = ResolutionConflict(
        provider="x",
        against="anchor",
        fields=[SignalConflict(signal="year", ours=2010, theirs=2020)],
    )
    assert rc.fields[0].signal == "year"
