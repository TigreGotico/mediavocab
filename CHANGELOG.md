# Changelog

## 0.3.0 — unreleased

Closing the gap list from the post-0.2 audit.

### Models

- **`Programme` + `Schedule`** — first-class EPG / broadcast-schedule
  models for live linear `MediaType.TV` / `MediaType.RADIO` channels.
  `Programme` is a slot (Work × channel × time); `Schedule` is the
  ordered slot list for a single channel over a window. Spec §5.9.
- **`ReleaseRelation` + `ReleaseRelationKind`** — per-edition lineage
  parallel to `WorkRelation`. Kinds: `SUPERSEDES`, `REMASTER_OF`,
  `REISSUE_OF`, `PORT_OF`, `DERIVED_FROM`. Spec §6.1.
- **`License`** — typed companion to `Release.license: str`. Captures
  the four orthogonal CC rights (attribution / share_alike /
  commercial / derivatives) plus a `is_public_domain` flag and an
  `is_open()` predicate. `License.from_spdx()` parses the well-known
  CC family + PD/CC0; unknown identifiers stay restricted. Spec §5.8.
- **`EntityRef.localized_names`** — `List[Tuple[str, str]]` of
  `(name, ISO 639-1)` for cross-locale credit matching (kanji ↔
  romaji ↔ English transliteration). Not part of identity.
- **`Work.original_languages`** — `List[str]` for multi-language
  originals (Quebec film FR+EN, simulcast anime JP+EN). The singular
  `Work.language` remains the primary; `original_languages` carries
  the full list when the work was authored in several at once.
- **`Release.availability_windows`** — `List[Tuple[from, until]]`
  for cycled availability ("Disney vault"). The simple single-window
  case stays in `available_from` / `available_until`.
- **`Chapter.work_ref`** — optional `EntityRef` pointing at a
  distinct Work whose region this chapter delineates (podcast
  episode whose chapters are interview Work + monologue Work). When
  `None` the chapter is purely a navigation aid.

### Taxonomy

- **`WorkRelationKind.DLC_FOR` / `EXPANSION_OF`** — game-shaped
  relation kinds. DLC ships as its own Work tied to a base via
  `DLC_FOR`; standalone expansions use `EXPANSION_OF`.

### Helpers (`mediavocab.helpers.queries`)

- **`episodes_of(series, all_works)`** — episodes belonging to a
  series, sorted by `(season, episode)`.
- **`filmography_of(entity_ref, all_works, role=None)`** — Works on
  which an entity is credited. Match by external-id overlap, fall
  back to name equality.
- **`quality_score(release)` / `best_release(*releases)`** — typed
  preference rules for "play me the highest quality available".
  Variant preference (DIRECTORS > THEATRICAL, BOOTLEG loses)
  composes with resolution / HDR / audio channels / sample rate.

### Spec

- Spec §6.1 closes "ReleaseRelation belongs to a future version" —
  formalised here.
- Spec §5.5 documents `Work.original_languages` alongside `language`.
- Spec §5.6 documents `Release.availability_windows`.
- Spec §5.8 documents `License`.
- Spec §5.9 documents `Programme` + `Schedule`.

## 0.2.0 — unreleased

Spec maturation pass. All changes are spec-driven; no published consumers
yet, so the migration is direct.

### Added

- **`ExternalIds`** — typed Pydantic model promoted from metadatarr.
  Lives in ``mediavocab.models``. Offers ~50 known fields, automatic
  ISBN-10/ISBN-13 pairing on construction, ``merge()`` with
  first-writer-wins semantics, ``is_empty()``, ``to_dict()`` /
  ``from_dict()`` round-trip, and a ``streams`` property that expands
  known ID keys (``youtube_video_id``, ``bandcamp_track_url`` …) into
  typed ``Stream`` objects. The free-form ``Dict[str, str]`` shape on
  ``Work.external_ids`` / ``Release.external_ids`` / ``Entity.external_ids``
  remains the canonical persisted form; the typed model is a
  validation/ergonomics overlay. Resolves spec Q4 for external_ids.
- **`Stream`** — uniform playable-stream model
  (``platform``, ``url``, ``media_type``, ``id``). Aggregated by
  ``ExternalIds.streams`` for player code that wants a typed iterable
  rather than dict-key spelunking.
- **`mediavocab.text.isbn`** — pure-stdlib helpers ``isbn10_to_13``,
  ``isbn13_to_10``, ``normalize_isbn``. Books / audiobooks / comics
  consumers had been duplicating these.
- **`Signals`** — flat disambiguation bag (~14 fields) used by
  resolvers, scrapers, and dedup pipelines before a full ``Work``
  exists. Lifted from metadatarr; ships with ``compare_signals``,
  ``merge_signals``, ``match_quality``, ``signal_hash`` so every
  consumer cross-source resolver shares the same comparison /
  merging / hashing semantics.
- **`MetadataProvider` Protocol + `ProviderMatch` + `ResolutionConflict`**
  — the typed resolver-provider contract, in
  ``mediavocab.models.protocols``. ``MetadataProvider`` is a
  ``runtime_checkable`` ``Protocol`` (no inheritance required); the
  registry / dispatcher / consolidator stay in downstream packages.
  Includes a reference ``provider_matches(provider, signals)``
  implementation so cross-package routing is consistent.
- **`MediaType.PLAYLIST`** — cross-media-type curated collection
  (Spotify playlist, YouTube playlist, M3U file, OPML podcast bundle).
  Distinct from `MUSIC + variant_kind=COMPILATION` (which is for
  single-media-type *published* compilations). Pattern doc:
  ``docs/patterns/playlists-and-channels.md``. 18 MediaType values
  total.
- **`RelationRole.CURATOR`** — for someone who selected and ordered
  other people's works without creating them (playlist curator,
  anthology editor). Distinguishes selection-as-value from
  creation-as-value.
- **`release_hash(release)`** — companion to ``work_hash``. Combines
  ``work_hash(release.work)`` with the release-level identity fields
  (variant_kind, edition, region, container/codec/quality/platform,
  audio_language). Use as a per-edition dedup seed.
- `MediaType.EPISODIC_SERIES` for on-demand ordered episodes (anime, drama,
  sitcom, web series). `MediaType.TV` is now reserved for live linear /
  IPTV broadcast channels (parallel to `RADIO`, channel-as-Work). The
  17-value enum split makes the runtime-tolerance and routing semantics
  honest — episodic content gets ±30s, broadcast channels get 0s.
- `WorkRelationKind.FANEDIT_OF` to link a fanedit Work back to its source.
  Pair with `Work.variant_kind` (`FANEDIT`, `TV_TO_MOVIE`, `MOVIE_TO_TV`)
  to express the kind of recut.
- `mediavocab.text.parse_title` and `mediavocab.text.classify_video` —
  pure string→struct primitives lifted from tutubo. Returns `VariantKind`
  / `ContentType` directly. Locale-aware via `mediavocab.locale.voc_regex`
  with a stateless `lang=` parameter (no global mutable state — safe for
  concurrent callers).
- `mediavocab.locale` package: `.voc` keyword vocabularies for en-us, es,
  es-es, es-mx, fr-fr, it-it, nl-nl, pt, pt-br, pt-pt. Adding a language
  is a `.voc` drop, no Python changes.
- `mediavocab.taxonomy.ContentType` — finer-grained classifier output
  with `to_media_type()` bridge to the canonical 17-value `MediaType`.
- Spec axiom 12 ("one Work, one MediaType. Distribution forks Releases,
  not Works") and §7.2 mutability/immutability contract for canonicalised
  Works.
- §4.1 4-step classifier for `MUSIC` / `SOUND_EFFECT` / `AMBIENT_SOUNDS`
  to disambiguate when an asset could plausibly fit multiple types.

### Changed

- `MembershipStatus.LIVE` renamed to `MembershipStatus.TOURING` to avoid
  collision with `StreamMode.LIVE` and `WorkRelationKind.LIVE_VERSION`
  — three different "live" semantics in scope at once was confusing.
- Spec §5.6: `Release` inheritance reworded — Release has no identity
  fields of its own; identity is read through `release.work`.
- Spec §6 closed Q1 — `WorkRelation` is no longer "deferred"; the model
  ships in `mediavocab.models`.
- `Release.bitrate` semantics tightened (audio fidelity only;
  resolution-shaped values were a category error).
- `Release.region_locked` is now `Optional[bool]` — `None` distinguishes
  "unknown" from "worldwide".
- §7.2 `compare()` doc enumerates compared fields explicitly; `score()`
  episodic-media list updated for the EPISODIC_SERIES split.

### Removed

- `EntityKind.EVENT` (use `OTHER` + `extra["event_type"]`).
- `Credit.position` (list order is editorial credit order; no separate
  field needed).
- `Release.credits` (always read through `release.work.credits`).
- `WorkRelationKind.PROMOTES` / `DELETED_SCENE` (collapsed into
  `BONUS_FOR` with a free `note` field).
- `MediaType.STAGE` (use `MOVIE + GENRE_STAND_UP` for recordings; live-
  in-venue productions are `docs/patterns/stage.md`).

### Spec docs

- §1.1 / §8 are now project-agnostic — no hard refs to consumer
  packages. Application patterns live in `docs/patterns/`.
- New per-MediaType `Work.country` convention table.
- Tightened `runtime` / `language` / `country` field comments.

## 0.1.0 — 2026-05-07

Initial PyPI release. Folds the 0.2 and 0.3 unreleased sections into the
shipped baseline.

### Spec

- Axiom 1 refined: a `MediaType` earns its place by changing the schema
  *and* when no orthogonal axis would fit. Adding the axis is the first
  question; adding a `MediaType` value is the second.
- New axiom 13 (orthogonality): routing axes are typed fields / ClassVars,
  not `MediaType` values. Identity is `(media + identity-fields)`; the
  resolver gate is `(media, modality, content_genres, …)`.
- New axiom 14 (provider hygiene): output flows through typed fields *or*
  `extra` — never both. Consolidator dedup assumes one source of truth
  per fact.
- New §4.10 `PlaybackModality` — defines the enum, the default
  `MediaType → Modality` mapping, and the routing rule. No `DEVICE`
  modality (devices are `EntityKind.DEVICE`, axiom 4).
- New §5.10 Signals scope — `Signals` is exclusively for the resolver
  pipeline (query / observation / consensus); the taxonomy and
  `Work` / `Release` / `Entity` models do not use it.
- New §10.2 `extra` escape-hatch contract: strings preferred, lists /
  numbers tolerated for legacy fields, no identity participation,
  provider-namespaced keys.
- §6.1 documents `ReleaseRelation` (per-edition lineage parallel to
  `WorkRelation`).

### Taxonomy

- **`PlaybackModality`** enum (`AUDIO`, `VIDEO`, `INTERACTIVE`, `TEXT`,
  `UNKNOWN`) plus `MEDIA_TYPE_TO_MODALITY` lookup and `infer_modality()`
  helper, in `mediavocab.taxonomy.modality`.
- **`ContentType.to_routing()`** returns `(MediaType, content_genres)` —
  the canonical input for the resolver two-axis gate. Old
  `to_media_type()` is preserved but lossy.
- `ContentType` routing fixes: `TRAILER`, `BEHIND_THE_SCENES`, `REACTION`,
  `TUTORIAL`, `GAMING`, `COMPILATION`, `KIDS`, `SOCIAL_CLIP`, `SPORT`,
  `NEWS`, `LIVE`, `UPCOMING`, `VIDEO` now map to `MediaType.GENERIC` plus
  a genre tag instead of `MediaType.MOVIE`. `MOVIE` is reserved for
  feature-length narrative film per axiom 1.
- 18-value `MediaType`: adds `PLAYLIST`, splits `EPISODIC_SERIES` from
  live linear `TV` / `RADIO`.

### Models

- **`Signals.modality`** — query-only field. Never participates in
  `compare_signals` / `merge_signals` / `signal_hash` (it is a query
  hint, not an observation).
- **`MetadataProvider`** is now an ABC (was `runtime_checkable` Protocol).
  Stub providers that do not subclass no longer `isinstance()` pass;
  forgetting an abstract method raises at instantiation. Three-axis
  `matches()` gate on `(media, modality, genre_filter)`, each axis
  short-circuiting independently.
- **`Programme` + `Schedule`** — first-class EPG / broadcast-schedule
  models for live linear `TV` / `RADIO` channels.
- **`ReleaseRelation` + `ReleaseRelationKind`** — per-edition lineage
  (`SUPERSEDES`, `REMASTER_OF`, `REISSUE_OF`, `PORT_OF`, `DERIVED_FROM`).
- **`License`** — typed companion to `Release.license: str`. Captures
  the four orthogonal CC rights plus `is_public_domain` and
  `is_open()`. `License.from_spdx()` parses the CC family + PD/CC0.
- **`Release.parsed_license`** — read-only typed view of the persisted
  license string via `License.from_spdx`.
- **`EntityRef.localized_names`** — `List[Tuple[str, str]]` of
  `(name, ISO 639-1)` for cross-locale credit matching. Not part of
  identity.
- **`Work.original_languages`** — `List[str]` for multi-language
  originals; `Work.language` remains the primary.
- **`Release.availability_windows`** — `List[Tuple[from, until]]` for
  cycled availability ("Disney vault").
- **`Chapter.work_ref`** — optional `EntityRef` pointing at a distinct
  Work whose region this chapter delineates.
- **`ExternalIds`** — typed Pydantic model with ~50 known fields,
  automatic ISBN-10 ↔ ISBN-13 pairing on construction, `merge()` with
  first-writer-wins semantics, and a `streams` property aggregating
  per-platform `Stream` models.
- **`Stream`** — uniform playable-stream model.

### Validators

- **`IsoDate`** annotated string validates ISO-8601 date / datetime
  strings on field assignment. Applied to `Release.release_date` /
  `available_from` / `available_until` / `availability_windows`,
  `Programme.starts_at` / `ends_at`, and `Schedule.valid_from` /
  `valid_until` / `fetched_at`. Empty / `None` still pass through.

### Helpers

- New `mediavocab.helpers.queries`: `episodes_of`, `filmography_of`,
  `quality_score`, `best_release`.
- Removed `mediavocab.helpers.builders` (wallpaper around two-argument
  constructors). `examples/01_build_a_movie.py` updated to construct
  `Work` / `Release` / `Credit` directly.

### Bug fixes

- `MembershipStatus.LIVE` renamed to `TOURING` (collision with
  `StreamMode.LIVE` and `WorkRelationKind.LIVE_VERSION`).
- `Release.bitrate` semantics tightened to audio fidelity only.
- `Release.region_locked` is now `Optional[bool]` — `None` distinguishes
  "unknown" from "worldwide".
- `work_hash` docstring states `aka` and `localized_titles` are excluded
  by design (alternative spellings of the same identity).
- `StreamMode` docstring distinguishes `ON_DEMAND` / `LIVE` /
  `CONTINUOUS` so callers stop conflating `LIVE` with `CONTINUOUS` for
  radio.
