# mediavocab — Production Roadmap

Phased checklist for a coding agent. Run after every phase:

```bash
python -m pytest tests/ -q --tb=short
ruff check mediavocab/
```

Current state: **593 tests passing, 88% coverage, ruff clean.**

---

## Phase 0 — Verify baseline ✅

- [x] `python -m pytest tests/ -q` passes — 593 tests, 88% coverage
- [x] `ruff check mediavocab/` clean
- [x] `python -c "import mediavocab; print(mediavocab.__version__)"` works

---

## Phase 1 — Type correctness & contract tightening

### 1.1 — `ExternalIds.extra` Dict[str, Any] ✅
- [x] `extra: Dict[str, str]` → `extra: Dict[str, Any]`
- [x] Key naming conventions documented in field docstring
- [ ] Update `docs/models.md` with "ExternalIds.extra — key naming conventions" section

### 1.2 — `ProviderMatch.confidence` range validation ✅
- [x] Already enforced via `Field(ge=0.0, le=1.0)` — no change needed

### 1.3 — `Credit.role` / `Credit.relation_role` consistency ✅
- [x] `model_validator` logs WARNING when role strings visibly disagree
- [x] `Credit` docstring updated

### 1.4 — `Release.license` type
- **File**: `mediavocab/models/work.py`, `mediavocab/models/license.py`
- [ ] Change `Release.license: str = ""` → `Release.license: Optional[License] = None`
- [ ] Add `@field_validator("license", mode="before")` coercing string → `License.from_spdx(s)`
- [ ] Update tests that set `release.license = "CC-BY-4.0"` (string) — coercion must keep them passing
- [ ] Remove deprecated `parsed_license` property (replaced by direct field access)
- [ ] **Acceptance**: `Release(work=..., license="CC-BY-4.0").license.is_open()` is True; 593+ tests pass

### 1.5 — Genre normalisation & KNOWN_GENRES ✅
- [x] `KNOWN_GENRES: frozenset` built from all `GENRE_*` constants (85 genres)
- [x] `Work.content_genres` lowercases/strips on intake via `field_validator`
- [x] Exported from `mediavocab.__init__`
- [ ] Update `tests/taxonomy/test_genres_canonical.py` to assert new constants (variety, talk, city_pop, etc.)

### 1.6 — `Membership.date_from` / `date_to` order ✅
- [x] Already validated in existing `_check` model_validator — no change needed

### 1.7 — `AvailabilityWindow` start/end ordering ✅
- [x] Replaced string `<` comparison with `iso_compare()` — handles partial ISO dates correctly

---

## Phase 2 — Signals lifecycle clarity ✅

### 2.1 — Field section comments ✅
- [x] `signals.py` has routing-hints section comment; module docstring covers all three roles

### 2.2 — `SignalsRole` enum ✅
- [x] `SignalsRole(QUERY / OBSERVATION / RESULT)` added
- [x] `Signals.role: SignalsRole = QUERY` field added
- [x] `role` excluded from `compare_signals()` and `merge_signals()`
- [x] Exported from `mediavocab.__init__`

### 2.3 — Lifecycle constructors ✅
- [x] `Signals.as_query(**kwargs)`, `Signals.as_observation(**kwargs)`, `Signals.as_result()` implemented
- [ ] Update `examples/19_signals_pipeline_roles.py` to show all three constructors

---

## Phase 3 — Country slot

### 3.1 — "at most one per slot" ✅
- [x] Validator already uses `sum(1 for s in slots if s) > 1` — allows any combination, rejects only when >1 slot is set simultaneously
- [ ] Update `docs/mediavocab_spec.md` §5.3 — current text still says "exactly one"; should say "at most one of each"
- [ ] Update `tests/test_country_slots.py` to assert that zero slots is valid

---

## Phase 4 — Scope reduction ✅

### Removed outright (no backwards compat needed):
- [x] `Programme` and `Schedule` models deleted from `work.py` and all exports
- [x] `ContentType` enum deleted from `taxonomy/`
- [x] `classify_video()`, `extract_tags()`, `classify_video_dict()` deleted from `text/`
- [x] `quality_score()`, `best_release()` deleted from `helpers/queries.py`
- [x] `text/classify.py` and `taxonomy/content_type.py` deleted (dead code)
- [x] All associated tests deleted or trimmed
- [ ] Remove locale `.voc` keyword files and `mediavocab/locale/` — only used by deleted `classify_video()`
  - **File**: `mediavocab/locale/`, `mediavocab/text/title_parse.py` (check if still uses locale)
  - Check `title_parse.py` imports — if it uses `mediavocab.locale`, either keep locale or remove the locale-dependent path
  - **Acceptance**: `import mediavocab` does not load `.voc` files; no locale directory in wheel

---

## Phase 5 — Routing gate ✅

### 5.1 — ContentForm axis removed ✅
- [x] `content_form` removed from `MetadataProvider` ClassVar and `matches()` implementation
- [x] `_four_axis_gate` renamed `_three_axis_gate`
- [x] `test_content_form_gate` removed
- [ ] Update `docs/mediavocab_spec.md` §4.11 (A6) — still says "four-axis"; update to three-axis
- [ ] Update `docs/patterns/writing-a-provider.md` — remove `content_form` from provider recipe

### 5.2 — API stability tiers in docs
- **File**: `docs/models.md` or new `docs/api-stability.md`
- [ ] Document: Tier 1 (taxonomy, models, text) stable v1.x; Tier 2 (helpers) stable but non-normative; removed items gone

---

## Phase 6 — Genre enforcement

### 6.1 — Validate `MetadataProvider.genre_filter` against `KNOWN_GENRES`
- **File**: `mediavocab/models/protocols.py`
- [ ] Add `__init_subclass__` hook that checks every string in `genre_filter` is in `KNOWN_GENRES` — emit `logging.WARNING`, not error
- [ ] **Acceptance**: provider with `genre_filter = {"anime"}` logs no warning; `genre_filter = {"Anime"}` logs a normalisation warning

### 6.2 — New genre constants ✅
- [x] Added: `GENRE_VARIETY`, `GENRE_TALK`, `GENRE_COMPILATION`, `GENRE_INSTRUCTIONAL`, `GENRE_NATURE`, `GENRE_TRAVEL`, `GENRE_COOKING`, `GENRE_FITNESS`, `GENRE_TRUE_CRIME`, `GENRE_SELF_HELP`, `GENRE_VOCALOID`, `GENRE_CITY_POP`
- [x] All 85 constants in `KNOWN_GENRES`
- [ ] Update `tests/taxonomy/test_genres_canonical.py` to cover the 12 new constants

---

## Phase 7 — External ID registry

### 7.1 — New external ID constants ✅
- [x] Added: `ANIDB`, `LETTERBOXD`, `BANDCAMP`, `SOUNDCLOUD`, `YOUTUBE_CHANNEL`, `YOUTUBE_VIDEO`, `YOUTUBE_MUSIC_ARTIST`, `HARDCOVER`, `READING_GLASSES`, `PODCAST_INDEX_FEED`, `RADIO_BROWSER_UUID`
- [x] `KNOWN_EXTERNAL_IDS: frozenset` (55 keys) added and exported
- [ ] Update `tests/models/test_external_ids.py` to assert new constants are importable and in `KNOWN_EXTERNAL_IDS`

### 7.2 — `ExternalIds.merge()` ISBN deduplication ✅
- [x] Already implemented in `_normalize_and_pair_isbn` validator — ISBN-10/13 pairs are back-filled automatically on construction and survive merge

---

## Phase 8 — Relation helpers

### 8.1 — Traversal helpers ✅
- [x] `relations_of_kind(work, kind)`, `is_sequel_of(work)`, `is_part_of_series(work)`, `all_cuts(work)`, `release_variants(release)` added to `helpers/queries.py`
- [x] Exported via `helpers/__init__.py`
- [x] Tested in `tests/test_new_features.py`

### 8.2 — WorkRelation vs variant_kind docs
- **File**: `docs/mediavocab_spec.md`
- [ ] Add subsection clarifying when to use `variant_kind` vs `WorkRelation.DERIVED_FROM` for alternative cuts
- [ ] Note that both can coexist: `variant_kind=DIRECTORS` on the record + `WorkRelation(DERIVED_FROM, theatrical)` linking it

---

## Phase 9 — Merge robustness

### 9.1 — `IDENTITY_FIELDS` constant ✅
- [x] `IDENTITY_FIELDS: frozenset` (15 fields) added to `text/compare.py`
- [x] Exported via `text/__init__`
- [ ] Document in `docs/text-utilities.md` — note which fields trigger `IdentityConflict`

### 9.2 — `MergeStrategy` top-level export ✅
- [x] Already exported — `from mediavocab import MergeStrategy` works

---

## Phase 10 — Spec alignment

### 10.1 — WorkRelation vs ReleaseRelation guidance
- **File**: `docs/mediavocab_spec.md` §4.13
- [ ] Add: WorkRelation = conceptual link between creative works; ReleaseRelation = format-level link between manifested releases
- [ ] Update `examples/16_release_relation_lineage.py` with a complete lineage chain example

### 10.2 — EntityRef vs Entity guidance
- **File**: `docs/models.md`
- [ ] Add: EntityRef = lightweight reference in credits/tracklist; Entity = full persistent record stored separately
- [ ] Note: `Work.credits` contains `EntityRef`, not `Entity`

### 10.3 — `NORMALISE_TITLE_VERSION` pin ✅
- [x] `NORMALISE_TITLE_VERSION = 1` added to `text/normalize.py`
- [x] Exported via `text/__init__`
- [ ] Document in `docs/mediavocab_spec.md` §6.3 — note that changing normalise_title() requires bumping this constant and a major version bump
- [ ] Expand `test_normalise_title_pins.py` golden values to cover non-Latin scripts (Japanese, Arabic, Chinese)

---

## Phase 11 — Examples

### 11.1 — Signals lifecycle example
- **File**: `examples/19_signals_pipeline_roles.py`
- [ ] Update to use `Signals.as_query()` / `Signals.as_observation()` / `Signals.as_result()`
- [ ] Show `compare_signals()` detecting a year disagreement between two providers

### 11.2 — WorkRelation + VariantKind example
- **File**: `examples/21_variant_kind_and_relation.py` (new)
- [ ] Theatrical cut Work + director's cut Work linked via `WorkRelation(DERIVED_FROM, theatrical)` + `variant_kind=DIRECTORS`

### 11.3 — Verify existing examples still run
- [ ] `python -m py_compile examples/*.py` — no syntax errors (some may import removed names)
- [ ] Fix any examples that imported `Programme`, `Schedule`, `classify_video`, `quality_score`, `best_release`, or `ContentType`

---

## Phase 12 — CI & packaging

### 12.1 — Coverage gate ✅
- [x] `min_coverage` raised from 0 to 85
- [x] `test_path` corrected from `test/` to `tests/`

### 12.2 — `KNOWN_EXTERNAL_IDS` ✅
- [x] Added to `external_ids.py` and exported from `mediavocab.__init__`

### 12.3 — pyproject.toml audit
- **File**: `pyproject.toml`
- [ ] Confirm `Homepage` URL is correct
- [ ] Confirm `classifiers` includes `Development Status :: 5 - Production/Stable`
- [ ] Confirm no stale extras or obsolete deps

### 12.4 — Pre-release checklist for v1.1.0
- [ ] All remaining `[ ]` items above checked off
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
