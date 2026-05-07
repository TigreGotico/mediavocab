# Broadcast scheduling (EPG)

`Programme` and `Schedule` are the mediavocab primitives for EPG / TV-listings
/ radio-schedule data. They are not `Work` subclasses and carry no playback
URI — they locate *content* in time on a *channel*.

Source references: `mediavocab/models/work.py:220` (`Programme`),
`mediavocab/models/work.py:247` (`Schedule`).

## Key distinction: channel Work vs Programme slot

| Concept | Model | Notes |
|---|---|---|
| The station / channel itself | `Work` (`MediaType.RADIO` or `MediaType.TV`) | Persistent identity; its stream URLs are `Release`s |
| What is playing at a moment | `Programme` | Points at a content Work + channel + time window |
| A day's listings for a channel | `Schedule` | Ordered list of `Programme` slots |

The same episode broadcast on two channels at different times yields two
`Programme` records and one `Work`.

## Building a Schedule

```python
from mediavocab import EntityRef, EntityKind
from mediavocab.models.work import Programme, Schedule

channel = EntityRef(name="BBC Radio 4", external_ids={"tunein": "s18723"})

prog = Programme(
    work=EntityRef(name="The Archers", external_ids={"tvmaze": "6903"}),
    channel=channel,
    starts_at="2026-05-06T07:00:00Z",
    ends_at="2026-05-06T07:15:00Z",
    is_repeat=True,
)

schedule = Schedule(
    channel=channel,
    programmes=[prog],
    valid_from="2026-05-06T00:00:00Z",
    valid_until="2026-05-07T00:00:00Z",
    source="tvmaze",
    fetched_at="2026-05-06T01:00:00Z",
)
```

## Querying "what's on now"

mediavocab does not provide a query helper for "now" — the `Schedule` model is
intentionally data-only. A typical consumer pattern:

```python
def current_programme(schedule: Schedule, now_iso: str):
    for p in schedule.programmes:
        if p.starts_at <= now_iso < (p.ends_at or ""):
            return p
    return None
```

`programmes` is ordered by `starts_at` ascending. Replace a stale `Schedule`
wholesale rather than patching individual slots.

## Live vs repeat

`Programme.is_live` — set `True` for events where the aired moment is the
primary value (sport, breaking news, parliamentary coverage). Resolvers can
use this to skip dedup against a pre-existing Work record.

`Programme.is_repeat` — set `True` when this airing is a re-broadcast of an
episode already logged. Does not affect the referenced content Work.

## Resolving the content Work

`Programme.work` is an `EntityRef`, not an embedded `Work`. Resolve it against
the consumer's Work store using `external_ids` (preferred) or `title + year`.
Do not embed full Work trees in `Programme` records — this creates serialisation
cycles when an episode references its own series Work.

## Relationship to the radio pattern

`Schedule` and `Programme` sit *on top of* the station-as-Work model described
in `docs/patterns/radio.md`. The channel `EntityRef` on both models resolves
to the same radio/TV `Work` record.
