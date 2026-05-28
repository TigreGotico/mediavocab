# mediavocab — Production Roadmap

Phased checklist for a coding agent. Work top-to-bottom within each phase. Run after every phase:

```bash
python -m pytest tests/ -q --tb=short
ruff check mediavocab/
```

---

## Phase 0 — Verify baseline

- [ ] Confirm `python -m pytest tests/ -q` passes with zero failures (626 tests, 98% coverage)
- [ ] Confirm `ruff check mediavocab/` is clean
- [ ] Confirm `python -c "import mediavocab; print(mediavocab.__version__)"` works

---

## Phase 1 — Type correctness & contract tightening

### 1.1 — `ExternalIds.extra` is typed `Dict[str, str]` but stores mixed types
- **File**: `mediavocab/models/external_ids.py`
- [ ] Change `extra: Dict[str, str]` → `extra: Dict[str, Any]`; add `from typing import Any` if missing
- [ ] Add a docstring comment listing expected key naming conventions: `"cover_url"`, `"feed_url"`, `"image_url"`, `"slug"`, etc.
- [ ] Update `docs/resolve.md` (or `docs/models.md`) with a section: "ExternalIds.extra — key naming conventions"
- [ ] **Acceptance**: `mypy mediavocab/models/external_ids.py --strict` passes; all existing tests pass

### 1.2 — `MappingEntry.score` / `ProviderMatch.confidence` not range-validated
- **File**: `mediavocab/models/protocols.py` (`ProviderMatch.confidence`)
- [ ] Add `@field_validator("confidence")` that clamps or rejects values outside `[0.0, 1.0]`; raise `ValueError` on out-of-range
- [ ] **Acceptance**: `ProviderMatch(confidence=1.5, ...)` raises `ValidationError`; new test in `tests/models/test_protocols.py`

### 1.3 — `Credit.role` (free string) and `Credit.relation_role` (RelationRole) can disagree silently
- **File**: `mediavocab/models/entity.py` (`Credit` model)
- [ ] Add `@model_validator(mode="after")` that, if both `role` and `relation_role` are set, asserts `role.lower()` contains `relation_role.value.lower()` or logs a WARNING — do not reject (too strict), but surface the inconsistency
- [ ] Add docstring on `Credit.role`: "Free-text editorial label (e.g. 'Executive Producer'). When relation_role is set, role should be a human-readable expansion of it."
- [ ] **Acceptance**: new test `test_credit_role_disagreement_warns` — assert no ValidationError but check that validator runs; existing tests pass

### 1.4 — `Release.license` is a free string; `License` model is a separate companion
- **File**: `mediavocab/models/work.py` (`Release`), `mediavocab/models/license.py`
- [ ] Change `Release.license: Optional[str]` → `Release.license: Optional[License]`
- [ ] Add `@field_validator("license", mode="before")` that coerces a plain string `s` → `License(identifier=s)` so existing string-based callers still work
- [ ] Update all tests that set `release.license = "CC-BY-4.0"` (string) to verify they still pass after coercion
- [ ] Update examples that populate `release.license` as a string
- [ ] **Acceptance**: `Release(work=..., license="CC-BY-4.0").license.is_open()` returns True; all existing tests pass

### 1.5 — `Work.content_genres: Set[str]` accepts arbitrary strings; genre constants are unenforced
- **File**: `mediavocab/models/work.py`, `mediavocab/taxonomy/genre.py`
- [ ] Build a `KNOWN_GENRES: frozenset[str]` in `mediavocab/taxonomy/genre.py` containing all `GENRE_*` values
- [ ] Add `@field_validator("content_genres", mode="before")` on `Work` that normalises each genre string via `normalize(g)` before storing
- [ ] Do NOT reject unknown genres (too strict for extensibility) — only normalise case/whitespace
- [ ] Export `KNOWN_GENRES` from `mediavocab/__init__.py`
- [ ] **Acceptance**: `Work(title="x", media_type=MediaType.MUSIC, content_genres={"Rock"}).content_genres == {"rock"}`; `"rock" in KNOWN_GENRES` is True

### 1.6 — `Membership.date_from` / `date_to` have no `from < to` order check
- **File**: `mediavocab/models/entity.py` (`Membership`)
- [ ] Add `@model_validator(mode="after")` that, if both `date_from` and `date_to` are set, asserts `iso_compare(date_from, date_to) <= 0`
- [ ] **Acceptance**: `Membership(entity=..., kind=..., temporal=..., date_from="2020", date_to="2019")` raises `ValidationError`; new test in `tests/models/test_entity.py`

### 1.7 — `AvailabilityWindow` has no `start < end` check within a single window
- **File**: `mediavocab/models/work.py` (`AvailabilityWindow`)
- [ ] Add `@model_validator(mode="after")` that, if both `available_from` and `available_until` are set, asserts `iso_compare(available_from, available_until) < 0`
- [ ] **Acceptance**: new test — window with `available_from="2025-12"` and `available_until="2025-01"` raises `ValidationError`

---

## Phase 2 — Signals lifecycle clarity

> The `Signals` model has three roles (query, observation, result) in one type with no type-level distinction. This phase makes the contract explicit without breaking the existing interface.

### 2.1 — Document Signals lifecycle fields explicitly
- **File**: `mediavocab/models/signals.py`
- [ ] Add section comments partitioning fields into three groups:
  - `# --- Query role: filled by the caller before resolution ---`
  - `# --- Observation role: filled by providers after lookup ---`
  - `# --- Result role: filled by consolidator after merge ---`
  - `# --- Routing hints: never conflict-eligible, never persisted ---`
- [ ] Add a module-level docstring explaining the three lifecycle roles
- [ ] **Acceptance**: `mediavocab/models/signals.py` is readable without the patterns doc; no logic change

### 2.2 — Add `Signals.lifecycle` field for explicit role tracking
- **File**: `mediavocab/models/signals.py`
- [ ] Add `SignalsRole` enum: `QUERY = "query"`, `OBSERVATION = "observation"`, `RESULT = "result"`
- [ ] Add `role: SignalsRole = SignalsRole.QUERY` field to `Signals`
- [ ] `role` is excluded from `compare_signals()` and `merge_signals()` (it is not a data field)
- [ ] Export `SignalsRole` from `mediavocab/__init__.py`
- [ ] **Acceptance**: `Signals(title="x", role=SignalsRole.OBSERVATION)` works; `compare_signals(s1, s2)` does not include `role` in conflicts; new test in `tests/models/test_signals.py`

### 2.3 — Add `Signals.as_query()` / `Signals.as_observation()` / `Signals.as_result()` constructors
- **File**: `mediavocab/models/signals.py`
- [ ] Add `@classmethod as_query(cls, **kwargs) -> Signals` — sets `role=QUERY`
- [ ] Add `@classmethod as_observation(cls, **kwargs) -> Signals` — sets `role=OBSERVATION`
- [ ] Add `as_result()` instance method — returns a copy with `role=RESULT`
- [ ] Add example to `examples/19_signals_pipeline_roles.py` showing all three constructors
- [ ] **Acceptance**: `Signals.as_query(title="Blade Runner").role == SignalsRole.QUERY`; all tests pass

---

## Phase 3 — Country slot relaxation

> The current validator enforces exactly-one-slot exclusivity. Real-world media often legitimately populates multiple slots (e.g., a film has both a production country and a broadcaster country). This phase relaxes to at-most-one-per-slot.

### 3.1 — Relax country slot from "exactly one" to "at most one per slot, any combination allowed"
- **File**: `mediavocab/models/work.py` (`Work` country slot validator)
- [ ] Change the validator from "exactly one of {production_country, publication_country, broadcaster_country}" to "no slot may be populated by the wrong media type" (use `COUNTRY_SLOT_FOR` to check that if a slot is populated, the media type is allowed to use it)
- [ ] Remove the "at least one must be set" constraint — country is optional
- [ ] Update `tests/test_country_slots.py` to reflect relaxed semantics
- [ ] Update `docs/mediavocab_spec.md` §5.3 country slot section
- [ ] **Acceptance**: a MOVIE Work with both `production_country="US"` and `broadcaster_country="GB"` is valid; tests pass

---

## Phase 4 — Scope reduction: extract operational models

> `Programme`, `Schedule`, `classify_video()`, `quality_score()`, and `best_release()` are application-level, not vocabulary-level. They inflate scope and create a maintenance surface unrelated to identity or structure. This phase deprecates them in place, preparing for extraction to a downstream package.

### 4.1 — Deprecate `Programme` and `Schedule` models
- **File**: `mediavocab/models/work.py`, `mediavocab/__init__.py`
- [ ] Add `DeprecationWarning` to `Programme.__init_subclass__` and to any import path: `"Programme and Schedule will be removed in v2.0; use a downstream EPG package"`
- [ ] Keep them functional for v1.x — do not remove
- [ ] Add `# deprecated: moving to mediavocab-epg in v2.0` comment at class definition
- [ ] Update `docs/models.md` with a deprecation notice
- [ ] **Acceptance**: `from mediavocab import Programme` emits `DeprecationWarning`; existing `test_programme_schedule.py` still passes

### 4.2 — Deprecate `classify_video()` and `ContentType`
- **File**: `mediavocab/text/classify.py`, `mediavocab/taxonomy/content_type.py`, `mediavocab/__init__.py`
- [ ] Add `DeprecationWarning` at the top of `classify_video()` and `extract_tags()`: `"classify_video() is heuristic application logic and will be removed in v2.0"`
- [ ] Mark `ContentType` enum as deprecated in its docstring
- [ ] Keep functional for v1.x
- [ ] **Acceptance**: calling `classify_video("...")` emits `DeprecationWarning`; tests still pass

### 4.3 — Deprecate `quality_score()` and `best_release()` in helpers
- **File**: `mediavocab/helpers/queries.py` (or wherever these live)
- [ ] Add `DeprecationWarning` to both functions: `"quality_score() encodes application preferences; will be removed in v2.0"`
- [ ] **Acceptance**: calling either function emits `DeprecationWarning`; tests still pass

### 4.4 — Deprecate locale `.voc` keyword files as internal API
- **File**: `mediavocab/locale/__init__.py`
- [ ] Add module-level `DeprecationWarning` on import: `"mediavocab.locale is an internal implementation detail and will be extracted in v2.0"`
- [ ] Keep functional for v1.x
- [ ] Document in `docs/mediavocab_spec.md` §8 that locale support will be extracted

---

## Phase 5 — ContentForm routing axis cleanup

> The four-axis routing gate (A6) includes `content_form` as an axis, but no real provider filters on ContentForm. It adds complexity to the gate with no documented use case.

### 5.1 — Remove `content_form` from the four-axis routing gate
- **File**: `mediavocab/models/protocols.py` (`MetadataProvider.matches()`)
- [ ] Remove `content_form` from the `matches()` default implementation
- [ ] Remove `content_form: ClassVar[Set[ContentForm]]` from `MetadataProvider` base class (or keep as an optional override, defaulting to "match all")
- [ ] Update `docs/mediavocab_spec.md` §4.11 (A6) to reflect three-axis gate: `media × playback_type × genre_filter`
- [ ] Update `docs/patterns/writing-a-provider.md`
- [ ] **Acceptance**: `MetadataProvider.matches()` no longer checks `content_form`; all tests pass; no provider in metadatarr uses `content_form` filter

### 5.2 — Update `helpers/` stability contract in docs
- **File**: `docs/models.md` or a new `docs/api-stability.md`
- [ ] Add explicit section: "API stability tiers" — Tier 1 (taxonomy, models, text): stable for v1.x; Tier 2 (helpers): stable for v1.x but non-normative; Tier 3 (Programme/Schedule, classify_video, quality_score): deprecated, removal in v2.0
- [ ] **Acceptance**: stability contract is documented; downstream consumers know what to trust

---

## Phase 6 — Genre enforcement & registry

### 6.1 — Validate `MetadataProvider.genre_filter` against `KNOWN_GENRES`
- **File**: `mediavocab/models/protocols.py` (`MetadataProvider`)
- [ ] Add `__init_subclass__` or `@model_validator` that checks every string in `genre_filter` is in `KNOWN_GENRES` (emit WARNING, not error — providers may use upstream genre strings not yet in the registry)
- [ ] **Acceptance**: a provider with `genre_filter = {"anime"}` (valid) logs no warning; `genre_filter = {"Anime"}` logs a normalisation warning

### 6.2 — Add missing genre constants
- **File**: `mediavocab/taxonomy/genre.py`
- [ ] Audit the 60+ existing constants against common streaming platform genre taxonomies (Spotify, TMDB, MAL)
- [ ] Add missing genres that are broadly used: `GENRE_VARIETY`, `GENRE_TALK`, `GENRE_COMPILATION`, `GENRE_INSTRUCTIONAL`, `GENRE_NATURE`, `GENRE_TRAVEL`, `GENRE_COOKING`, `GENRE_FITNESS`, `GENRE_TRUE_CRIME`, `GENRE_SELF_HELP`
- [ ] Add `GENRE_VOCALOID` and `GENRE_CITY_POP` for completeness with anime/J-music providers
- [ ] **Acceptance**: new constants are in `KNOWN_GENRES`; `test_genres_canonical.py` covers them

---

## Phase 7 — External ID registry expansion

### 7.1 — Add missing well-known external ID constants
- **File**: `mediavocab/models/external_ids.py`
- [ ] Add: `ANIDB = "anidb"`, `MYANIMELIST = "myanimelist"`, `ANILIST = "anilist"` (anime)
- [ ] Add: `LETTERBOXD = "letterboxd"` (film)
- [ ] Add: `BANDCAMP = "bandcamp"`, `SOUNDCLOUD = "soundcloud"`, `YOUTUBE_CHANNEL = "youtube_channel"`, `YOUTUBE_VIDEO = "youtube_video"`, `YOUTUBE_MUSIC_ARTIST = "youtube_music_artist"` (audio/video)
- [ ] Add: `HARDCOVER = "hardcover"`, `READING_GLASSES = "reading_glasses"` (books)
- [ ] Add: `METAL_ARCHIVES_BAND = "metal_archives_band"`, `METAL_ARCHIVES_RELEASE = "metal_archives_release"` (metal music)
- [ ] Add: `PODCAST_INDEX_FEED = "podcast_index_feed"` (podcasts — distinct from episode-level PODCAST_INDEX)
- [ ] Add: `RADIO_BROWSER_UUID = "radio_browser_uuid"` (radio)
- [ ] Update `KNOWN_EXTERNAL_IDS` frozenset (if it exists) or create it
- [ ] **Acceptance**: `from mediavocab import ANIDB` works; `test_external_ids.py` covers new constants

### 7.2 — Add `ExternalIds.merge()` deduplication for ISBN-10/13 pairs
- **File**: `mediavocab/models/external_ids.py`
- [ ] When merging two `ExternalIds`, if one has `ISBN = "978-..."` (ISBN-13) and the other has a compatible ISBN-10, normalise and deduplicate
- [ ] Reuse `mediavocab.text.isbn.normalize_isbn()` 
- [ ] **Acceptance**: `e1.merge(e2)` where e1 has ISBN-10 and e2 has the equivalent ISBN-13 produces exactly one ISBN key; new test in `tests/models/test_external_ids.py`

---

## Phase 8 — Work/Release relation helpers

### 8.1 — Add relationship traversal helpers
- **File**: `mediavocab/helpers/queries.py`
- [ ] `relations_of_kind(work: Work, kind: WorkRelationKind) -> List[WorkRelation]` — filter `work.relations` by kind
- [ ] `is_sequel_of(work: Work) -> bool` — True if any relation has kind SEQUEL
- [ ] `is_part_of_series(work: Work) -> bool` — True if any relation has kind PART_OF_SERIES
- [ ] `all_cuts(work: Work) -> List[WorkRelation]` — all ALTERNATIVE_CUT relations
- [ ] `release_variants(release: Release) -> List[ReleaseRelation]` — all VARIANT release relations
- [ ] **Acceptance**: new tests in `tests/helpers/test_queries.py`; `director(blade_runner)` still works

### 8.2 — Clarify `WorkRelation.ALTERNATIVE_CUT` vs `Work.variant_kind` in docs
- **File**: `docs/mediavocab_spec.md` (§5.3 or patterns section)
- [ ] Add subsection: "When to use variant_kind vs WorkRelation.ALTERNATIVE_CUT"
  - `variant_kind`: use when the variant is your primary record (you have the director's cut and want to express what kind it is)
  - `WorkRelation.ALTERNATIVE_CUT`: use when you have two records and want to link them (theatrical ↔ director's cut)
  - Both can and should be set simultaneously on the director's cut record
- [ ] Update `examples/01_build_a_movie.py` to demonstrate both
- [ ] **Acceptance**: no code change; docs reviewed and merged

---

## Phase 9 — Merge robustness

### 9.1 — `merge()` identity conflict field list is undocumented
- **File**: `mediavocab/text/compare.py` (`merge()`), `docs/text-utilities.md`
- [ ] Add a `IDENTITY_FIELDS: frozenset[str]` constant listing fields that trigger `IdentityConflict` when they disagree (e.g., `media_type`, `season`, `episode`, `work_hash`)
- [ ] Reference `IDENTITY_FIELDS` in the `merge()` implementation so the set is single-sourced
- [ ] Document `IDENTITY_FIELDS` in `docs/text-utilities.md`
- [ ] **Acceptance**: `from mediavocab.text.compare import IDENTITY_FIELDS` works; `test_merge_strategy.py` asserts that identity-field disagreement raises `IdentityConflict`

### 9.2 — `MergeStrategy` is not exported at top-level
- **File**: `mediavocab/__init__.py`
- [ ] Confirm `MergeStrategy`, `DEFAULT_STRATEGY`, `IdentityConflict` are in `__init__.py` exports — add if missing
- [ ] **Acceptance**: `from mediavocab import MergeStrategy` works

---

## Phase 10 — Spec alignment fixes

### 10.1 — Document `WorkRelation` vs `ReleaseRelation` embedding guidance
- **File**: `docs/mediavocab_spec.md` §4.13, `docs/patterns/`
- [ ] Add subsection: "WorkRelation vs ReleaseRelation — which to use"
  - WorkRelation: conceptual links between creative works (this film is a sequel of that film)
  - ReleaseRelation: format-level links between manifested releases (this remaster is derived from that original pressing)
- [ ] Update `examples/16_release_relation_lineage.py` to show a complete lineage chain

### 10.2 — Document `EntityRef` vs `Entity` embedding guidance
- **File**: `docs/models.md` or `docs/mediavocab_spec.md` §5.1
- [ ] Add subsection: "When to embed EntityRef vs Entity"
  - `EntityRef`: lightweight reference inside a Work's credit list or Appearance.attributed_to — you know the name and maybe an external ID, but don't have the full entity record
  - `Entity`: the full persistent record, stored separately, linked by ID
  - `Work.credits` always contains `EntityRef`, never `Entity`

### 10.3 — Pin `normalise_title()` behaviour in the hash stability contract
- **File**: `mediavocab/text/normalize.py`, `docs/mediavocab_spec.md` §6.3
- [ ] Add `NORMALISE_TITLE_VERSION = 1` constant to `mediavocab/text/normalize.py`
- [ ] Document in §6.3: "work_hash stability depends on normalise_title() v{NORMALISE_TITLE_VERSION}. Any change to normalise_title() increments this constant and constitutes a breaking change requiring a major version bump."
- [ ] Add `test_normalise_title_pins.py` with golden-value assertions for 20+ representative titles (ASCII, diacritics, punctuation, non-Latin scripts)
- [ ] **Acceptance**: new test file passes; constant exported from `mediavocab.text.normalize`

---

## Phase 11 — New patterns & examples

### 11.1 — Add missing example: Signals three-role walkthrough (detailed)
- **File**: `examples/19_signals_pipeline_roles.py` (update existing or create new)
- [ ] Show full lifecycle: `Signals.as_query(title="Blade Runner 2049")` → mock provider returns `Signals.as_observation(title="Blade Runner 2049", year=2017, ...)` → consolidator produces `Signals.as_result(...)`
- [ ] Show `compare_signals()` detecting a year disagreement between two providers

### 11.2 — Add example: multi-country Work (post Phase 3)
- **File**: `examples/20_multi_country_work.py` (new)
- [ ] Demonstrate a co-production with both `production_country` and `broadcaster_country` set simultaneously
- [ ] Show how to query the country slot via `COUNTRY_SLOT_FOR`

### 11.3 — Add example: `WorkRelation` + `VariantKind` together
- **File**: `examples/21_variant_kind_and_relation.py` (new)
- [ ] Demonstrate a theatrical cut Work and a director's cut Work with both `variant_kind=DIRECTORS` on the second, and a `WorkRelation(kind=ALTERNATIVE_CUT, target=theatrical_work_ref)` linking them

### 11.4 — Verify all 19 existing examples still run after Phase 1–4 changes
- [ ] `python -m py_compile examples/*.py` — no syntax errors
- [ ] `python -c "exec(open('examples/01_build_a_movie.py').read())"` — no runtime errors (for each example that doesn't require network)

---

## Phase 12 — CI & packaging

### 12.1 — Coverage gate is 0% (should be 85%+)
- **File**: `.github/workflows/coverage.yml`
- [ ] Change `min_coverage=0` to `min_coverage=85` (current coverage is 98%, so this is safe)
- [ ] **Acceptance**: coverage workflow fails if coverage drops below 85%

### 12.2 — Add `KNOWN_EXTERNAL_IDS` frozenset to `external_ids.py`
- **File**: `mediavocab/models/external_ids.py`
- [ ] Build `KNOWN_EXTERNAL_IDS: frozenset[str]` from all module-level string constants in the file
- [ ] Export from `mediavocab/__init__.py`
- [ ] **Acceptance**: `from mediavocab import KNOWN_EXTERNAL_IDS; "imdb" in KNOWN_EXTERNAL_IDS` is True

### 12.3 — pyproject.toml: verify `[project.urls]` and package metadata
- **File**: `pyproject.toml`
- [ ] Confirm `Homepage` URL is correct GitHub repo
- [ ] Confirm `[project.optional-dependencies]` only contains `test`
- [ ] Confirm `[project.classifiers]` reflects `Development Status :: 5 - Production/Stable` (it's v1.0.0)
- [ ] Confirm no stale extras from pre-1.0 development

### 12.4 — Pre-release checklist for v1.1.0
- [ ] All Phase 1–11 tasks checked off
- [ ] `python -m pytest tests/ -q` — zero failures
- [ ] Coverage ≥ 90%
- [ ] `ruff check mediavocab/` — zero violations
- [ ] `pip-audit` — zero known CVEs
- [ ] `python -m py_compile examples/*.py` — clean
- [ ] `python -c "import mediavocab"` — no deprecation warnings on clean import
- [ ] Do NOT edit `version.py` — gh-automations bumps via semver from commit prefixes
- [ ] Merge `dev` → `master` to trigger `release_workflow.yml`

---

## Deferred to v2.0 (do not implement in v1.x)

These require breaking changes and must wait for a major version bump:

- [ ] **v2.0**: Remove `Programme`, `Schedule` (extracted to `mediavocab-epg`)
- [ ] **v2.0**: Remove `classify_video()`, `ContentType`, `extract_tags()` (extracted to `mediavocab-classify`)
- [ ] **v2.0**: Remove `quality_score()`, `best_release()` (extracted to downstream)
- [ ] **v2.0**: Extract locale `.voc` files to `mediavocab-locale`
- [ ] **v2.0**: Replace three-role `Signals` with typed `QuerySignals` / `ObservationSignals` / `ResolvedSignals` hierarchy
- [ ] **v2.0**: Make `Credit.relation_role` mandatory (remove free-string-only path)
- [ ] **v2.0**: Change `work_hash` quantum values based on real-world collision data (bump `NORMALISE_TITLE_VERSION`)

---

## Verification commands

```bash
# After every phase:
python -m pytest tests/ -q --tb=short
ruff check mediavocab/

# Full pre-release check:
python -m pytest tests/ --cov=mediavocab --cov-report=term-missing -q
pip-audit
python -m py_compile examples/*.py

# Smoke test:
python -c "
from mediavocab import Work, Release, Entity, MediaType, EntityKind
from mediavocab import work_hash, release_hash, score, compare, merge
from mediavocab import Signals, MetadataProvider, ProviderMatch
w = Work(title='Test', media_type=MediaType.MOVIE)
print('work_hash:', work_hash(w))
print('mediavocab OK')
"

# Deprecation check (should import cleanly):
python -W error::DeprecationWarning -c "import mediavocab"
```
