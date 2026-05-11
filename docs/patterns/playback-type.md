# Playback type — the derived player-surface axis

mediavocab spec §3.8 / §4.11 defines `PlaybackType` (`AUDIO` / `VIDEO`
/ `PAGED` / `INTERACTIVE` / `UNKNOWN`) as a *derived* routing axis (A6)
orthogonal to `MediaType` and `content_genres`. This pattern documents
the flow from a consumer-side request through the four-axis provider
gate to the right provider subset.

## When to populate

Modality is a **query hint**, never an identity claim. Set it on a
`Signals` query; never on a `Work` or `Release`. The model layer derives
the *default* playback_type from `MediaType` via
`mediavocab.infer_playback_type(work.media_type)` — that's the canonical
projection if you need one — but the value is not persisted on the
canonical record.

Two upstream populations matter:

1. **Consumer verb → playback_type** (voice agent, search bar, command-line
   tool): the request shape carries the user's intent. *"play X"* ⇒
   `AUDIO`, *"watch X"* / *"show me X"* ⇒ `VIDEO`, *"open X"* / *"read
   X"* ⇒ `TEXT`, *"launch X"* / *"start X"* ⇒ `INTERACTIVE`.
2. **Indexed-data → playback_type** (cataloguer / archivist): when a row is
   already typed (Bandcamp ⇒ `MUSIC`, IPTV ⇒ `TV`), derive the playback_type
   from the medium via `infer_playback_type()`. The `media-archivist`
   reference implementation does exactly this in
   `signals_from_entry()`.

Underspecified rows (`MediaType.GENERIC` / `PLAYLIST` / `NOT_MEDIA`)
should leave `playback_type=None`. Gating on `PlaybackType.UNKNOWN` would
exclude every provider; `None` is the gate's "no preference" sentinel
and lets the resolver fan out fully.

## The four-axis gate

`MetadataProvider.matches(signals)` short-circuits on four independent
checks (mediavocab/models/protocols.py:`_four_axis_gate`):

```
(no `media`         declared OR signals.medium         in self.media)
AND (no `playback_type` declared OR signals.playback_type in self.playback_type)
AND (no `content_form`  declared OR signals.content_form  in self.content_form)
AND (no `genre_filter`  declared OR self.genre_filter ∩ signals.content_genres)
```

A provider declares its routing axes as `ClassVar[Set[…]]`:

```python
class TvmazeProvider(MetadataProvider):
    name     = "tvmaze"
    media    = {MediaType.EPISODIC_SERIES}
    playback_type = {PlaybackType.VIDEO}
```

Empty set on any axis means "accept all" for that axis (the universal
case — used by `wikidata` and `skyhook`).

## Worked example: voice agent

```python
from mediavocab import (
    MediaType, PlaybackType, Signals, infer_playback_type,
)
from metadatarr.resolve import resolve

VERB_TO_MODALITY = {
    "play":   PlaybackType.AUDIO,
    "listen": PlaybackType.AUDIO,
    "watch":  PlaybackType.VIDEO,
    "show":   PlaybackType.VIDEO,
    "read":   PlaybackType.PAGED,
    "open":   PlaybackType.PAGED,
    "launch": PlaybackType.INTERACTIVE,
}


def parse(utterance: str) -> Signals:
    verb, _, title = utterance.strip().partition(" ")
    return Signals(title=title.strip(),
                   playback_type=VERB_TO_MODALITY.get(verb.lower()))


# "play me Bohemian Rhapsody" ⇒ playback_type=AUDIO ⇒ no fan-out to tvmaze /
# pyfanedit / dvdcompare; only audio-playback_type providers get the lookup.
result = resolve(parse("play Bohemian Rhapsody"))
```

## Worked example: indexed data

When the row is already typed, derive the playback_type from the medium:

```python
from mediavocab import infer_playback_type, PlaybackType, Signals

def signals_from_entry(entry):
    medium = entry.medium  # already MUSIC / MOVIE / BOOK / ...
    inferred = infer_playback_type(medium)
    playback_type = inferred if inferred is not PlaybackType.UNKNOWN else None
    return Signals(title=entry.title, medium=medium, playback_type=playback_type)
```

Bandcamp (`MUSIC`) and SoundCloud (`MUSIC`) rows ⇒ `AUDIO`. IPTV (`TV`)
⇒ `VIDEO`. Plain YouTube (`GENERIC`) ⇒ `None` until a content-type
enrichment pass narrows it. Reference implementation:
`media_archivist/canonicalize.py` — `signals_from_entry()`.

## What playback_type is *not*

- **Not a `Work` field.** A `Work`'s playback_type is derived from its
  `MediaType` (A6). Persisting it would invite drift between two sources
  of truth (A7).
- **Not in the identity hash.** `signal_hash`, `work_hash`, and
  `release_hash` all exclude it — playback_type is a routing concern, not an
  identity one.
- **Not a comparator.** `compare_signals()` and `merge_signals()` skip
  playback_type. Two providers observing the same work never disagree on
  playback_type (they don't observe it at all); the consumer's hint is the
  only authoritative source.
- **Not for device control.** Per A3, devices are
  `Entity(EntityKind.DEVICE)`; *"turn on the kitchen light"* is
  `MediaType.NOT_MEDIA`. `PlaybackType` is for media-playback intent only.

## Adding a new playback_type value

The default mapping (`MEDIA_TYPE_TO_PLAYBACK_TYPE`) covers every `MediaType`.
A new playback_type value would have to (a) capture a real consumer-side
intent that's not expressible by the existing five, and (b) gate at
least one provider distinctly from the others. A "background ambient"
playback_type — e.g. for unattended playback — would meet both bars; an
"educational" playback_type would not (it's a content-genre concern).

When in doubt, add a `content_genres` tag instead.
