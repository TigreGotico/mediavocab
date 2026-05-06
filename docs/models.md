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
| `original_languages` | `List[str]` | ISO 639-1 list; for multi-language originals (e.g. Quebec films, simulcast anime) — `mediavocab/models/work.py:98` |
| `credits` | `List[Credit]` | Who contributed to this Work |
| `tracklist` | `List[Appearance]` | For albums, anthologies, playlists |
| `external_ids` | `Dict[str, str]` | `{"imdb": "tt..."}` |
| `extra` | `Dict[str, Any]` | Escape hatch — use sparingly |

## `Release` — a specific manifestation

A Release has a `work`, a `uri`, and four orthogonal blocks of metadata:
**format**, **quality**, **localisation**, and **rights/availability**.

**Format axes** (replaces the old overloaded `source_format`):

| Field | Carries | Examples |
|---|---|---|
| `container` | physical or distribution medium | `"Blu-ray"`, `"Vinyl"`, `"Digital"`, `"Skill"`, `"ROM"`, `"Glulx"` |
| `codec` | audio/video codec | `"FLAC"`, `"H.264"`, `"AV1"` |
| `bitrate` | codec parameters | `"320kbps"`, `"24/96"` |
| `platform` | game / IF runtime target | `"PS4"`, `"SNES"`, `"Alexa Skill"` |

**Quality** — `resolution`, `hdr`, `audio_channels`, `sample_rate`. Enables
"play me the highest-quality release" without string parsing.

`variant_kind` on Release wins over Work — a director's cut is a Release-level
distinction. `stream_mode` is on Release, not Work, because looping is a
delivery concern.

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

**Rights and availability** — `license`, `region_locked`, `regions_available`,
`available_from`, `available_until`. Typed instead of buried in `extra`. Covers
public-domain editions, Creative-Commons releases, region-locked streams, and
"leaves Netflix on 2026-01-31" workflows.

`availability_windows: List[Tuple[Optional[str], Optional[str]]]` — list of
`(available_from, available_until)` ISO datetime pairs for releases with multiple
availability windows (e.g. a rotating catalogue window). Populate only when a
single `available_from`/`available_until` pair is insufficient — `mediavocab/models/work.py:169`.

**Box sets / composite Releases** — `contents: List[Appearance]` aggregates
multiple Works in a single Release without inventing a synthetic container Work.
Use `tracklist` on Work for canonical track ordering of the work itself; use
`contents` on Release for box-set packaging of *separate* Works.

## `Chapter` — mid-Release marker

`offset` (seconds), `title`, optional `image`, optional `end`. Chapters are
markers, not Works.

`work_ref: Optional[EntityRef]` — set only when the chapter content is a
separately-identifiable Work (e.g. a named short story in an anthology
audiobook). Usually `None` — `mediavocab/models/work.py:62`.

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

`localized_names: List[Tuple[str, str]]` — language-tagged alternative spellings
of the entity name: `(name, ISO 639-1)`. Distinct from the `name` field (which
carries the canonical/search spelling) — `mediavocab/models/entity.py:30`.

## `Membership` — temporal group membership

`date_to=None` does NOT mean current — combine with `status` to interpret.

## Helpers — `mediavocab.helpers.queries`

Non-normative convenience functions on top of the model surface
(`mediavocab/helpers/queries.py`).

```python
episodes_of(series_work, all_works) -> List[Work]
    # Episodes belonging to a series, sorted (season, episode).
    # Match by series_title. — queries.py:60

filmography_of(entity_ref, all_works, relation_role=None) -> List[Work]
    # Works on which the entity is credited. Optional RelationRole filter.
    # Matches by external_ids overlap; falls back to name equality. — queries.py:80

quality_score(release) -> tuple
    # Sortable tuple: (variant_pref, resolution, hdr, audio_channels,
    # sample_rate). Higher tuples are better releases. — queries.py:141

best_release(*releases) -> Optional[Release]
    # The highest-quality Release. Bootlegs lose to anything;
    # director's cuts beat theatrical; 4K beats 1080p; Atmos beats stereo.
    # List order breaks ties (caller pre-orders by preference). — queries.py:156
```

`quality_score` variant preference order (highest first): `directors`, `extended`,
`preservation`, `remastered`, `upscaled` / `deluxe`, `colorized`, `theatrical` /
`reissue`, `regional`, `bootleg` (negative).

## `WorkRelation` — Work→Work links

Wraps `WorkRelationKind` (`COVERS`, `SOUNDTRACK_FOR`, `SEQUEL_TO`,
`FANEDIT_OF`, …) and a target Work. The `target` field carries enough
identity (`title`, `year`, `media_type`, plus an `external_ids` entry)
to resolve against the consumer's Work store later — avoid embedding
the full nested target Work, which creates serialisation cycles for
chains like `COVERS` or `PART_OF`.

Game-shaped relations added in 0.3 — `mediavocab/taxonomy/relation.py:64`:

| Kind | Semantics |
|---|---|
| `DLC_FOR` | DLC tied to a specific base game; the DLC is not standalone |
| `EXPANSION_OF` | Standalone expansion that ships independently but extends a base Work |

## `ReleaseRelation` — Release→Release links

Per-edition lineage parallel to `WorkRelation` — use when the relationship
exists at the *manifestation* level rather than the *creative work* level
(`mediavocab/models/work.py:205`, `mediavocab/taxonomy/relation.py:68`).

| `ReleaseRelationKind` | Semantics |
|---|---|
| `SUPERSEDES` | Newer release replaces an earlier one (e.g. newer remaster) |
| `REMASTER_OF` | Explicit remaster lineage |
| `REISSUE_OF` | Later commercial release of the same edition |
| `PORT_OF` | Platform port of the same base game or IF work |
| `DERIVED_FROM` | Generic "this Release is derived from that one" |

Example: a 2025 Atmos remaster `SUPERSEDES` the 2017 stereo remaster of the
same Work. `WorkRelation` cannot express this because both Releases share the
same Work.

## `Programme` — broadcast slot

A single airing of a Work on a broadcast channel (`mediavocab/models/work.py:220`).
Points at the *content* Work being aired and locates it in time on a specific
channel. Two channels broadcasting the same episode at different times yield two
`Programme` records and one Work.

| Field | Type | Notes |
|---|---|---|
| `work` | `EntityRef` | Content Work being aired |
| `channel` | `EntityRef` | Broadcast channel Work or Entity |
| `starts_at` | `str` | ISO datetime; aired-at start |
| `ends_at` | `Optional[str]` | ISO datetime; aired-at end |
| `runtime` | `Optional[float]` | Seconds; programme length on the schedule |
| `is_live` | `bool` | `True` for live broadcasts (sport, news, talk) |
| `is_repeat` | `bool` | `True` for re-broadcasts |

## `Schedule` — EPG window for a channel

An ordered list of `Programme` slots for a single broadcast channel over a
time window (`mediavocab/models/work.py:247`). Use for EPG / TV-listings /
radio-schedule data.

| Field | Type | Notes |
|---|---|---|
| `channel` | `EntityRef` | The broadcast channel |
| `programmes` | `List[Programme]` | Ordered slots |
| `valid_from` | `Optional[str]` | ISO datetime; start of the schedule window |
| `valid_until` | `Optional[str]` | ISO datetime; end of the schedule window |
| `source` | `str` | Provider hint (`"tunein"`, `"tvmaze"`, `"epg.xml"`) |
| `fetched_at` | `Optional[str]` | When the schedule was retrieved (staleness check) |

Query the schedule for the slot whose `[starts_at, ends_at)` contains the
consumer's clock. Schedules are append-only at the model level; replace a
stale `Schedule` wholesale to refresh.

## `License` — typed rights overlay

`mediavocab.models.license.License` is a typed companion to the free-form
`Release.license: str` field (`mediavocab/models/license.py`). The string
stays canonical for persistence; `License` is an ergonomic overlay for
callers that want to filter on rights without string-matching.

```python
from mediavocab.models.license import License

lic = License.from_spdx("CC-BY-SA-4.0")
lic.commercial      # False (NC not set → True; SA set → still commercial)
lic.share_alike     # True
lic.is_open()       # True — any CC-* or public-domain licence is open
```

`License.from_spdx(spdx: str) -> License` — `mediavocab/models/license.py:68`
— parses an SPDX-style identifier, a `CC-BY-*` variant, `"public_domain"`,
`"CC0"`, or `"all_rights_reserved"`. Unknown strings default to fully
restricted (preserving the raw identifier). Round-trip via the `identifier`
field.

`License.is_open() -> bool` — `mediavocab/models/license.py:55` — `True` iff
the licence permits at least non-commercial, no-derivative redistribution. All
CC-* and public-domain/CC0 licences qualify; `all_rights_reserved` and empty
do not.

## `ExternalIds` — typed external identifiers

`mediavocab.ExternalIds` is the typed companion to the free-form
`Dict[str, str]` `external_ids` field on Work / Release / Entity. ~50
known fields (musicbrainz_*, tmdb_*, anilist_*, isbn_10, isbn_13,
fanedit_id, …) plus a `extra: Dict[str, str]` escape hatch for
unknown providers.

```python
ids = ExternalIds(isbn_10="0-261-10328-8")
ids.isbn_13       # auto-paired: "9780261103283"
ids.merge(other)  # first-writer-wins
ids.streams       # → List[Stream] expanded from URL/ID keys in `extra`
ids.to_dict()     # plain Dict[str, str]
```

## `Stream` — playable media stream

`platform` (e.g. `"youtube"`, `"bandcamp"`, `"radio"`), `url` (fully
formed), `media_type` (`"track"` / `"album"` / `"video"` /
`"playlist"` / `"stream"`), and an optional raw `id`. Aggregated by
`ExternalIds.streams` so player code iterates typed streams instead
of dict-key spelunking.

## `Signals` — disambiguation bag

`mediavocab.Signals` is the *pre-canonical* metadata bag used by
resolvers, scrapers, and dedup pipelines before a full `Work` exists.
~14 fields (`title`, `artist`, `year`, `country`, `runtime`,
`medium`, `language`, `season`, `episode`, `content_genres`,
`variant_kind`, `edition`, `region`, `source_format`,
`fanedit_subtype`, `include_variants`). Distinct from `Work`: no
nested credits / tracklist, no Release inheritance.

Comparison helpers in `mediavocab.models.signals`:

```python
compare_signals(a, b) -> List[SignalConflict]   # overlapping disagreements
merge_signals(*bags)  -> Signals                # first-non-empty wins; genres unioned
match_quality(local, candidate) -> float        # [0, 1]; year/medium mismatches halve
signal_hash(s) -> str                           # canonical-id seed
```

## `MetadataProvider` Protocol

`mediavocab.MetadataProvider` is a `runtime_checkable` `Protocol` —
the typed contract every cross-source resolver provider implements.
No inheritance required:

```python
class MyProvider:
    name: ClassVar[str] = "my_provider"
    media: ClassVar[Set[MediaType]] = {MediaType.MOVIE}
    genre_filter: ClassVar[Set[str]] = set()

    def is_available(self) -> bool: ...
    def lookup(self, signals: Signals) -> Optional[ProviderMatch]: ...
    def matches(self, signals: Signals) -> bool:
        return provider_matches(self, signals)

assert isinstance(MyProvider(), MetadataProvider)   # passes
```

`provider_matches(provider, signals)` is the reference dispatcher
gate — combines a media-type check and a genre-filter check.
`ProviderMatch` carries the provider's typed response;
`ResolutionConflict` records dropped matches.

The runtime registry / dispatcher / consolidator implementation
itself lives in downstream packages (e.g. `metadatarr.resolve`).

> **Caveat — `runtime_checkable` Protocol evolution.** Adding a new
> abstract method to the Protocol is a *silent* breakage for existing
> concrete providers — `isinstance(p, MetadataProvider)` will simply
> start returning `False` for providers that don't implement the new
> method, with no error at registration time. Treat additions as
> breaking changes; ship them in major versions and update every
> known concrete provider in lockstep.

## Decision guide: Work vs Release

| Question | Answer |
|---|---|
| Same film, different cut? | Same Work, different Release (`variant_kind=DIRECTORS`) |
| Same song on two albums? | Same Work, two Appearances in two different Release containers |
| Track 3 in a continuous DJ mix? | `Appearance(work=track, position=3, offset=754.5)` |
| Three films in a Blu-ray box set? | One Release with `contents=[…]`; no synthetic box Work |
| Episode in production order vs broadcast order? | One Work, `episode_orderings={"production":1,"broadcast":11}` |
| BBC Radio 4 primary URL vs backup mirror? | Same Work, two Releases with different URIs |
| 1986 CD vs 2017 remaster of an album? | Same Work, two Releases (`REMASTERED` on the second) |
| Cover version of "Hallelujah"? | Different Work; link with `WorkRelation(kind=COVERS)` |
