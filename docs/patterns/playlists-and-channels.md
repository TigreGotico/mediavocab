# User playlists and live-streamer channels

Two patterns that look like Works but feel different to users.

## User playlists

A user playlist is a `Work` whose `tracklist` is `Appearance`s pointing to
existing Works. The curator is credited via `RelationRole.CREATOR`.

```python
playlist = Work(
    title="Evening Wind-Down",
    media_type=MediaType.MUSIC,
    tracklist=[
        Appearance(work=track1, position=1),
        Appearance(work=track2, position=2),
    ],
    credits=[Credit(
        entity=EntityRef(name="Alice", kind=EntityKind.PERSON),
        role="curator",
        relation_role=RelationRole.CREATOR,
    )],
)
```

The model is identical to an album; the **lifecycle** is different (the user
adds and removes members over time). That's a consumer concern, not a
vocabulary one.

## Live-streamer channels

A streamer's channel (Twitch, Kick, YouTube Live) is modelled exactly like a
radio station — a `Work` whose stream URLs are `Release`s with
`stream_mode=StreamMode.CONTINUOUS` while live, transitioning to
`stream_mode=ON_DEMAND` once archived as a VOD.

```python
channel = Work(
    title="some_streamer",
    media_type=MediaType.TV,
    series_title="some_streamer",
    runtime=None,
)
live = Release(work=channel, uri="https://twitch.tv/...",
                stream_mode=StreamMode.LIVE)
vod  = Release(work=channel, uri="https://twitch.tv/videos/...",
                stream_mode=StreamMode.ON_DEMAND)
```

When a stream is a discrete catalogued piece (e.g. a one-off marathon) it
becomes its own Work whose `series_title` is the channel name — exactly as a
specific radio programme on a station is its own Work.
