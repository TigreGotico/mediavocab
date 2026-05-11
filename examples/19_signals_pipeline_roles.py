"""Signals — the three pipeline roles (spec §5.10).

Same shape, three different jobs distinguished by direction of flow:

1. **Query** — caller fills it in, passes to the resolver.
2. **Observation** — the provider re-emits a Signals on
   ``ProviderMatch.signals`` describing what it believes the work is.
3. **Result** — the consolidator merges observations into one
   consensus ``ResolveResult.signals`` (not a Work — no canonical
   hash, no credits, no tracklist).

The duplication with Work is intentional — cross-provider comparison
needs identical comparable structure. A6 keeps Signals-only fields off
Work (``include_variants``, ``fanedit_subtype``, ``playback_type``,
``content_form``).
"""
from typing import ClassVar
from mediavocab import (
    MediaType, MetadataProvider, ProviderMatch, Signals,
)
from mediavocab.models import ExternalIds
from mediavocab.models.signals import compare_signals, merge_signals


# A toy provider that "observes" some signals from a Wikipedia-shaped row.
class ToyProvider(MetadataProvider):
    name: ClassVar[str] = "toy"

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        # ROLE 2: Observation. We assert what *we* found about the row.
        return ProviderMatch(
            provider=self.name,
            confidence=0.9,
            signals=Signals(
                title="Inception",
                year=2010,
                runtime=148 * 60.0,
                medium=MediaType.MOVIE,
                language="en",
            ),
            external_ids=ExternalIds(imdb="tt1375666", tmdb_movie=27205),
        )


def main() -> None:
    # ROLE 1: Query. The caller fills in what they know.
    query = Signals(title="Inception", year=2010, medium=MediaType.MOVIE)
    print(f"1. Query (caller → resolver):")
    print(f"   {query.model_dump(exclude_none=True)}")

    # Resolver dispatches to the provider...
    p = ToyProvider()
    if p.matches(query):
        match = p.lookup(query)
        # ROLE 2: Observation, on ProviderMatch.signals.
        print(f"\n2. Observation (provider → consolidator):")
        print(f"   provider={match.provider} confidence={match.confidence}")
        print(f"   signals={match.signals.model_dump(exclude_none=True)}")
        print(f"   external_ids={match.external_ids.model_dump(exclude_none=True)}")

        # ROLE 3: Result. The consolidator compares observation against the
        # query (and against other providers); merge_signals() unions the
        # information.
        conflicts = compare_signals(query, match.signals)
        merged = merge_signals(query, match.signals)
        print(f"\n3. Result (consolidator → caller):")
        print(f"   conflicts: {conflicts or '(none)'}")
        print(f"   merged signals (consensus, NOT a Work):")
        print(f"   {merged.model_dump(exclude_none=True)}")
        print(f"\n   Note: this is closest to a Work the pipeline produces,")
        print(f"   but it has no canonical hash, no credits, no tracklist.")
        print(f"   A consumer that wants a Work calls a separate constructor.")


if __name__ == "__main__":
    main()
