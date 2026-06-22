"""Signals — the three pipeline roles (spec §5.10).

Same shape, three different jobs distinguished by direction of flow:

1. **Query** (``Signals.as_query()``) — caller fills it in, passes to the resolver.
2. **Observation** (``Signals.as_observation()``) — the provider re-emits a Signals
   on ``ProviderMatch.signals`` describing what it believes the work is.
3. **Result** (``signals.as_result()``) — the consolidator marks the merged
   consensus as a result; not a Work (no canonical hash, no credits, no tracklist).

Use ``SignalsRole`` to inspect or assert which lifecycle phase a Signals bag is in.
"""
from typing import ClassVar
from mediavocab import (
    MediaType, MetadataProvider, ProviderMatch, Signals, SignalsRole,
)
from mediavocab.models import ExternalIds
from mediavocab.models.signals import compare_signals, merge_signals


# A toy provider that "observes" signals from a Wikipedia-shaped row.
class ToyProvider(MetadataProvider):
    name: ClassVar[str] = "toy"

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        # ROLE 2: Observation — use as_observation() to mark the role.
        return ProviderMatch(
            provider=self.name,
            confidence=0.9,
            signals=Signals.as_observation(
                title="Inception",
                year=2010,
                runtime=148 * 60.0,
                medium=MediaType.MOVIE,
                language="en",
            ),
            external_ids=ExternalIds(imdb="tt1375666", tmdb_movie=27205),
        )


class ToyProviderB(MetadataProvider):
    """A second provider that disagrees on year — demonstrates conflict detection."""
    name: ClassVar[str] = "toy_b"

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return ProviderMatch(
            provider=self.name,
            confidence=0.7,
            signals=Signals.as_observation(title="Inception", year=2009),
            external_ids=ExternalIds(),
        )


def main() -> None:
    # ROLE 1: Query — use as_query() to mark the role explicitly.
    query = Signals.as_query(title="Inception", year=2010, medium=MediaType.MOVIE)
    assert query.role == SignalsRole.QUERY
    print(f"1. Query (caller → resolver): role={query.role.value}")
    print(f"   {query.model_dump(exclude_none=True, exclude={'role'})}")

    p = ToyProvider()
    pb = ToyProviderB()

    # ROLE 2: Observations from two providers.
    match_a = p.lookup(query)
    match_b = pb.lookup(query)
    assert match_a.signals.role == SignalsRole.OBSERVATION
    print(f"\n2a. Observation from '{match_a.provider}': confidence={match_a.confidence}")
    print(f"   {match_a.signals.model_dump(exclude_none=True, exclude={'role'})}")
    print(f"2b. Observation from '{match_b.provider}': confidence={match_b.confidence}")
    print(f"   {match_b.signals.model_dump(exclude_none=True, exclude={'role'})}")

    # Conflict detection: year disagrees (2010 vs 2009).
    conflicts = compare_signals(match_a.signals, match_b.signals)
    print(f"\n   Conflicts between providers: {[c.signal for c in conflicts] or '(none)'}")

    # ROLE 3: Result — merge winners and mark as result.
    merged = merge_signals(match_a.signals, match_b.signals).as_result()
    assert merged.role == SignalsRole.RESULT
    print(f"\n3. Result (consolidator → caller): role={merged.role.value}")
    print(f"   {merged.model_dump(exclude_none=True, exclude={'role'})}")
    print(f"\n   Note: a Result Signals is the closest the pipeline gets to a Work,")
    print(f"   but it has no canonical hash, no credits, no tracklist.")


if __name__ == "__main__":
    main()
