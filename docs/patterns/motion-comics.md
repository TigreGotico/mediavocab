# Motion comics

See spec §8.6. A motion comic is a video adaptation of comic panels with
camera moves, voice acting, and music. Despite the name, **it is not a
`COMIC`** — the playable artefact is video.

- `media_type` = `MOVIE` (single-volume) or `TV` (episodic series)
- `content_genres += [GENRE_MOTION_COMIC]`
- The static comic source is a separate `Work` (`MediaType.COMIC`) linked via
  `WorkRelation(kind=ADAPTED_FROM)` if both records are catalogued

A "comic book" label in a voice-playback context therefore maps to `TV`/`MOVIE`
with `GENRE_MOTION_COMIC`, never to `COMIC` — a static comic isn't a
playback target.
