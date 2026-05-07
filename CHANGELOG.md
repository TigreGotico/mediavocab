# Changelog

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
