# Models reference

All models are pydantic v2 with `ConfigDict(extra="ignore", populate_by_name=True)`.
Unknown input fields are dropped silently — this is intentional, since the
spec values flexibility over strictness at consumer boundaries.

## `Work` — the canonical creative work

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | Required |
| `media_type` | `MediaType` | Defaults to `GENERIC` |
| `year` | `Optional[int]` | Original release year of *this* Work; for TV episodes use episode air year |
| `runtime` | `Optional[float]` | Seconds; `None` for stations / open-ended content |
| `language` | `str` | ISO 639-1 or 639-2; `""` = unknown |
| `country` | `str` | ISO 3166-1 alpha-2 |
| `season`, `episode` | `Optional[int]` | TV / episodic podcast / radio |
| `series_title` | `Optional[str]` | Container series name |
| `variant_kind` | `Optional[VariantKind]` | `None` = canonical edition |
| `edition` | `str` | Free text, e.g. `"Criterion Collection"` |
| `source_format` | `str` | Original capture: `"35mm"`, `"DAB"`, `"Analogue tape"` |
| `color`, `audio_present` | `Optional[bool]` | Objective artefact properties |
| `content_genres` | `List[str]` | Free; use `GENRE_*` constants when known |
| `release_status` | `ReleaseStatus` | Defaults to `RELEASED` |
| `aka` | `List[str]` | Plain alternative titles / spellings; not part of identity hash |
| `localized_titles` | `List[Tuple[str, str]]` | `(title, ISO 639-1)` for cross-locale matching |
| `credits` | `List[Credit]` | Who contributed to this Work |
| `tracklist` | `List[Appearance]` | For albums, anthologies, playlists |
| `external_ids` | `Dict[str, str]` | `{"imdb": "tt..."}` |
| `extra` | `Dict[str, Any]` | Escape hatch — use sparingly |

## `Release` — a specific manifestation

A Release has a `work`, a `uri`, and edition/format/region metadata. `variant_kind`
on Release wins over Work — a director's cut is a Release-level distinction.
`stream_mode` is on Release, not Work, because looping is a delivery concern.

**Localisation** is three orthogonal axes — do *not* collapse into `VariantKind.REGIONAL`:

- `region` — release market (ISO 3166-1 alpha-2)
- `audio_language` — primary audio track (ISO 639-1)
- `subtitle_languages` — available subtitle tracks (`List[str]` of ISO 639-1)

`VariantKind.REGIONAL` is reserved for *editorial* differences (censorship cuts,
alternate scenes), not language tracks.

**`chapters: List[Chapter]`** — timestamped navigation markers within the Release.
Audiobook chapters, podcast chapter markers, DVD scene breaks. Chapters are not
Works; if the unit can stand alone on another Release, model it as `Appearance`
referencing its own Work instead.

**`accessibility: List[AccessibilityTrack]`** — subtitles, captions, audio
description, sign-language inserts, lyric files, transcripts. Per-Release because
the same Work commonly has different accessibility profiles across its Releases.

## `Chapter` — mid-Release marker

`offset` (seconds), `title`, optional `image`, optional `end`. Chapters are
markers, not Works.

## `AccessibilityTrack` — per-Release accessibility asset

`kind` is a free string ("subtitles", "captions", "audio_description",
"sign_language", "transcript", "lyrics"). `language` is ISO 639-1. Booleans
`forced` and `sdh` flag forced subtitles and SDH (subtitles for the deaf and
hard-of-hearing).

## `Appearance` — Work in a Release container

Position of a Work within an album / anthology / playlist. Use
`attributed_to` on every Appearance of a split release (axiom: leaving it
`None` is ambiguous).

## `Entity` — person / group / organisation / series / device

No `media_type` — entities are not played, they participate in or route
playback. Use `memberships` for GROUP lineups (each stint is one record).

## `Credit` — entity participation in a specific Work or Release

`role` keeps the raw source string ("Bass Guitar"); `relation_role` maps to
the closed `RelationRole` enum for programmatic routing.

## `EntityRef` — a pointer

Used inside Work / Release / Credit / Membership. Resolve against a consumer-
side entity store before treating as authoritative.

## `Membership` — temporal group membership

`date_to=None` does NOT mean current — combine with `status` to interpret.

## `WorkRelation` — Work→Work links (optional)

Wraps `WorkRelationKind` and a target Work. Use for `COVERS`, `SOUNDTRACK_FOR`,
`SEQUEL_TO`, etc. Stored on `Work.extra` until consumers need uniform
behaviour, per the spec's deferred-formalisation note.

## Decision guide: Work vs Release

| Question | Answer |
|---|---|
| Same film, different cut? | Same Work, different Release (`variant_kind=DIRECTORS`) |
| Same song on two albums? | Same Work, two Appearances in two different Release containers |
| BBC Radio 4 primary URL vs backup mirror? | Same Work, two Releases with different URIs |
| 1986 CD vs 2017 remaster of an album? | Same Work, two Releases (`REMASTERED` on the second) |
| Cover version of "Hallelujah"? | Different Work; link with `WorkRelation(kind=COVERS)` |
