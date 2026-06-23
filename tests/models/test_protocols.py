"""Tests for ``mediavocab.models.protocols``."""
from typing import ClassVar, Optional, Set

from mediavocab import (
    MediaType, MetadataProvider, PlaybackType, ProviderMatch,
    ResolutionConflict, Signals,
)
from mediavocab.models.protocols import provider_matches


# ---------------------------------------------------------------------------
# Concrete providers — subclass the ABC.
# ---------------------------------------------------------------------------

class _AnimeOnlyProvider(MetadataProvider):
    name: ClassVar[str] = "anime_only"
    media: ClassVar[Set[MediaType]] = {MediaType.EPISODIC_SERIES, MediaType.MOVIE}
    genre_filter: ClassVar[Set[str]] = {"anime"}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        return ProviderMatch(provider=self.name, confidence=1.0,
                             signals=signals)


class _UniversalProvider(MetadataProvider):
    name: ClassVar[str] = "universal"

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        return None


# ---------------------------------------------------------------------------
# ABC enforcement
# ---------------------------------------------------------------------------

def test_concrete_provider_is_metadata_provider():
    assert isinstance(_AnimeOnlyProvider(), MetadataProvider)
    assert isinstance(_UniversalProvider(), MetadataProvider)


def test_abc_blocks_unimplemented_subclass():
    import pytest

    class _Broken(MetadataProvider):
        name = "broken"

    with pytest.raises(TypeError):
        _Broken()


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
# matches() — default four-axis routing
# ---------------------------------------------------------------------------

def test_universal_matches_anything():
    p = _UniversalProvider()
    assert p.matches(Signals(medium=MediaType.MOVIE)) is True
    assert p.matches(Signals(medium=MediaType.MUSIC)) is True
    assert p.matches(Signals()) is True


def test_anime_provider_requires_genre():
    p = _AnimeOnlyProvider()
    assert p.matches(Signals(
        medium=MediaType.EPISODIC_SERIES, content_genres=["anime"])) is True
    assert p.matches(Signals(medium=MediaType.EPISODIC_SERIES)) is False
    assert p.matches(Signals(medium=MediaType.MOVIE, content_genres=["anime"])) is True
    assert p.matches(Signals(medium=MediaType.MUSIC, content_genres=["anime"])) is False


def test_unknown_medium_passes_media_gate():
    p = _AnimeOnlyProvider()
    assert p.matches(Signals(content_genres=["anime"])) is True


def test_genre_filter_with_partial_overlap():
    p = _AnimeOnlyProvider()
    assert p.matches(Signals(
        medium=MediaType.MOVIE,
        content_genres=["anime", "horror"])) is True


def test_provider_matches_alias():
    p = _AnimeOnlyProvider()
    sig = Signals(medium=MediaType.MOVIE, content_genres=["anime"])
    assert provider_matches(p, sig) == p.matches(sig)


# ---------------------------------------------------------------------------
# Four-axis gate — playback_type
# ---------------------------------------------------------------------------

class _AudioOnlyProvider(MetadataProvider):
    name = "audio_only"
    playback_type = {PlaybackType.AUDIO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return None


class _VideoOnlyProvider(MetadataProvider):
    name = "video_only"
    playback_type = {PlaybackType.VIDEO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return None


def test_playback_gate_filters_video_from_audio_provider():
    p = _AudioOnlyProvider()
    assert p.matches(Signals(playback_type=PlaybackType.AUDIO)) is True
    assert p.matches(Signals(playback_type=PlaybackType.VIDEO)) is False


def test_playback_none_passes_gate():
    p = _AudioOnlyProvider()
    assert p.matches(Signals(medium=MediaType.MUSIC)) is True


def test_universal_provider_accepts_all_playback_types():
    p = _UniversalProvider()
    for pt in PlaybackType:
        assert p.matches(Signals(playback_type=pt)) is True


def test_playback_orthogonal_to_media_gate():
    p = _VideoOnlyProvider()
    p.media = {MediaType.MOVIE}     # type: ignore[misc]
    try:
        assert p.matches(Signals(medium=MediaType.MUSIC,
                                 playback_type=PlaybackType.VIDEO)) is False
        assert p.matches(Signals(medium=MediaType.MOVIE,
                                 playback_type=PlaybackType.VIDEO)) is True
        assert p.matches(Signals(medium=MediaType.MOVIE,
                                 playback_type=PlaybackType.AUDIO)) is False
    finally:
        p.media = set()              # type: ignore[misc]


# ---------------------------------------------------------------------------
# ContentForm gate
# ---------------------------------------------------------------------------


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
