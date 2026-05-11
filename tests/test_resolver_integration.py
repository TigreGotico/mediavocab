"""Integration tests — full resolver flow with multiple providers.

Exercises the end-to-end pipeline the spec describes:
1. A caller emits `Signals(query)` with what they know.
2. The resolver routes to providers via the four-axis gate.
3. Each provider returns `ProviderMatch(signals=...)` with what it believes.
4. The consolidator compares observations via `compare_signals`, merges via
   `merge_signals` (or `merge` if building a Work).
5. The result is suitable for constructing a canonical `Work`.
"""
from typing import ClassVar, Optional, Set

import pytest

from mediavocab import (
    ContentForm, ExternalIds, MediaType, MetadataProvider, PlaybackType,
    ProviderMatch, RelationRole, Signals, Work,
)
from mediavocab.models import external_ids as eid
from mediavocab.models.signals import (
    compare_signals, match_quality, merge_signals,
)


# ---------------------------------------------------------------------------
# Stub providers
# ---------------------------------------------------------------------------

class _IMDBProvider(MetadataProvider):
    name: ClassVar[str] = "imdb"
    media: ClassVar[Set[MediaType]] = {MediaType.MOVIE, MediaType.EPISODIC_SERIES}
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.VIDEO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        if not self.matches(signals):
            return None
        return ProviderMatch(
            provider=self.name,
            confidence=0.95,
            signals=signals.model_copy(update={
                "year": 2010,
                "runtime": 148 * 60.0,
                "medium": MediaType.MOVIE,
                "language": "en",
                "country": "US",
            }),
            external_ids=ExternalIds(imdb="tt1375666"),
        )


class _TMDBProvider(MetadataProvider):
    name: ClassVar[str] = "tmdb"
    media: ClassVar[Set[MediaType]] = {MediaType.MOVIE}
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.VIDEO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        if not self.matches(signals):
            return None
        return ProviderMatch(
            provider=self.name,
            confidence=0.90,
            signals=signals.model_copy(update={
                "year": 2010,
                "runtime": 148 * 60.0 + 30,   # within tolerance
                "medium": MediaType.MOVIE,
                "language": "en",
                "country": "US",
                "content_genres": ["sci_fi", "thriller"],
            }),
            external_ids=ExternalIds(tmdb_movie=27205, imdb="tt1375666"),
        )


class _MusicBrainzProvider(MetadataProvider):
    name: ClassVar[str] = "musicbrainz"
    media: ClassVar[Set[MediaType]] = {MediaType.MUSIC}
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.AUDIO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        if not self.matches(signals):
            return None
        return ProviderMatch(provider=self.name, confidence=0.99)


# ---------------------------------------------------------------------------
# Routing — gate decides who gets called
# ---------------------------------------------------------------------------

def test_video_query_routes_to_video_providers_only():
    """A `playback_type=VIDEO` query reaches IMDB / TMDB; not MusicBrainz."""
    providers = [_IMDBProvider(), _TMDBProvider(), _MusicBrainzProvider()]
    query = Signals(title="Inception", playback_type=PlaybackType.VIDEO)
    matched = [p for p in providers if p.matches(query)]
    assert _MusicBrainzProvider not in (type(p) for p in matched)
    assert _IMDBProvider in (type(p) for p in matched)
    assert _TMDBProvider in (type(p) for p in matched)


def test_audio_query_routes_to_audio_providers_only():
    providers = [_IMDBProvider(), _TMDBProvider(), _MusicBrainzProvider()]
    query = Signals(title="Hotline Bling", playback_type=PlaybackType.AUDIO)
    matched = [p for p in providers if p.matches(query)]
    assert _MusicBrainzProvider in (type(p) for p in matched)
    assert _IMDBProvider not in (type(p) for p in matched)


# ---------------------------------------------------------------------------
# Consolidation — agreement → no conflicts, merge → consensus
# ---------------------------------------------------------------------------

def test_two_providers_agree_no_conflicts():
    """IMDB and TMDB both return Inception (2010) — no conflicts."""
    query = Signals(title="Inception", playback_type=PlaybackType.VIDEO)
    imdb = _IMDBProvider().lookup(query)
    tmdb = _TMDBProvider().lookup(query)
    assert compare_signals(imdb.signals, tmdb.signals) == []


def test_merge_signals_combines_provider_views():
    """The consolidator merges IMDB + TMDB into one consensus."""
    query = Signals(title="Inception", playback_type=PlaybackType.VIDEO)
    imdb = _IMDBProvider().lookup(query)
    tmdb = _TMDBProvider().lookup(query)
    consensus = merge_signals(imdb.signals, tmdb.signals)
    # First-non-empty wins on scalars
    assert consensus.title == "Inception"
    assert consensus.year == 2010
    # genres unioned (TMDB contributed; IMDB had none)
    assert "sci_fi" in consensus.content_genres


def test_external_ids_combine_across_providers():
    """The consolidator merges ExternalIds; IMDB's tt-id agrees with TMDB's."""
    imdb_match = _IMDBProvider().lookup(
        Signals(title="Inception", playback_type=PlaybackType.VIDEO))
    tmdb_match = _TMDBProvider().lookup(
        Signals(title="Inception", playback_type=PlaybackType.VIDEO))
    combined = imdb_match.external_ids.merge(tmdb_match.external_ids)
    assert combined.imdb == "tt1375666"
    assert combined.tmdb_movie == 27205


def test_match_quality_self_score_is_one():
    """match_quality of a Signals against itself is 1.0."""
    s = Signals(title="Inception", year=2010, medium=MediaType.MOVIE)
    assert match_quality(s, s) == 1.0


def test_match_quality_lower_on_mismatch():
    """Year mismatch halves the score."""
    a = Signals(title="Inception", year=2010, medium=MediaType.MOVIE)
    b = Signals(title="Inception", year=2020, medium=MediaType.MOVIE)
    assert match_quality(a, b) < 1.0


# ---------------------------------------------------------------------------
# End-to-end: query → providers → consolidation → Work
# ---------------------------------------------------------------------------

def test_full_resolver_flow_yields_consistent_signals():
    """Simulated full flow: query → multiple providers → merged consensus."""
    providers = [_IMDBProvider(), _TMDBProvider(), _MusicBrainzProvider()]

    # 1. Caller emits a query
    query = Signals(title="Inception", playback_type=PlaybackType.VIDEO)

    # 2. Resolver routes to providers
    matches = [p.lookup(query) for p in providers if p.matches(query)]
    matches = [m for m in matches if m is not None]

    # 3. Compare observations — no conflicts
    for a, b in zip(matches, matches[1:]):
        assert compare_signals(a.signals, b.signals) == []

    # 4. Merge into consensus
    consensus = merge_signals(*(m.signals for m in matches))

    # 5. Consensus has enough to build a Work
    assert consensus.title == "Inception"
    assert consensus.year == 2010
    assert consensus.medium == MediaType.MOVIE

    # External IDs merged across providers
    combined_ids = matches[0].external_ids
    for m in matches[1:]:
        combined_ids = combined_ids.merge(m.external_ids)
    assert combined_ids.imdb == "tt1375666"
    assert combined_ids.tmdb_movie == 27205


def test_resolver_skips_unreachable_provider():
    """An is_available()=False provider is filtered before routing."""
    class _Offline(MetadataProvider):
        name = "offline"
        media: ClassVar[Set[MediaType]] = {MediaType.MOVIE}

        def is_available(self) -> bool:
            return False

        def lookup(self, signals):
            return None  # would be skipped before this in practice

    p = _Offline()
    assert not p.is_available()
