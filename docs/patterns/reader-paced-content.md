# Reader-paced and user-paced content

Books, comics, slideshows, and interactive fiction share an attribute that
isn't representable as a runtime: the user controls pacing. A novel's page
count is finite but reading time depends on the reader. A photo slideshow
ends when the viewer dismisses it. An IF session ends when the player saves.

`mediavocab` encodes this as `runtime=None`. There is intentionally no
`Pacing` axis — adding one would force every consumer to handle a third state
for a property they don't use.

`runtime=None` has two interpretations:

1. **Unknown** — not yet resolved by the consumer's pipeline
2. **Indeterminate** — user-paced or open-ended

Distinguish at the consumer per the rule in §5.3 (`Work.runtime`):

- `media_type ∈ {BOOK, COMIC, GAME, INTERACTIVE_FICTION, TV, RADIO, PLAYLIST}` → indeterminate
- `stream_mode == StreamMode.CONTINUOUS` on any Release → indeterminate (open-ended stream)
- otherwise → unknown (treat as missing data)

## Slideshows and photo books

A photo collection is a `BOOK` Work:

- `content_genres=[GENRE_PHOTO_BOOK]` — unordered or arbitrary order
- `content_genres=[GENRE_SLIDESHOW]` — ordered for sequential viewing

A slideshow timer (if any) is a Release-level concern; store interval seconds
in `Release.extra["slide_interval"]` or rely on the consumer's default.

A motion-comic slideshow with embedded animation is **not** this — it is
`MOVIE`/`TV` with `GENRE_MOTION_COMIC` (see [motion-comics.md](./motion-comics.md)).

## Branching narratives

The MediaType follows distribution channel (T7), not narrative structure:

| Distribution | MediaType | Genres |
|---|---|---|
| Print "choose your own adventure" | `BOOK` | `GENRE_BRANCHING` |
| Twine, ChoiceScript, Inform | `INTERACTIVE_FICTION` | `GENRE_CHOICE_IF` / `GENRE_PARSER_IF` + `GENRE_BRANCHING` |
| Voice-only narrative app | `INTERACTIVE_FICTION` | `GENRE_VOICE_GAME` + `GENRE_BRANCHING` |
| Telltale, Detroit: Become Human | `GAME` | `GENRE_BRANCHING` |
