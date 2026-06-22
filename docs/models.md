# Models reference

All models are pydantic v2 with `ConfigDict(extra="ignore",
populate_by_name=True)`. Unknown input fields are dropped silently —
flexibility at consumer boundaries.

## `Work` — the canonical creative work

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | Required |
| `media_type` | `MediaType` | Required; pipeline sentinels rejected (T8) |
| `content_form` | `ContentForm` | Default `PRIMARY`; enters `work_hash` (A8b) |
| `year` | `Optional[int]` | Original release/broadcast year of *this* Work |
| `runtime` | `Optional[float]` | Seconds; `None` for stations / paged / interactive |
| `language` | `str` | ISO 639-1 / 639-2; `""` = unknown |
| `original_languages` | `List[str]` | For multi-lingual originals (e.g. Quebec FR+EN) |
| `production_country` | `str` | MOVIE, SHORT_FILM, EPISODIC_SERIES, MUSIC_VIDEO, GAME, IF |
| `publication_country` | `str` | MUSIC, BOOK, COMIC, AUDIOBOOK |
| `broadcaster_country` | `str` | RADIO, TV, PODCAST, AUDIO_DRAMA |
| `season`, `episode` | `Optional[int]` | TV / episodic podcast / comic |
| `series_title` | `Optional[str]` | Container series name (denormalised) |
| `episode_orderings` | `Dict[str, int]` | Alternative orderings (`production`, `broadcast`, …) |
| `variant_kind` | `Optional[VariantKind]` | Work-level restructuring; `None` = canonical (A2) |
| `edition` | `str` | Free text |
| `source_format` | `str` | Original capture: `"35mm"`, `"DAB"`, `"Analogue tape"` |
| `content_genres` | `List[str]` | Free; use `GENRE_*` constants when known |
| `programme_format` | `Optional[ProgrammeFormat]` | Structural format (documentary, concert, stand-up …) |
| `release_status` | `ReleaseStatus` | Defaults to `RELEASED` |
| `aka` | `List[str]` | Alternative spellings; not part of identity hash |
| `localized_titles` | `List[LocalizedTitle]` | Language-tagged titles |
| `credits` | `List[Credit]` | Who contributed |
| `tracklist` | `List[Appearance]` | Canonical track / chapter order |
| `relations` | `List[WorkRelation]` | Work→Work lineage (COVERS, DERIVED_FROM, …) |
| `external_ids` | `Dict[str, str]` | `{"imdb": "tt..."}` |
| `extra` | `Dict[str, str]` | Escape hatch — strings only |

The model validator rejects pipeline sentinels and enforces at most one
country slot non-empty. The `country()` method returns whichever slot is
populated, or `""`.

## `Release` — a specific manifestation

| Block | Fields |
|---|---|
| Reference | `work: Work` |
| Packaging | `packaging: Optional[ReleasePackaging]`, `edition: str`, `region: str` |
| Format identity (T6) | `container`, `codec`, `bitrate`, `platform`, `resolution` |
| Quality (description) | `hdr`, `audio_channels`, `sample_rate`, `frame_rate`, `aspect_ratio`, `color`, `audio_present` |
| Delivery | `stream_mode: StreamMode` |
| Localisation | `audio_language` (identity), `subtitle_languages` (description) |
| Lifecycle | `release_status`, `release_date` |
| Rights | `license: str`, `region_locked: Optional[bool]`, `regions_available: List[str]` |
| Availability | `available_from`, `available_until`, `availability_windows: List[AvailabilityWindow]` |
| Playback | `uri`, `image` |
| Navigation / a11y | `chapters: List[Chapter]`, `accessibility: List[AccessibilityTrack]` |
| Composite | `contents: List[Appearance]` |
| Infrastructure | `label`, `distributor`, `relations: List[ReleaseRelation]` |
| Resolver | `match_confidence: float`, `external_ids`, `extra` |

The model validator enforces (a) ordered, non-overlapping
`availability_windows` with at most one open-ended (must be last); and
(b) `region_locked=False → regions_available` must be empty.

Each cut (theatrical / director's / extended / remaster) is its own
Work (§3.4); `Release.variant_kind` does not exist. The Release-side
distinctions are `packaging` (deluxe / reissue / box-set / bootleg /
regional / promo) and the format-identity block.

`Work.tracklist` is canonical-Work-level (an album's intended track
order). `Release.contents` is manifestation-level (multiple Works
shipped together in a box set / anthology / multi-cut disc).

## `Chapter` — mid-Release marker

`offset` (seconds), `title`, optional `image`, optional `end`,
optional `work_ref`. Chapters are markers, not Works.

## `AccessibilityTrack` — per-Release a11y asset

`kind: AccessibilityKind`, `language: str` (ISO 639-1), `uri`, `forced`,
`sdh`, `note`. Per-Release because the same Work commonly ships
different a11y profiles across editions.

## `AvailabilityWindow` — single (start, end) availability span

`start: Optional[str]`, `end: Optional[str]` (ISO date), `note: str`.
Ordered, non-overlapping; the trailing window may have `end=None`
(open-ended current availability).

## `Appearance` — Work in a container

| Field | Type | Notes |
|---|---|---|
| `work` | `Work` | The contained Work (identity-fields-only stub OK) |
| `position`, `disc` | `int` | Track / chapter / episode within container |
| `offset` | `Optional[float]` | Seconds into the parent Release where this member starts (DJ mixes, megamixes) |
| `title_override` | `Optional[str]` | If re-titled on this Release |
| `length_override` | `Optional[float]` | If runtime differs from `work.runtime` |
| `is_bonus` | `bool` | Bonus track / chapter flag |
| `attributed_to` | `Optional[EntityRef]` | Required on every Appearance of a split release |

## `Entity` — person / group / organisation / series / device

| Field | Notes |
|---|---|
| `name` | Canonical / search spelling |
| `kind` | `EntityKind` |
| `org_kind` | `Optional[OrganisationKind]` — required iff `kind=ORGANISATION` |
| `birth_year`, `death_year` | `Optional[int]` — PERSON-only |
| `memberships` | `List[Membership]` — for GROUP / SERIES |
| `part_of` | `Optional[EntityRef]` — imprint, sub-label, franchise membership |
| `formed`, `disbanded` | `Optional[str]` |
| `years_active` | `List[str]` |
| `external_ids` | `Dict[str, str]` |
| `extra` | `Dict[str, str]` |

The model validator enforces:
- `kind=ORGANISATION ↔ org_kind` set;
- `birth_year` / `death_year` only on `kind=PERSON`;
- `death_year >= birth_year` when both set.

## `Credit` — entity participation in a Work

`role` keeps the raw source string ("Bass Guitar"); `relation_role`
maps to the closed `RelationRole` enum for programmatic routing.
Section: `PRINCIPAL` / `GUEST` / `STAFF`.

## `EntityRef` — a lightweight pointer

`name`, `kind`, `external_ids`, `localized_names: List[Tuple[str, str]]`.

**When to use `EntityRef` vs `Entity`:**

- `EntityRef` — lightweight reference embedded inside a Work's `credits`
  list, `Appearance.attributed_to`, or `Membership.entity`. Use it when
  you know the name and possibly an external ID, but don't have the full
  entity record. `Work.credits` always contains `EntityRef`, never `Entity`.
- `Entity` — the full persistent record (aliases, memberships, birth/death
  years, lifecycle dates). Stored separately in your entity store; linked by
  matching `external_ids` or name when you need the full record.

Resolve `EntityRef` against the consumer's entity store using
`external_ids` overlap (authoritative) or `name` equality (fallback).

## `Membership` — temporal group membership (§5.2)

Two orthogonal facets (A5):

| Field | Notes |
|---|---|
| `entity` | `EntityRef` |
| `roles` | `List[str]` — lowercase free text |
| `kind` | `MembershipKind` — `MEMBER` / `TOURING` / `SESSION` |
| `temporal` | `TemporalState` — `ACTIVE` / `ENDED` / `INACTIVE_GROUP` |
| `date_from`, `date_to` | `Optional[str]` — year or ISO date |
| `note` | `Optional[str]` |

**`date_to=None` does NOT mean "current"** — check `temporal`. A defunct
band's last member has `temporal=INACTIVE_GROUP, date_to=None`. Validator
enforces `ACTIVE → date_to=None`.

## Helpers — `mediavocab.helpers.queries`

```python
# Credit traversal
credits_with_role(work, relation_role) -> List[Credit]
primary_credit(work, relation_role=None) -> Optional[Credit]
director(work) -> Optional[Credit]
author(work)   -> Optional[Credit]
performers(work) -> List[Credit]

# Episode / filmography
episodes_of(series_work, all_works) -> List[Work]
filmography_of(entity_ref, all_works, relation_role=None) -> List[Work]

# WorkRelation / ReleaseRelation traversal
relations_of_kind(work, kind: WorkRelationKind) -> List[WorkRelation]
is_sequel_of(work) -> bool           # True if any SEQUEL_TO relation
is_part_of_series(work) -> bool      # True if any PART_OF relation
all_cuts(work) -> List[WorkRelation] # all DERIVED_FROM relations
release_variants(release) -> List[ReleaseRelation]  # all SUPERSEDES relations
```

These are non-normative convenience wrappers — every consumer could write
them in two lines. They are stable for v1.x — signatures will not change
in minor releases. "Non-normative" means they add no new semantics beyond
what the models already express; they do not introduce new constraints or
side effects. Use them for convenience; don't depend on them for correctness
assertions in your own spec.

## `WorkRelation` — Work→Work links

```python
class WorkRelation(BaseModel):
    kind: WorkRelationKind
    target: Work
    note: Optional[str] = None
```

**When to use `WorkRelation` vs `variant_kind`:**

- `Work.variant_kind` — describes what *this record* is ("this is the
  Director's Cut"). Set it on the record that holds the variant.
- `WorkRelation(kind=DERIVED_FROM, target=original)` — links two records
  together ("this Director's Cut was derived from the Theatrical Cut").
  Set it when you have both records and want to trace the lineage.
- Both can and should coexist: a Director's Cut Work has `variant_kind=DIRECTORS`
  AND a `WorkRelation(DERIVED_FROM, target=theatrical_work)`.

The `target` is a `Work` populated with only identity fields — don't
recurse into the target's own `relations`, `tracklist`, or `credits`.

## `ReleaseRelation` — Release→Release links

```python
class ReleaseRelation(BaseModel):
    kind: ReleaseRelationKind
    target: Release
    note: Optional[str] = None
```

**WorkRelation vs ReleaseRelation:**

- `WorkRelation` — conceptual link between *creative works* (this film is a
  sequel of that film; this cover is derived from the original recording).
- `ReleaseRelation` — format-level link between *manifested releases* (this
  4K remaster supersedes the original DVD release; this stream is a mirror of
  the broadcast).

| `ReleaseRelationKind` | Semantics |
|---|---|
| `SUPERSEDES` | Newer release replaces an earlier one |
| `PORT_OF` | Platform port of the same base game / IF |
| `MIRROR_OF` | Alternate stream of the same broadcast |
| `DERIVED_FROM` | Generic catch-all |

Use sparingly — most distinctions are encoded by format / packaging
plus `release_hash`.

## `License` — typed rights

`Release.license` accepts either a plain SPDX-style string or a `License`
object. Strings are coerced to `License.from_spdx()` on intake:

```python
from mediavocab import Release, Work, MediaType

r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
            license="CC-BY-SA-4.0")
r.license.attribution   # True
r.license.share_alike   # True
r.license.commercial    # True
r.license.is_open()     # True
```

Well-known constants in `mediavocab.models.license`:
`ALL_RIGHTS_RESERVED`, `PUBLIC_DOMAIN`, `CC0`, `CC_BY`, `CC_BY_SA`,
`CC_BY_NC`, `CC_BY_NC_SA`, `CC_BY_ND`, `CC_BY_NC_ND`. Free-function
predicates (`is_open`, `requires_attribution`, `allows_commercial`, etc.)
operate directly on SPDX strings — see spec §7.2.

## `ExternalIds` — optional typed external identifiers

`mediavocab.ExternalIds` is a typed companion to the canonical
`Dict[str, str]` form. Known fields plus an `extra: Dict[str, Any]`
escape hatch for provider-specific IDs.

```python
ids = ExternalIds(isbn_10="0-261-10328-8")
ids.isbn_13       # auto-paired: "9780261103283"
ids.merge(other)  # first-writer-wins
ids.streams       # → List[Stream] expanded from URL/ID keys in `extra`
ids.to_dict()     # plain Dict[str, str]
```

On `Work` and `Release` models, use the `external_ids_model` property
to dynamically access or update `external_ids` using this typed model
instance:

```python
# Access
typed_ids = my_work.external_ids_model
# Update
my_work.external_ids_model = typed_ids
```

`extra` accepts any JSON-serialisable type (str, int, float, bool, list,
dict). Common keys: `"cover_url"`, `"feed_url"`, `"image_url"`, `"slug"`,
`"soundcloud_track_url"`, `"bandcamp_track_url"`, `"youtube_video_id"`.

Note: when using `Work.from_signals()` to construct a Work, non-standard
signal hints (like display-level artist names) are stored in the `extra`
field under a structured `signals_meta` dictionary (e.g.,
`extra["signals_meta"]["artist"]`).

`KNOWN_EXTERNAL_IDS` (exported from `mediavocab`) is a frozenset of every
well-known key string — the `ALL_KNOWN_KEYS` constants plus every typed
`ExternalIds` field name — for O(1) membership testing.

## `Stream` — playable media stream

`platform` (e.g. `"youtube"`, `"bandcamp"`, `"radio"`), `url`, `kind`
(`"track"` / `"album"` / `"video"` / `"playlist"` / `"stream"` — the
platform's *asset category*, distinct from mediavocab `MediaType`),
optional raw `id`. Aggregated by `ExternalIds.streams`.

## `Signals` — resolver pipeline bag

`mediavocab.Signals` exists only in the resolver pipeline — it is not a
persisted record. Persisted records are `Work`s. Use lifecycle constructors
to make the role explicit:

```python
from mediavocab import Signals, SignalsRole

query = Signals.as_query(title="Inception", year=2010, medium=MediaType.MOVIE)
obs   = Signals.as_observation(title="Inception", year=2010, runtime=8880.0)
result = merge_signals(query, obs).as_result()

assert query.role  == SignalsRole.QUERY
assert obs.role    == SignalsRole.OBSERVATION
assert result.role == SignalsRole.RESULT
```

Fields: `title`, `artist`, `year`, `country`, `runtime`, `medium`,
`language`, `season`, `episode`, `content_genres`, `variant_kind`,
`edition`, `region`, `source_format`, `fanedit_subtype`,
`include_variants`, `playback_type`, `role`.

`Signals.country` is a single field (resolver-side hint), distinct from the
three country slots on `Work`.

Comparison helpers:

```python
compare_signals(a, b) -> List[SignalConflict]   # overlapping disagreements
merge_signals(*bags)  -> Signals                # first-non-empty wins; genres unioned
match_quality(local, candidate) -> float        # [0, 1]
signal_hash(s) -> str                           # canonical-id seed
```

## `MetadataProvider` ABC

`mediavocab.MetadataProvider` is the abstract base every concrete
provider inherits from. Three routing `ClassVar` axes (A6):

```python
class MyProvider(MetadataProvider):
    name: ClassVar[str] = "my_provider"
    media: ClassVar[Set[MediaType]] = {MediaType.MOVIE}
    playback_type: ClassVar[Set[PlaybackType]] = set()
    genre_filter: ClassVar[Set[str]] = set()   # values from KNOWN_GENRES

    def is_available(self) -> bool: ...
    def lookup(self, signals: Signals) -> Optional[ProviderMatch]: ...
```

`provider_matches(provider, signals)` is the three-axis gate. A provider
with `playback_type = {PlaybackType.AUDIO}` is skipped when
`signals.playback_type == PlaybackType.VIDEO`. Empty sets are universal
on that axis. Genre strings in `genre_filter` should be values from
`KNOWN_GENRES`; unknown strings emit a `WARNING` at class-definition time.

Full walkthrough: [Writing a metadata provider](./patterns/writing-a-provider.md).

## Decision guide: Work vs Release

See spec §5.7 — the canonical table is maintained there.
