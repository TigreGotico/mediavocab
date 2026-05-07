# Playback modality — the third routing axis

mediavocab spec axiom 13 introduces `PlaybackModality` (`AUDIO` / `VIDEO`
/ `INTERACTIVE` / `TEXT` / `UNKNOWN`) as a routing axis orthogonal to
`MediaType` and `content_genres`. This pattern documents the full flow
from a consumer-side request through the three-axis gate to the right
provider subset.

## When to populate

Modality is a **query hint**, never an identity claim. Set it on a
`Signals` query; never on a `Work` or `Release`. The model layer derives
the *default* modality from `MediaType` via
`mediavocab.infer_modality(work.media_type)` — that's the canonical
projection if you need one — but the value is not persisted on the
canonical record.

Two upstream populations matter:

1. **Consumer verb → modality** (voice agent, search bar, command-line
   tool): the request shape carries the user's intent. *"play X"* ⇒
   `AUDIO`, *"watch X"* / *"show me X"* ⇒ `VIDEO`, *"open X"* / *"read
   X"* ⇒ `TEXT`, *"launch X"* / *"start X"* ⇒ `INTERACTIVE`.
2. **Indexed-data → modality** (cataloguer / archivist): when a row is
   already typed (Bandcamp ⇒ `MUSIC`, IPTV ⇒ `TV`), derive the modality
   from the medium via `infer_modality()`. The `media-archivist`
   reference implementation does exactly this in
   `signals_from_entry()`.

Underspecified rows (`MediaType.GENERIC` / `PLAYLIST` / `NOT_MEDIA`)
should leave `modality=None`. Gating on `PlaybackModality.UNKNOWN` would
exclude every provider; `None` is the gate's "no preference" sentinel
and lets the resolver fan out fully.

## The three-axis gate

`MetadataProvider.matches(signals)` short-circuits on three independent
checks (mediavocab/models/protocols.py:131):

```
(no `media`    declared OR signals.medium   in self.media)
AND
(no `modality` declared OR signals.modality in self.modality)
AND
(no `genre_filter` declared OR self.genre_filter ∩ signals.content_genres)
```

A provider declares its routing axes as `ClassVar[Set[…]]`:

```python
class TvmazeProvider(MetadataProvider):
    name     = "tvmaze"
    media    = {MediaType.EPISODIC_SERIES}
    modality = {PlaybackModality.VIDEO}
```

Empty set on any axis means "accept all" for that axis (the universal
case — used by `wikidata` and `skyhook`).

## Worked example: voice agent

```python
from mediavocab import (
    MediaType, PlaybackModality, Signals, infer_modality,
)
from metadatarr.resolve import resolve

VERB_TO_MODALITY = {
    "play":   PlaybackModality.AUDIO,
    "listen": PlaybackModality.AUDIO,
    "watch":  PlaybackModality.VIDEO,
    "show":   PlaybackModality.VIDEO,
    "read":   PlaybackModality.TEXT,
    "open":   PlaybackModality.TEXT,
    "launch": PlaybackModality.INTERACTIVE,
}


def parse(utterance: str) -> Signals:
    verb, _, title = utterance.strip().partition(" ")
    return Signals(title=title.strip(),
                   modality=VERB_TO_MODALITY.get(verb.lower()))


# "play me Bohemian Rhapsody" ⇒ modality=AUDIO ⇒ no fan-out to tvmaze /
# pyfanedit / dvdcompare; only audio-modality providers get the lookup.
result = resolve(parse("play Bohemian Rhapsody"))
```

## Worked example: indexed data

When the row is already typed, derive the modality from the medium:

```python
from mediavocab import infer_modality, PlaybackModality, Signals

def signals_from_entry(entry):
    medium = entry.medium  # already MUSIC / MOVIE / BOOK / ...
    inferred = infer_modality(medium)
    modality = inferred if inferred is not PlaybackModality.UNKNOWN else None
    return Signals(title=entry.title, medium=medium, modality=modality)
```

Bandcamp (`MUSIC`) and SoundCloud (`MUSIC`) rows ⇒ `AUDIO`. IPTV (`TV`)
⇒ `VIDEO`. Plain YouTube (`GENERIC`) ⇒ `None` until a content-type
enrichment pass narrows it. Reference implementation:
`media_archivist/canonicalize.py` — `signals_from_entry()`.

## What modality is *not*

- **Not a `Work` field.** A `Work`'s modality is implicit in its
  `MediaType`. Persisting it would invite drift between two sources of
  truth (axiom 13).
- **Not in the identity hash.** `signal_hash`, `work_hash`, and
  `release_hash` all exclude it — modality is a routing concern, not an
  identity one.
- **Not a comparator.** `compare_signals()` and `merge_signals()` skip
  modality. Two providers observing the same work never disagree on
  modality (they don't observe it at all); the consumer's hint is the
  only authoritative source.
- **Not for device control.** Per axiom 4, devices are
  `Entity(EntityKind.DEVICE)`; *"turn on the kitchen light"* is
  `MediaType.NOT_MEDIA`. `PlaybackModality` is for media-playback
  intent only.

## Adding a new modality value

The default mapping (`MEDIA_TYPE_TO_MODALITY`) covers every `MediaType`.
A new modality value would have to (a) capture a real consumer-side
intent that's not expressible by the existing five, and (b) gate at
least one provider distinctly from the others. A "background ambient"
modality — e.g. for unattended playback — would meet both bars; an
"educational" modality would not (it's a content-genre concern).

When in doubt, add a `content_genres` tag instead.
