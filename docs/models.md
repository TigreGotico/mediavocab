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
Resolve against the consumer's entity store. Distinct from
`Work` / `Release` references — those pass the full model with identity
fields populated only.

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
episodes_of(series_work, all_works) -> List[Work]
filmography_of(entity_ref, all_works, relation_role=None) -> List[Work]
quality_score(release) -> tuple
best_release(*releases) -> Optional[Release]
```

`quality_score` is a tuple: Work-level variant preference (director's >
extended > preservation > remastered > upscaled > colorized >
theatrical > fanedit > compilation > other), Release packaging (deluxe
> box_set > reissue > regional > promo > other > bootleg), resolution,
HDR, audio channels, sample_rate.

`best_release` picks the highest tuple; list order breaks ties.

## `WorkRelation` — Work→Work links

```python
class WorkRelation(BaseModel):
    kind: WorkRelationKind
    target: Work
    note: Optional[str] = None
```

The `target` is a `Work` populated with only identity fields — wire-format
recursion is bounded by consumer convention (don't recurse into the
target's own `relations`, `tracklist`, or `credits`).

## `ReleaseRelation` — Release→Release links

```python
class ReleaseRelation(BaseModel):
    kind: ReleaseRelationKind
    target: Release
    note: Optional[str] = None
```

| `ReleaseRelationKind` | Semantics |
|---|---|
| `SUPERSEDES` | Newer release replaces an earlier one |
| `PORT_OF` | Platform port of the same base game / IF |
| `MIRROR_OF` | Alternate stream of the same broadcast (different bitrate / transmitter) |
| `DERIVED_FROM` | Generic catch-all |

Use sparingly — most distinctions are encoded by format / packaging
plus `release_hash`.

## `Programme` — broadcast slot

A single airing of a Work on a broadcast channel. Per T4 the channel is
itself a Work (a RADIO or TV station).

| Field | Type | Notes |
|---|---|---|
| `work` | `Work` | Content Work being aired |
| `channel` | `Work` | Broadcast channel Work (RADIO / TV) |
| `starts_at` | `IsoDate` | RFC 3339 / ISO 8601 with offset |
| `ends_at` | `Optional[IsoDate]` | Only the trailing slot may be `None` |
| `runtime` | `Optional[float]` | Seconds |
| `is_live` | `bool` | |
| `is_repeat` | `bool` | |

## `Schedule` — EPG window for a channel

| Field | Notes |
|---|---|
| `channel` | `Work` |
| `programmes` | `List[Programme]` — sorted by `starts_at`, non-overlapping |
| `valid_from`, `valid_until` | `Optional[IsoDate]` |
| `source` | Provider hint (`"tunein"`, `"tvmaze"`, `"epg.xml"`) |
| `fetched_at` | `Optional[IsoDate]` |

Validator enforces ordering, non-overlap, and the "only last may be
open-ended" rule. Schedules are append-only at the model level; replace
wholesale to refresh.

## `License` — optional typed rights overlay

`mediavocab.models.license.License` is a Pydantic companion to the
canonical `Release.license: str`. The string stays the source of
truth (A7); the typed view is parse-only.

```python
from mediavocab.models.license import License

lic = License.from_spdx("CC-BY-SA-4.0")
lic.attribution     # True
lic.share_alike     # True
lic.commercial      # True (only NC variants set this False)
lic.is_open()       # True
```

For unrecognised identifiers all flags return the most-restrictive
answer (see spec §7.2).

## `ExternalIds` — optional typed external identifiers

`mediavocab.ExternalIds` is a typed companion to the canonical
`Dict[str, str]` form. Known fields plus an `extra: Dict[str, str]`
escape hatch.

```python
ids = ExternalIds(isbn_10="0-261-10328-8")
ids.isbn_13       # auto-paired: "9780261103283"
ids.merge(other)  # first-writer-wins
ids.streams       # → List[Stream] expanded from URL/ID keys in `extra`
ids.to_dict()     # plain Dict[str, str]
```

## `Stream` — playable media stream

`platform` (e.g. `"youtube"`, `"bandcamp"`, `"radio"`), `url`, `kind`
(`"track"` / `"album"` / `"video"` / `"playlist"` / `"stream"` — the
platform's *asset category*, distinct from mediavocab `MediaType`),
optional raw `id`. Aggregated by `ExternalIds.streams`.

## `Signals` — resolver pipeline bag

`mediavocab.Signals` exists only in the resolver pipeline — it is not a
persisted record. Persisted records are `Work`s. The same shape carries
three roles:

1. **Query** (caller → resolver) — what the caller knows.
2. **Observation** (provider → consolidator) — what the provider believes.
3. **Consensus** (consolidator → caller) — the merged result.

Fields: `title`, `artist`, `year`, `country`, `runtime`, `medium`,
`language`, `season`, `episode`, `content_genres`, `variant_kind`,
`edition`, `region`, `source_format`, `fanedit_subtype`,
`include_variants`, `content_form`, `playback_type`.

`Signals.country` is a single field (resolver-side query / observation
hint), distinct from the three slots on `Work`. The consolidator
canonicalises onto the correct slot when building a Work from a
resolved bag.

Comparison helpers in `mediavocab.models.signals`:

```python
compare_signals(a, b) -> List[SignalConflict]   # overlapping disagreements; skips playback_type
merge_signals(*bags)  -> Signals                # first-non-empty wins; genres unioned
match_quality(local, candidate) -> float        # [0, 1]; year/medium mismatches halve
signal_hash(s) -> str                           # canonical-id seed (excludes playback_type)
```

## `MetadataProvider` ABC

`mediavocab.MetadataProvider` is the abstract base every concrete
provider inherits from. Four routing `ClassVar` axes (A6):

```python
class MyProvider(MetadataProvider):
    name: ClassVar[str] = "my_provider"
    media: ClassVar[Set[MediaType]] = {MediaType.MOVIE}
    playback_type: ClassVar[Set[PlaybackType]] = set()
    content_form: ClassVar[Set[ContentForm]] = set()
    genre_filter: ClassVar[Set[str]] = set()

    def is_available(self) -> bool: ...
    def lookup(self, signals: Signals) -> Optional[ProviderMatch]: ...
```

`provider_matches(provider, signals)` is the four-axis gate. A provider
with `playback_type = {PlaybackType.AUDIO}` is skipped when
`signals.playback_type == PlaybackType.VIDEO`. Empty sets are universal
on that axis.

Full walkthrough: [Writing a metadata provider](./patterns/writing-a-provider.md).

> **Note — ABC evolution.** Adding a new abstract method is a breaking
> change for every concrete provider. Ship additions in major versions
> and update all known providers in lockstep.

## Decision guide: Work vs Release

See spec §5.7 — the canonical table is maintained there.
