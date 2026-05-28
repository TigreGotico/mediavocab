# mediavocab — Production Roadmap

Phased checklist for a coding agent. Run after every phase:

```bash
python -m pytest tests/ -q --tb=short
ruff check mediavocab/
```

Current state: **594 tests passing, 88% coverage, ruff clean.**

---

## Phase 0 — Verify baseline ✅

- [x] `python -m pytest tests/ -q` passes — 594 tests, 88% coverage
- [x] `ruff check mediavocab/` clean
- [x] `python -c "import mediavocab; print(mediavocab.__version__)"` works

---

## Phase 1 — Type correctness & contract tightening ✅

### 1.1 — `ExternalIds.extra` Dict[str, Any] ✅
- [x] `extra: Dict[str, str]` → `extra: Dict[str, Any]`; `from_dict` preserves typed values
- [ ] Update `docs/models.md` with "ExternalIds.extra — key naming conventions" section

### 1.2 — `ProviderMatch.confidence` range validation ✅
- [x] Already enforced via `Field(ge=0.0, le=1.0)` — no change needed

### 1.3 — `Credit.role` / `Credit.relation_role` consistency ✅
- [x] `model_validator` logs WARNING when role strings visibly disagree

### 1.4 — `Release.license` typed ✅
- [x] `Release.license: str = ""` → `Optional[License] = None`
- [x] `field_validator` coerces any SPDX string → `License.from_spdx(s)`; empty string → `None`
- [x] `parsed_license` property removed (direct field access replaces it)
- [x] 3 tests updated; example 11 updated

### 1.5 — Genre normalisation & KNOWN_GENRES ✅
- [x] `KNOWN_GENRES: frozenset` (85 genres) built from all `GENRE_*` constants
- [x] `Work.content_genres` lowercases/strips on intake via `field_validator`
- [x] Exported from `mediavocab.__init__`
- [ ] Update `tests/taxonomy/test_genres_canonical.py` to assert 12 new constants

### 1.6 — `Membership.date_from` / `date_to` order ✅
- [x] Already validated in existing `_check` model_validator

### 1.7 — `AvailabilityWindow` start/end ordering ✅
- [x] Uses `iso_compare()` instead of string `<`

---

## Phase 2 — Signals lifecycle clarity ✅

- [x] `SignalsRole(QUERY / OBSERVATION / RESULT)` enum added
- [x] `Signals.role: SignalsRole = QUERY` field added; excluded from compare/merge
- [x] `Signals.as_query()`, `Signals.as_observation()`, `Signals.as_result()` implemented
- [x] Exported from `mediavocab.__init__`
- [ ] Update `examples/19_signals_pipeline_roles.py` to demonstrate all three constructors

---

## Phase 3 — Country slot ✅

- [x] Validator already uses `sum > 1` — allows zero or one per slot, any combination valid
- [ ] Update `docs/mediavocab_spec.md` §5.3 — text still says "exactly one"; correct to "at most one"
- [ ] Update `tests/test_country_slots.py` to assert zero slots is valid

---

## Phase 4 — Scope reduction ✅ (removed outright)

- [x] `Programme` and `Schedule` deleted from `work.py` and all exports
- [x] `ContentType` enum deleted from `taxonomy/`
- [x] `classify_video()`, `extract_tags()`, `classify_video_dict()` deleted from `text/`
- [x] `quality_score()`, `best_release()` deleted from `helpers/queries.py`
- [x] `text/classify.py` and `taxonomy/content_type.py` deleted

### Locale — adopt ovos-spec-tools format (NEW TASK)
> User directive: adopt ovos-spec-tools and the `/locale` folder format for all strings.
> The locale system stays; classify_video-only `.voc` files are already dead. The
> surviving use case is `title_parse.py` cut/edition/format keyword matching.

- [ ] Research `ovos-spec-tools` locale format conventions (how `.voc` files are structured, loaded, referenced)
- [ ] Audit `mediavocab/locale/` — identify which `.voc` files are still used vs orphaned (classify_video's files are dead)
- [ ] Remove orphaned `.voc` files (those only referenced from deleted `classify_video`)
- [ ] Adopt ovos-spec-tools loading conventions in `mediavocab/locale/__init__.py`
- [ ] Update `title_parse.py` to use the adopted loading API
- [ ] Add `ovos-spec-tools` to `pyproject.toml` dependencies if needed
- [ ] **Acceptance**: `python -m pytest tests/text/test_title_parse.py -v` passes; locale loads via ovos-spec-tools pattern

---

## Phase 5 — Routing gate ✅

- [x] `content_form` axis removed — `MetadataProvider` is now three-axis (`media × playback_type × genre_filter`)
- [x] `_four_axis_gate` renamed `_three_axis_gate`
- [ ] Update `docs/mediavocab_spec.md` §4.11 (A6) — still says "four-axis"; update to three-axis
- [ ] Update `docs/patterns/writing-a-provider.md` — remove `content_form` from provider recipe

### 5.2 — API stability tiers in docs
- **File**: `docs/models.md` or new `docs/api-stability.md`
- [ ] Document: Tier 1 (taxonomy, models, text) stable v1.x; Tier 2 (helpers) stable but non-normative; removed items gone

---

## Phase 6 — Genre enforcement

### 6.1 — Validate `MetadataProvider.genre_filter` against `KNOWN_GENRES`
- **File**: `mediavocab/models/protocols.py`
- [ ] Add `__init_subclass__` hook that checks every string in `genre_filter` against `KNOWN_GENRES` — emit `logging.WARNING`, not error
- [ ] **Acceptance**: provider with `genre_filter = {"anime"}` logs no warning; `genre_filter = {"Anime"}` logs warning

### 6.2 — New genre constants ✅
- [x] Added 12 new constants (variety, talk, compilation, instructional, nature, travel, cooking, fitness, true_crime, self_help, vocaloid, city_pop)
- [x] All 85 in `KNOWN_GENRES`
- [ ] Update `tests/taxonomy/test_genres_canonical.py` to cover the 12 new constants

---

## Phase 7 — External ID registry ✅

- [x] Added 11 new constants (anidb, letterboxd, bandcamp, soundcloud, youtube_channel, youtube_video, youtube_music_artist, hardcover, reading_glasses, podcast_index_feed, radio_browser_uuid)
- [x] `KNOWN_EXTERNAL_IDS: frozenset` (55 keys) exported from `mediavocab.__init__`
- [ ] Update `tests/models/test_external_ids.py` to assert new constants are importable and in `KNOWN_EXTERNAL_IDS`

---

## Phase 8 — Relation helpers ✅

- [x] `relations_of_kind`, `is_sequel_of`, `is_part_of_series`, `all_cuts`, `release_variants` added to `helpers/queries.py`
- [x] Exported via `helpers/__init__.py`; tested in `tests/test_new_features.py`

### 8.2 — WorkRelation vs variant_kind docs
- **File**: `docs/mediavocab_spec.md`
- [ ] Add subsection: `variant_kind` = describe what this record is; `WorkRelation(DERIVED_FROM)` = link two records together; both can coexist on the same Work

---

## Phase 9 — Merge robustness ✅

- [x] `IDENTITY_FIELDS: frozenset` (15 fields) added to `text/compare.py`, exported via `text.__init__`
- [x] `MergeStrategy`, `DEFAULT_STRATEGY`, `IdentityConflict` already exported top-level
- [ ] Document `IDENTITY_FIELDS` in `docs/text-utilities.md`

---

## Phase 10 — Spec alignment

### 10.1 — WorkRelation vs ReleaseRelation guidance
- **File**: `docs/mediavocab_spec.md` §4.13
- [ ] Add: WorkRelation = conceptual link between creative works; ReleaseRelation = format-level link between manifested releases

### 10.2 — EntityRef vs Entity guidance
- **File**: `docs/models.md`
- [ ] Add: EntityRef = lightweight reference in credits/tracklist; Entity = full persistent record; `Work.credits` always contains `EntityRef`

### 10.3 — `NORMALISE_TITLE_VERSION` pin ✅
- [x] `NORMALISE_TITLE_VERSION = 1` added to `text/normalize.py`, exported
- [ ] Document in `docs/mediavocab_spec.md` §6.3: increment = breaking change = major version bump
- [ ] Expand golden-value tests to cover non-Latin scripts (Japanese, Arabic, Chinese)

---

## Phase 11 — Examples

### 11.1 — Signals lifecycle example
- **File**: `examples/19_signals_pipeline_roles.py`
- [ ] Update to use `Signals.as_query()` / `Signals.as_observation()` / `Signals.as_result()`

### 11.2 — WorkRelation + VariantKind example
- **File**: `examples/21_variant_kind_and_relation.py` (new)
- [ ] Theatrical + director's cut linked via `WorkRelation(DERIVED_FROM)` + `variant_kind=DIRECTORS`

### 11.3 — Verify existing examples still run
- [ ] `python -m py_compile examples/*.py` — no syntax errors (some may import removed names)
- [ ] Fix any that imported `Programme`, `Schedule`, `classify_video`, `quality_score`, `best_release`, `ContentType`

---

## Phase 12 — CI & packaging

### 12.1 — Coverage gate ✅
- [x] `min_coverage` 0 → 85; `test_path` `test/` → `tests/`

### 12.2 — `KNOWN_EXTERNAL_IDS` ✅
- [x] Added to `external_ids.py`, exported from `mediavocab.__init__`

### 12.3 — pyproject.toml audit
- [ ] Confirm `Homepage` URL is correct
- [ ] Confirm `classifiers` includes `Development Status :: 5 - Production/Stable`
- [ ] Confirm no stale extras; add ovos-spec-tools if needed after Phase 4 locale work

### 12.4 — Pre-release checklist for v1.1.0
- [ ] All remaining `[ ]` items checked off
- [ ] `python -m pytest tests/ -q` — zero failures
- [ ] Coverage ≥ 90%
- [ ] `ruff check mediavocab/` — zero violations
- [ ] `pip-audit` — zero CVEs
- [ ] `python -m py_compile examples/*.py` — clean
- [ ] Do NOT edit `version.py` — gh-automations bumps from commit prefixes
- [ ] Merge `dev` → `master` to trigger `release_workflow.yml`

---

## Verification commands

```bash
# After every phase:
python -m pytest tests/ -q --tb=short
ruff check mediavocab/

# Full check:
python -m pytest tests/ --cov=mediavocab --cov-report=term-missing -q
pip-audit
python -m py_compile examples/*.py

# Smoke test:
python -c "
from mediavocab import Work, Release, Entity, MediaType, EntityKind
from mediavocab import work_hash, release_hash, score, compare, merge
from mediavocab import Signals, SignalsRole, MetadataProvider, ProviderMatch
from mediavocab import KNOWN_GENRES, KNOWN_EXTERNAL_IDS
w = Work(title='Test', media_type=MediaType.MOVIE)
print('work_hash:', work_hash(w))
print(len(KNOWN_GENRES), 'genres,', len(KNOWN_EXTERNAL_IDS), 'ext IDs')
print('mediavocab OK')
"
```
