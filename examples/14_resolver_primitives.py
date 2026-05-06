"""The resolver primitives: ``Signals``, ``ExternalIds``, ``Stream``,
``MetadataProvider`` Protocol.

These let any cross-source resolver share the same disambiguation bag,
typed external-id model, stream extraction, and provider contract.
"""
from __future__ import annotations

from typing import ClassVar, Optional, Set

from mediavocab import (
    ExternalIds,
    MediaType,
    MetadataProvider,
    ProviderMatch,
    Signals,
    Stream,
    VariantKind,
)
from mediavocab.models.protocols import provider_matches
from mediavocab.models.signals import (
    compare_signals,
    match_quality,
    merge_signals,
    signal_hash,
)
from mediavocab.text import isbn10_to_13, normalize_isbn, release_hash


# ---------------------------------------------------------------------------
# 1. Signals — the disambiguation bag
# ---------------------------------------------------------------------------

local = Signals(
    title="Blade Runner",
    year=1982,
    medium=MediaType.MOVIE,
    variant_kind=VariantKind.DIRECTORS,
)

candidate_a = Signals(title="Blade Runner", year=1982, medium=MediaType.MOVIE,
                      variant_kind=VariantKind.THEATRICAL)
candidate_b = Signals(title="Blade Runner", year=1982, medium=MediaType.MOVIE,
                      variant_kind=VariantKind.DIRECTORS)

print("=== compare_signals ===")
print(f"  vs theatrical: {[c.signal for c in compare_signals(local, candidate_a)]}")
print(f"  vs directors : {[c.signal for c in compare_signals(local, candidate_b)]}")

print("\n=== match_quality ===")
print(f"  perfect match: {match_quality(local, candidate_b):.2f}")
print(f"  variant mismatch: {match_quality(local, candidate_a):.2f}")

print("\n=== merge_signals (first non-empty wins) ===")
partial1 = Signals(title="X", year=2010)
partial2 = Signals(title="Y", country="US", content_genres=["sci_fi"])
merged = merge_signals(partial1, partial2)
print(f"  title: {merged.title}  year: {merged.year}  country: {merged.country}")
print(f"  genres: {merged.content_genres}")


# ---------------------------------------------------------------------------
# 2. ExternalIds — typed model with ISBN auto-pairing
# ---------------------------------------------------------------------------

print("\n=== ExternalIds ISBN auto-pairing ===")
ids_a = ExternalIds(isbn_10="0-261-10328-8")
print(f"  isbn_10: {ids_a.isbn_10}")
print(f"  isbn_13 (back-filled): {ids_a.isbn_13}")
print(f"  manual conversion: {isbn10_to_13(ids_a.isbn_10)}")
print(f"  normalize_isbn('978 0 261 10328 3'): {normalize_isbn('978 0 261 10328 3')}")

print("\n=== ExternalIds first-writer-wins merge ===")
strong = ExternalIds(imdb="tt0083658", tmdb_movie=78,
                      extra={"k": "from-strong"})
weak   = ExternalIds(imdb="tt0000000", wikidata="Q3361")
merged_ids = strong.merge(weak)
print(f"  imdb (strong wins): {merged_ids.imdb}")
print(f"  tmdb (only on strong): {merged_ids.tmdb_movie}")
print(f"  wikidata (only on weak — filled): {merged_ids.wikidata}")


# ---------------------------------------------------------------------------
# 3. Stream — typed playable streams from extra IDs
# ---------------------------------------------------------------------------

print("\n=== ExternalIds.streams expansion ===")
ids = ExternalIds(extra={
    "youtube_video_id": "dQw4w9WgXcQ",
    "bandcamp_track_url": "https://example.bandcamp.com/track/x",
})
for s in ids.streams:
    assert isinstance(s, Stream)
    print(f"  [{s.platform:12}] {s.media_type:8}  {s.url}")


# ---------------------------------------------------------------------------
# 4. MetadataProvider Protocol — typed contract, no inheritance required
# ---------------------------------------------------------------------------

class FakeAnimeProvider:
    """Anime / manga provider — gates on (media_type, content_genres).

    No base class. ``isinstance(p, MetadataProvider)`` works via the
    runtime-checkable Protocol.
    """

    name: ClassVar[str] = "fake_anime"
    media: ClassVar[Set[MediaType]] = {MediaType.EPISODIC_SERIES, MediaType.MOVIE}
    genre_filter: ClassVar[Set[str]] = {"anime"}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        if not provider_matches(self, signals):
            return None
        return ProviderMatch(
            provider=self.name,
            confidence=0.9,
            signals=signals.model_copy(update={"year": 1998}),
            external_ids=ExternalIds(anilist_id=1, mal_id=1),
        )

    def matches(self, signals: Signals) -> bool:
        return provider_matches(self, signals)


provider = FakeAnimeProvider()
print("\n=== MetadataProvider Protocol ===")
print(f"  isinstance(p, MetadataProvider): {isinstance(provider, MetadataProvider)}")

# Right media + right genre → match.
right = Signals(title="Cowboy Bebop", medium=MediaType.EPISODIC_SERIES,
                content_genres=["anime"])
match = provider.lookup(right)
print(f"  on anime EPISODIC_SERIES → {match.provider} (year={match.signals.year})")

# Wrong genre → no match.
wrong = Signals(title="The Office", medium=MediaType.EPISODIC_SERIES)
print(f"  on non-anime EPISODIC_SERIES → {provider.lookup(wrong)}")


# ---------------------------------------------------------------------------
# 5. release_hash — per-edition dedup
# ---------------------------------------------------------------------------

from mediavocab import Release, Work, StreamMode

br_work = Work(title="Blade Runner", media_type=MediaType.MOVIE,
               year=1982, runtime=117 * 60.0)
theatrical = Release(work=br_work, container="Blu-ray", region="US")
directors  = Release(work=br_work, container="Blu-ray", region="US",
                     variant_kind=VariantKind.DIRECTORS)
mirror     = Release(work=br_work, container="Blu-ray", region="US",
                     uri="x://mirror1")  # different URI, same edition

print("\n=== release_hash (per-edition dedup) ===")
print(f"  theatrical : {release_hash(theatrical)}")
print(f"  directors  : {release_hash(directors)}")
print(f"  mirror     : {release_hash(mirror)}")
print(f"  theatrical == mirror? {release_hash(theatrical) == release_hash(mirror)}")
print(f"  theatrical == directors? {release_hash(theatrical) == release_hash(directors)}")


# ---------------------------------------------------------------------------
# 6. signal_hash — canonical-id seed for resolvers
# ---------------------------------------------------------------------------

print("\n=== signal_hash (canonical-id seed) ===")
print(f"  '{local.title}' Director's Cut → {signal_hash(local)}")
print(f"  Same with whitespace      → {signal_hash(local.model_copy(update={'title': '  Blade  Runner  '}))}")
