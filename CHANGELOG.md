# Changelog

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

## 0.1.0 — 2026-05-06

Initial release.

- `mediavocab.taxonomy`: `MediaType`, `VariantKind`, `EntityKind`, `RelationRole`,
  `CreditSection`, `MembershipStatus`, `ReleaseStatus`, `StreamMode`,
  `WorkRelationKind`, plus `genre.py` constants.
- `mediavocab.models`: `Work`, `Release`, `Appearance`, `WorkRelation`, `Entity`,
  `EntityRef`, `Membership`, `Credit`, `Conflict`, well-known `external_ids` keys.
- `mediavocab.text`: `normalize`, `compare` (with `score`, `merge`, `work_hash`,
  `RUNTIME_TOLERANCE_S`), `iso` (ISO 639-1/-2 + ISO 3166-1 alpha-2 helpers).
- `mediavocab.helpers`: builder shortcuts and classifier predicates.
