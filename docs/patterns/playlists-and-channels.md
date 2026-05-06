# Playlists, anthologies, and live-streamer channels

Three patterns that reuse `Work` + `Release` differently from a typical
single-media-type catalogue entry.

## User playlists

A user playlist (Spotify playlist, YouTube playlist, M3U file, OPML
podcast bundle) is a `Work` with `media_type = MediaType.PLAYLIST` and
a `tracklist` of `Appearance`s pointing to the constituent Works.

The curator is credited via `RelationRole.CURATOR` — *not* `CREATOR`,
because the playlist's value is in the *selection and ordering*, not
in the underlying recordings (which have their own creator credits).

```python
from mediavocab import (
    Appearance, Credit, CreditSection, EntityKind, EntityRef,
    MediaType, RelationRole, Work,
)

playlist = Work(
    title="Evening Wind-Down",
    media_type=MediaType.PLAYLIST,
    tracklist=[
        Appearance(work=track1, position=1),
        Appearance(work=track2, position=2),
    ],
    credits=[Credit(
        entity=EntityRef(name="Alice", kind=EntityKind.PERSON),
        role="curator",
        relation_role=RelationRole.CURATOR,
        section=CreditSection.PRINCIPAL,
    )],
    external_ids={"spotify": "37i9dQZF1DX..."},
)
```

### Why a dedicated `MediaType.PLAYLIST`

A YouTube playlist routinely mixes music videos with vlogs and feature
films; a Spotify playlist mixes podcast episodes and music; an M3U
file mixes radio streams and on-demand audio. None of these fit
`MediaType.MUSIC` (or any other single type), and the cataloguing
schema is genuinely different — the *order* and *curator* are the
identity, the constituent Works are mutable, the database providers
(Spotify Playlist API, YouTube Playlist API) are distinct from the
Work-level providers underneath. Per spec axiom 1, that earns its own
type.

A single-media-type curated set that is itself a recognised release
(a rapper's mixtape, an artist's compilation album) stays as
`MediaType.MUSIC` with `variant_kind = COMPILATION` — the schema is
the same as a regular album.

### Mutability

`Work` identity-fields (`title`, `year`, `media_type`, …) are
immutable per spec §10.1, but `tracklist` is in the mutable set. A
playlist that loses or reorders tracks does not become a new Work.
Consumers that need to track playlist history versus current state
should snapshot the tracklist alongside a timestamp, separately from
the Work record.

## Anthologies and curated boxsets

A *published* anthology (a music label's "best of the year" comp, a
short-story anthology with a named editor) differs from a personal
playlist: it ships with an ISBN / cat-no / catalogue presence, and
the editor is *responsible* for the selection in a way the listener
treats as authoritative.

Use the underlying media type (e.g. `MediaType.MUSIC` /
`MediaType.BOOK`) plus `variant_kind = COMPILATION` and credit the
editor with `RelationRole.CURATOR`. The published anthology is a
different *kind of object* from a user-curated playlist even when the
content overlaps:

```python
anthology = Work(
    title="Year's Best Weird Fiction Vol. 5",
    media_type=MediaType.BOOK,
    variant_kind=VariantKind.COMPILATION,
    tracklist=[Appearance(work=story_1, position=1), ...],
    credits=[Credit(
        entity=EntityRef(name="Editor Name", kind=EntityKind.PERSON),
        role="editor",
        relation_role=RelationRole.CURATOR,
    )],
    external_ids={"isbn": "9781771485204"},
)
```

## Live-streamer channels

A streamer's channel (Twitch, Kick, YouTube Live) is modelled exactly
like a radio station — a `Work` with `media_type = MediaType.TV` (live
linear broadcast channel) whose stream URLs are `Release`s with
`stream_mode = StreamMode.CONTINUOUS` while live, transitioning to
`stream_mode = ON_DEMAND` once archived as a VOD.

```python
channel = Work(
    title="some_streamer",
    media_type=MediaType.TV,         # live broadcast channel
    series_title="some_streamer",
    runtime=None,
)
live = Release(work=channel, uri="https://twitch.tv/...",
                stream_mode=StreamMode.CONTINUOUS)
vod  = Release(work=channel, uri="https://twitch.tv/videos/...",
                stream_mode=StreamMode.ON_DEMAND)
```

When a stream is a discrete catalogued piece (e.g. a one-off marathon)
it becomes its own Work whose `series_title` is the channel name —
exactly as a specific radio programme on a station is its own Work.
