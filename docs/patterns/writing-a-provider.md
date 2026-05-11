# Writing a metadata provider

A *provider* is a class that resolves a `Signals` query into a typed
`ProviderMatch` against one source — IMDB, MusicBrainz, a local file
index, a Home Assistant entity registry. The mediavocab spec defines the
provider contract (§4.11, four-axis routing gate); downstream packages
(e.g. `metadatarr`) supply the runtime registry, dispatcher, and
consolidator.

This walkthrough builds a minimal `MetadataProvider` end-to-end.

## 1. Subclass `MetadataProvider` and declare your axes

The base class is in `mediavocab.models.protocols`. Declare the four
routing axes as `ClassVar[Set[...]]`. Empty sets mean "universal" on
that axis.

```python
from typing import ClassVar, Optional, Set

from mediavocab import (
    ContentForm, ExternalIds, MediaType, MetadataProvider, PlaybackType,
    ProviderMatch, Signals,
)


class TVMazeProvider(MetadataProvider):
    name: ClassVar[str] = "tvmaze"
    media: ClassVar[Set[MediaType]] = {MediaType.EPISODIC_SERIES}
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.VIDEO}
    content_form: ClassVar[Set[ContentForm]] = {ContentForm.PRIMARY}
    genre_filter: ClassVar[Set[str]] = set()   # universal across genres
```

The four-axis gate (in `_four_axis_gate`) short-circuits independently
on each axis. A `Signals` field that is `None` always passes — the
caller has no preference on that axis. A non-empty class-level set that
the corresponding `Signals` field is missing from rejects the provider.

## 2. Implement `is_available` and `lookup`

These are abstract; missing either raises `TypeError` at instantiation.

```python
class TVMazeProvider(MetadataProvider):
    # …axes above…

    def is_available(self) -> bool:
        # Cheap check: API reachable, key present, dependencies importable.
        # Called once per dispatch cycle.
        return True

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        if not self.matches(signals):     # honour the four-axis gate
            return None
        # Real impl: HTTP call, parse, normalise.
        return ProviderMatch(
            provider=self.name,
            confidence=0.92,
            signals=signals.model_copy(update={
                "year": 2005,             # what TVMaze believes
            }),
            external_ids=ExternalIds(tvmaze=1234, imdb="tt0386676"),
        )
```

`ProviderMatch.confidence ∈ [0.0, 1.0]` is the provider's own
self-assessed confidence. The consolidator weighs it against other
providers via `match_quality`.

## 3. Re-emit your beliefs as `Signals`

The same `Signals` shape carries three roles:
- **Query** (caller → resolver) — what the caller knows.
- **Observation** (provider → consolidator) — what *you* believe the
  Work is.
- **Consensus** (consolidator → caller) — the merged result.

In `lookup`, fill the Signals fields you can derive from your source.
The consolidator runs `compare_signals(ours, theirs)` across providers
and drops conflicts; non-overlap is treated as agreement (a missing
value is *unknown*, not contradictory).

## 4. Anchor with `ExternalIds`

`ProviderMatch.external_ids` carries the authoritative IDs your source
asserts. The consolidator uses these to merge cross-provider matches
via first-writer-wins (`ExternalIds.merge`). Use well-known constants
from `mediavocab.models.external_ids` for cross-package interop:

```python
from mediavocab.models import external_ids as eid

match.external_ids = ExternalIds.from_dict({
    eid.IMDB: "tt0386676",
    eid.TVMAZE: "1234",
})
```

## 5. Routing without inheritance

Anything declaring the four ClassVars duck-types as a provider:

```python
from mediavocab.models.protocols import provider_matches

class LocalIndex:
    name = "local_files"
    media = {MediaType.MUSIC}
    playback_type = {PlaybackType.AUDIO}
    content_form = set()
    genre_filter = set()

# provider_matches() takes any object with the four attrs.
assert provider_matches(LocalIndex(), Signals(medium=MediaType.MUSIC))
```

## Why this shape?

- **A1**: schema-or-database admission keeps `MediaType` small. The gate
  filters by `MediaType` first because that's the only axis that
  changes the schema.
- **A6**: routing axes are orthogonal to identity. `playback_type` /
  `content_form` / `genre_filter` are ClassVars on the provider; they
  do *not* live on `Work` and never enter `work_hash`.
- **A7**: one source of truth per fact. `ExternalIds` keys go in
  `ProviderMatch.external_ids`; they do *not* duplicate in
  `Signals.extra` or elsewhere.

## Common mistakes

- **Hashing `ProviderMatch.signals` and using it as a key.** Use
  `signal_hash` (a stable digest over the bag) — `Signals` itself isn't
  hashable.
- **Returning `MediaType.GENERIC` from `lookup`.** T8 forbids it on a
  Work; downstream code that builds a Work will raise. If you can't
  classify, leave `signals.medium = None`.
- **Conflating `Stream.kind` and `MediaType`.** `Stream.kind` is the
  *platform asset category* ("track", "video", "album"); it has
  nothing to do with the mediavocab `MediaType` enum.
- **Inheriting `RUNTIME_HASH_QUANTUM_S` semantics from the docs while
  comparing in your provider.** The consolidator handles runtime
  tolerance; your `lookup` just emits a number.

## Testing

See `tests/models/test_protocols.py` for the canonical four-axis-gate
tests. Roll your provider's tests on top of `MetadataProvider` rather
than re-deriving the gate logic.
