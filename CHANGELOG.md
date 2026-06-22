# Changelog

## 1.0.0 — 2026-05-11

First public release. Reference vocabulary and pydantic data model for
cataloguing media works: movies, music, books, comics, games, podcasts,
audio dramas, radio, sound effects, procedural ambient, playlists.

### Spec (`docs/mediavocab_spec.md`)

A formal specification derives every label from a small axiom set.
Section order:

§1 First principles → §2 Axioms and theorems → §3 Axes → §4 Labels
→ §5 Models → §6 Operations → §7 Identifiers and rights → §8 Versioning
→ §9 Patterns

Every term used in section N is defined in section ≤ N. Eight
independent axioms (A1–A8) plus eight labelled theorems (T1–T8) with
one-line proofs.

### Taxonomy

- **`MediaType`** — 17 concrete values (`MOVIE`, `SHORT_FILM`,
  `EPISODIC_SERIES`, `TV`, `MUSIC`, `MUSIC_VIDEO`, `PODCAST`, `AUDIOBOOK`,
  `AUDIO_DRAMA`, `RADIO`, `BOOK`, `COMIC`, `GAME`, `INTERACTIVE_FICTION`,
  `SOUND_EFFECT`, `PROCEDURAL_AMBIENT`, `PLAYLIST`) + 3 pipeline sentinels
  (`GENERIC` / `NOT_MEDIA` / `CONTROL`) rejected at `Work` construction
  (T8).
- **`VariantKind`** — Work-level restructuring (theatrical, director's,
  fanedit, remaster, …). Each cut is its own `Work` linked by
  `WorkRelation`.
- **`ReleasePackaging`** — Release-level packaging (`DELUXE`, `REISSUE`,
  `REGIONAL`, `BOOTLEG`, `BOX_SET`, `PROMO`, `OTHER`).
- **`ContentForm`** — experiential kind (`PRIMARY` / `TRAILER` /
  `TEASER` / `EXCERPT` / `BEHIND_SCENES` / `REACTION` / `SOCIAL_CLIP` /
  `SUPPLEMENT` / `OTHER`). The one human-perception axis admitted to
  identity (A8b).
- **`EntityKind`** + **`OrganisationKind`** — `PERSON` / `GROUP` /
  `ORGANISATION` / `SERIES` / `DEVICE` / `OTHER`, plus
  `LABEL` / `PUBLISHER` / `STUDIO` / `BROADCASTER` / `DEVELOPER` /
  `STREAMING_SERVICE` / `DISTRIBUTOR` / `OTHER` for organisation
  sub-types.
- **`MembershipKind`** + **`TemporalState`** — orthogonal facets (A5):
  `MEMBER` / `TOURING` / `SESSION` for role-shape; `ACTIVE` / `ENDED` /
  `INACTIVE_GROUP` for time-state.
- **`ProgrammeFormat`** — `CONCERT` / `STAND_UP` / `TALK_SHOW` /
  `REALITY` / `NEWS` / `SPORTS` / `QUIZ` / `DOCUMENTARY` / `OTHER`.
  Routing axis on `Work.programme_format`; excluded from `work_hash`.
- **`AccessibilityKind`** — `SUBTITLES` / `CAPTIONS` /
  `AUDIO_DESCRIPTION` / `SIGN_LANGUAGE` / `TRANSCRIPT` / `LYRICS`.
- **`PlaybackType`** — derived routing axis (`AUDIO` / `VIDEO` / `PAGED`
  / `INTERACTIVE` / `UNKNOWN`); never persisted on Work or Release.
- **`StreamMode`** — `ON_DEMAND` / `LIVE` / `CONTINUOUS`. Delivery, not
  identity (A3).
- **`ReleaseStatus`** — `RELEASED` / `ANNOUNCED` / `IN_PRODUCTION` /
  `CANCELLED` / `WITHDRAWN` / `UNKNOWN`.
- **`WorkRelationKind`** + **`ReleaseRelationKind`** — Work→Work and
  Release→Release lineage typed enums.
- **`content_genres`** — open-vocabulary string list with canonical
  spellings in `mediavocab.taxonomy.genre`.

### Models

- **`Work`** — canonical creative artefact. Required `media_type`
  (T8 rejects sentinels); three country slots (`production_country` /
  `publication_country` / `broadcaster_country`) with exclusivity
  validator; `season` / `episode` / `series_title` /
  `episode_orderings` for episodic media; `variant_kind` for
  Work-level restructurings; `programme_format` for structural format;
  `relations: List[WorkRelation]`.
- **`Release`** — manifestation of a Work. Format identity
  (`container`, `codec`, `bitrate`, `platform`, `resolution`,
  `audio_language`); `packaging` for description-layer edition;
  `region_locked` ↔ `regions_available` validator; ordered
  non-overlapping `availability_windows`; `chapters`, `accessibility`,
  `contents` (composite box-sets); `relations:
  List[ReleaseRelation]`.
- **`Entity`** — person / group / organisation / series / device.
  `org_kind` required when `kind=ORGANISATION`; `birth_year` /
  `death_year` PERSON-only.
- **`Membership`** — `kind` × `temporal` orthogonal facets;
  `date_to=None` does NOT imply *current*.
- **`Credit`** — entity contribution to a Work; preserved
  editorial-order list.
- **`Appearance`** — Work in a container Release / parent Work;
  `attributed_to` for split releases.
- **`Programme`** + **`Schedule`** — broadcast EPG models with
  ordered-non-overlapping validation.
- **`Chapter`**, **`AccessibilityTrack`**, **`AvailabilityWindow`**,
  **`LocalizedTitle`** — per-Release navigation, accessibility, and
  localisation models.
- **`WorkRelation`**, **`ReleaseRelation`** — typed lineage pointers.

### Operations

- **`work_hash`** — stable SHA-256 over identity fields per §6.3.
  Inputs: `normalise_title(title)`, `media_type`, `content_form`, year,
  country slot, language, quantum-rounded runtime, season, episode,
  `normalise_title(series_title)`, `variant_kind`, `edition`,
  `source_format`. Frozen for v1.x.
- **`release_hash`** — stable SHA-256 per §6.4. Inputs: parent
  `work_hash`, region, container, codec, bitrate, platform, resolution,
  audio_language.
- **`RUNTIME_HASH_QUANTUM_S`** with `QUANTUM_SKIP = -1` sentinel —
  per-MediaType tolerance is the hash quantum; providers within
  tolerance hash identically.
- **`compare`** — overlapping field disagreements; absence is unknown,
  not conflict.
- **`score`** — title-fuzzy primary, hard halves on year /
  `MediaType` / `ContentForm` / country / language mismatch, bonuses
  for variant / programme_format agreement and genre overlap.
- **`merge`** + **`merge_releases`** — first-non-empty-wins per scalar;
  `MergeStrategy` for title/edition tie-breakers and
  `provider_priority`; `IdentityConflict` raised in strict mode on
  identity disagreement; `release_status` collapses to
  highest-confidence (RELEASED > WITHDRAWN > ANNOUNCED >
  IN_PRODUCTION > CANCELLED > UNKNOWN).
- **Identity-input primitives** (§6.1): `normalise_title`,
  `normalise_edition`, `normalise_format`, `normalise_country`,
  `normalise_language` for consumers building their own hashes.

### Identifiers and rights

- **`external_ids: Dict[str, str]`** with module-level constants
  (`imdb`, `tmdb`, `musicbrainz_recording`, `isrc`, `isbn`, `igdb`, …)
  frozen for v1.x. Optional `ExternalIds` typed view with ISBN
  auto-pairing and `merge()`.
- **`Release.license: str`** with SPDX-style identifiers. Free-function
  predicates `is_open`, `is_public_domain`, `requires_attribution`,
  `allows_commercial`, `allows_derivatives`, `allows_share_alike` cover
  the Creative Commons family, GPL family, MIT, BSD, Apache, MPL, ISC,
  and Unlicense. Conservative defaults for unrecognised identifiers.
- **`Stream`** view helper — typed (`platform`, `url`, `kind`, `id`)
  derived from `ExternalIds.extra` provider URL / ID keys.

### Provider protocol

- **`MetadataProvider`** ABC with four-axis routing gate (A6): `media`
  × `playback_type` × `content_form` × `genre_filter` `ClassVar` sets.
  Empty set on any axis means "universal".
- **`ProviderMatch`** carries `confidence`, `signals`, `external_ids`.
- **`Signals`** is the resolver-pipeline bag (query → observation →
  consensus); not a persisted record.

### Text utilities

- **Normalisation** — `strip_diacritics`, `normalize`, `fuzzy_ratio`,
  `best_match`, `title_words`, plus the five identity-input primitives.
- **ISO helpers** — `validate_language`, `validate_country`,
  `normalize_language`, `normalize_country` (accept 639-1/639-2/full
  name; 3166-1 alpha-2/full name).
- **ISBN** — `isbn10_to_13`, `isbn13_to_10`, `normalize_isbn` with
  978-prefix awareness.
- **Title parser** — `parse_title` extracts year, season/episode,
  cuts (variant_kind), packaging (deluxe/criterion/anniversary),
  source format, language hint, alternative titles.
- **Content classifier** — `classify_video` returns a `ContentType`
  from title + description heuristics; `ContentType.to_routing()`
  projects onto `(MediaType, ContentForm, content_genres,
  ProgrammeFormat)`.
- **ISO date** — `parse_iso_date`, `iso_compare`, `IsoDate` annotated
  type for partial dates (year-only, year-month, full date,
  datetime-with-offset).

### Helpers

- `is_not_media`, `is_generic`, `is_control` — sentinel predicates on
  `MediaType`.
- `is_device_entity`, `is_continuous_release` — routing predicates.
- `primary_credit`, `director`, `author`, `performers`,
  `credits_with_role` — credit-list shortcuts.
- `episodes_of`, `filmography_of` — list-walking helpers.
- `quality_score`, `best_release` — sortable release ranking.

### Locale

- `.voc` keyword vocabularies for title-parsing and content-classifier
  heuristics in 7 locales (`en-us`, `pt-br`, `pt-pt`, `pt`, `es`,
  `es-es`, `es-mx`, `fr-fr`, `it-it`, `nl-nl`).
- Fallback chain: exact match → language-only → `en-us`.

### Examples

19 standalone example scripts covering the full surface: building a
movie / album / radio station / interactive fiction, band lineup with
temporal memberships, chapter and accessibility tracks, box sets and
quality ranking, license and rights filtering, credits and queries,
playlists with curator credit, resolver primitives, programme schedule
EPG, release relation lineage, playback-type routing, ContentType
classifier, signals pipeline roles.

### Documentation

- Full spec at `docs/mediavocab_spec.md` (2,150+ lines).
- Reference: `docs/quickstart.md`, `docs/models.md`,
  `docs/taxonomy.md`, `docs/text-utilities.md`.
- 16 pattern docs in `docs/patterns/`: adult media, games, interactive
  fiction, soundtracks, motion comics, independent creators / AI
  content, reader-paced content, accessibility, box sets, format /
  quality / rights / availability, playlists and channels, IoT
  devices, radio, scheduling, playback-type routing, writing a
  metadata provider.
