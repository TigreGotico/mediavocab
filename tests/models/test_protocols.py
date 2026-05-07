"""Tests for ``mediavocab.models.protocols``."""
from typing import ClassVar, Optional, Set

from mediavocab import (
    MediaType, MetadataProvider, PlaybackModality, ProviderMatch,
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
    """Subclassing the ABC is the canonical way."""
    assert isinstance(_AnimeOnlyProvider(), MetadataProvider)
    assert isinstance(_UniversalProvider(), MetadataProvider)


def test_abc_blocks_unimplemented_subclass():
    """Forgetting an abstract method raises at instantiation."""
    import pytest

    class _Broken(MetadataProvider):
        name = "broken"
        # Intentionally missing is_available + lookup.

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
# matches() — default two-axis routing
# ---------------------------------------------------------------------------

def test_universal_matches_anything():
    p = _UniversalProvider()
    assert p.matches(Signals(medium=MediaType.MOVIE)) is True
    assert p.matches(Signals(medium=MediaType.MUSIC)) is True
    assert p.matches(Signals()) is True


def test_anime_provider_requires_genre():
    p = _AnimeOnlyProvider()
    # Right media + right genre → match.
    assert p.matches(Signals(
        medium=MediaType.EPISODIC_SERIES, content_genres=["anime"])) is True
    # Right media but no genre tag → no match.
    assert p.matches(Signals(
        medium=MediaType.EPISODIC_SERIES)) is False
    # MOVIE is in the media set; needs the genre tag too.
    assert p.matches(Signals(
        medium=MediaType.MOVIE, content_genres=["anime"])) is True
    # Wrong media → no match.
    assert p.matches(Signals(
        medium=MediaType.MUSIC, content_genres=["anime"])) is False


def test_unknown_medium_passes_media_gate():
    """When ``signals.medium`` is None the media gate is skipped."""
    p = _AnimeOnlyProvider()
    assert p.matches(Signals(content_genres=["anime"])) is True


def test_genre_filter_with_partial_overlap():
    """Any tag in the filter present in content_genres → match."""
    p = _AnimeOnlyProvider()
    assert p.matches(Signals(
        medium=MediaType.MOVIE,
        content_genres=["anime", "horror"])) is True


def test_provider_matches_alias():
    """``provider_matches(p, sig)`` aliases ``p.matches(sig)``."""
    p = _AnimeOnlyProvider()
    sig = Signals(medium=MediaType.MOVIE, content_genres=["anime"])
    assert provider_matches(p, sig) == p.matches(sig)


# ---------------------------------------------------------------------------
# Three-axis gate — modality
# ---------------------------------------------------------------------------

class _AudioOnlyProvider(MetadataProvider):
    name = "audio_only"
    modality = {PlaybackModality.AUDIO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return None


class _VideoOnlyProvider(MetadataProvider):
    name = "video_only"
    modality = {PlaybackModality.VIDEO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return None


def test_modality_gate_filters_video_from_audio_provider():
    p = _AudioOnlyProvider()
    assert p.matches(Signals(modality=PlaybackModality.AUDIO)) is True
    assert p.matches(Signals(modality=PlaybackModality.VIDEO)) is False


def test_modality_none_passes_modality_gate():
    """No hint ⇒ no gate. The caller didn't constrain modality."""
    p = _AudioOnlyProvider()
    assert p.matches(Signals(medium=MediaType.MUSIC)) is True


def test_modality_universal_provider_accepts_all():
    p = _UniversalProvider()
    for m in PlaybackModality:
        assert p.matches(Signals(modality=m)) is True


def test_modality_orthogonal_to_media_gate():
    """media gate fails first ⇒ never reaches modality check."""
    p = _VideoOnlyProvider()
    p.media = {MediaType.MOVIE}     # type: ignore[misc]
    try:
        # Wrong media: rejected even though modality matches.
        assert p.matches(Signals(medium=MediaType.MUSIC,
                                 modality=PlaybackModality.VIDEO)) is False
        # Right media + right modality: accepted.
        assert p.matches(Signals(medium=MediaType.MOVIE,
                                 modality=PlaybackModality.VIDEO)) is True
        # Right media but wrong modality: rejected.
        assert p.matches(Signals(medium=MediaType.MOVIE,
                                 modality=PlaybackModality.AUDIO)) is False
    finally:
        p.media = set()              # type: ignore[misc]


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
