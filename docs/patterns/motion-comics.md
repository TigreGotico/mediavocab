# Motion comics

A motion comic is a video adaptation of comic panels with camera moves,
voice acting, and music. Despite the name, **it is not a `COMIC`** — the
playable artefact is video (T6: playback surface is `VIDEO`, not `PAGED`).

- `media_type` = `MOVIE` (single-volume) or `EPISODIC_SERIES` (when it
  ships as an ordered season-and-episode series).
- `content_genres += [GENRE_MOTION_COMIC]`.
- The static comic source is a separate `Work` (`MediaType.COMIC`) linked
  via `WorkRelation(kind=ADAPTED_FROM)` when both records are catalogued.

A "comic book" label in a voice-playback context therefore maps to
`MOVIE` / `EPISODIC_SERIES` with `GENRE_MOTION_COMIC`, never to `COMIC` —
a static comic is `PAGED`, not a playback target for *"play the
Watchmen motion comic"*.

```python
from mediavocab import MediaType, Work, WorkRelation, WorkRelationKind
from mediavocab.taxonomy.genre import GENRE_MOTION_COMIC

print_comic = Work(
    title="Watchmen",
    media_type=MediaType.COMIC, year=1986,
    publication_country="US",
    series_title="Watchmen", episode=1,
)

motion_comic = Work(
    title="Watchmen: Motion Comic",
    media_type=MediaType.EPISODIC_SERIES, year=2008,
    production_country="US", language="en",
    content_genres=[GENRE_MOTION_COMIC],
    series_title="Watchmen: Motion Comic", season=1, episode=1,
    relations=[WorkRelation(
        kind=WorkRelationKind.ADAPTED_FROM,
        target=print_comic,
        note="Direct adaptation of the 1986 DC Comics series",
    )],
)
```
