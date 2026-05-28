# mediavocab — Fix Roadmap

Addresses design critique findings. No new dependencies. Work phases top-to-bottom.
After every phase: `python -m pytest tests/ -q --tb=short && ruff check mediavocab/`

Current baseline: **601 tests, 88% coverage, ruff clean.**

---

## Phase A — Quick wins (pure additions, no breaking changes)

### A1 — `Work.extra` and `Release.extra` are `Dict[str, str]` (typing lie)
- **File**: `mediavocab/models/work.py`
- [ ] Change `Work.extra: Dict[str, str]` → `Dict[str, Any]`; add `Any` to typing import
- [ ] Change `Release.extra: Dict[str, str]` → `Dict[str, Any]`
- [ ] **Acceptance**: `Work(title="x", media_type=MediaType.MOVIE, extra={"count": 42}).extra["count"] == 42`; 601+ tests pass

### A2 — `KNOWN_GENRES` built from `globals()` (fragile)
- **File**: `mediavocab/taxonomy/genre.py`
- [ ] Replace the `globals()`-based frozenset with an explicit tuple of all `GENRE_*` values, then `frozenset(...)` it
- [ ] Verify length is still 85
- [ ] **Acceptance**: `ruff check` clean; `len(KNOWN_GENRES) == 85`; no runtime import of `globals()`

### A3 — `Work.content_genres` unknown values silently pass
- **File**: `mediavocab/models/work.py`
- [ ] In `_normalise_genres` field_validator, after normalising, emit `logging.WARNING` for each genre value not in `KNOWN_GENRES`
- [ ] Import `logging` at module top; add `_LOG = logging.getLogger(__name__)`
- [ ] **Acceptance**: `Work(content_genres=["roock"])` logs a warning; `Work(content_genres=["rock"])` does not; existing tests pass

### A4 — `SPEC_VERSION` constant missing
- **File**: `mediavocab/__init__.py`
- [ ] Add `SPEC_VERSION: str = "1.1"` as a module-level constant
- [ ] Export in `__all__`
- [ ] **Acceptance**: `from mediavocab import SPEC_VERSION; assert SPEC_VERSION == "1.1"`

### A5 — `merge_all()` missing (batch merge)
- **File**: `mediavocab/text/compare.py`, `mediavocab/text/__init__.py`
- [ ] Add `def merge_all(works: List[Work], strategy: MergeStrategy = DEFAULT_STRATEGY) -> Work` — reduces list via `merge()`, raises `ValueError` on empty list
- [ ] Export from `mediavocab.text` and `mediavocab`
- [ ] **Acceptance**: `merge_all([w1, w2, w3])` returns one Work; `merge_all([])` raises `ValueError`; new test

### A6 — `score_breakdown()` missing (score is opaque float)
- **File**: `mediavocab/text/compare.py`, `mediavocab/text/__init__.py`
- [ ] Add `@dataclass ScoreBreakdown: title: float; year: float; media_type: float; runtime: float; country: float; language: float; series: float; bonus: float; total: float`
- [ ] Add `def score_breakdown(query: Work, candidate: Work) -> ScoreBreakdown` — same logic as `score()`, returns per-field components
- [ ] Export from `mediavocab.text` and `mediavocab`
- [ ] **Acceptance**: `score_breakdown(a, b).title` is a float in [0, 1]; `score_breakdown(a, b).total == score(a, b)`; new test

### A7 — `group_by_hash()` missing (dedup helper)
- **File**: `mediavocab/helpers/queries.py`, `mediavocab/helpers/__init__.py`
- [ ] Add `def group_by_hash(works: Iterable[Work]) -> Dict[str, List[Work]]` — groups by `work_hash`, preserving insertion order within each group
- [ ] **Acceptance**: a list of 3 Works where 2 share a hash returns `{hash_a: [w1, w2], hash_b: [w3]}`; new test

### A8 — `is_available()` predicate missing
- **File**: `mediavocab/helpers/queries.py`, `mediavocab/helpers/__init__.py`
- [ ] Add `def is_available(release: Release, region: str = "", at: Optional[str] = None) -> bool`
  - If `region` given and `release.region_locked is True` and `region not in release.regions_available` → False
  - If `at` given (ISO date string) and `release.available_from` and `iso_compare(at, release.available_from) < 0` → False
  - If `at` given and `release.available_until` and `iso_compare(at, release.available_until) > 0` → False
  - If `at` given and `release.availability_windows` is non-empty → True iff `at` falls in at least one window
  - Otherwise True
- [ ] **Acceptance**: tests covering: locked-region rejection, date-before-available rejection, window-matching; new tests

### A9 — `token_sort_ratio()` for title matching (leading articles, re-ordering)
- **File**: `mediavocab/text/normalize.py`, `mediavocab/text/__init__.py`
- [ ] Add `def token_sort_ratio(a: str, b: str) -> float` — normalise both, sort tokens, then run `SequenceMatcher` on the sorted forms; handles "The Dark Knight" ↔ "Dark Knight, The" and "Lord of the Rings, The" ↔ "The Lord of the Rings"
- [ ] Update `score()` in `compare.py` to use `max(fuzzy_ratio(a, b), token_sort_ratio(a, b))` for title scoring
- [ ] Update `match_quality()` in `signals.py` similarly
- [ ] Export `token_sort_ratio` from `mediavocab.text`
- [ ] **Acceptance**: `token_sort_ratio("The Dark Knight", "Dark Knight, The") > 0.95`; `score()` no longer penalises article reordering; new test; existing score tests still pass

---

## Phase B — API improvements

### B1 — `Credit.relation_role` is required (many real credits don't map)
- **File**: `mediavocab/models/entity.py`
- [ ] Change `relation_role: RelationRole` → `relation_role: Optional[RelationRole] = None`
- [ ] Update `_check_role_consistency` validator: if `relation_role` is None and `role` is set, emit WARNING "Credit.relation_role not set — consider mapping role to a RelationRole value"
- [ ] Update all tests that construct `Credit` without `relation_role` to pass (they should already be fine if optional)
- [ ] Fix tests that assert `relation_role` is required (change to assert optional works)
- [ ] Update `credits_with_role`, `director()`, `author()`, `performers()` to guard against `None` relation_role gracefully
- [ ] **Acceptance**: `Credit(entity=ref, role="Colorist")` works without `relation_role`; `credit.relation_role` may be None; existing helpers still work; new test

### B2 — `Entity(kind=ORGANISATION, org_kind=None)` rejected (common ingestion gap)
- **File**: `mediavocab/models/entity.py`
- [ ] Change validator: if `kind == ORGANISATION` and `org_kind is None`, emit WARNING instead of raising `ValueError`
- [ ] Update `test_entity.py` — the test that asserts this raises should now assert it warns instead
- [ ] **Acceptance**: `Entity(name="Warner Bros.", kind=EntityKind.ORGANISATION)` succeeds (with warning); `Entity(kind=EntityKind.PERSON, org_kind=OrganisationKind.LABEL)` still raises

### B3 — `Work.from_signals()` constructor missing (the most-needed function)
- **File**: `mediavocab/models/work.py`
- [ ] Add `@classmethod def from_signals(cls, signals: "Signals", **overrides) -> "Work"` — maps Signals fields to Work fields:
  - `title` → `title` (required; raise ValueError if absent)
  - `medium` → `media_type`
  - `year` → `year`
  - `runtime` → `runtime`
  - `language` → `language`
  - `country` → the appropriate slot via `COUNTRY_SLOT_FOR.get(media_type, "production_country")`
  - `season` → `season`, `episode` → `episode`
  - `variant_kind` → `variant_kind`
  - `edition` → `edition`
  - `source_format` → `source_format`
  - `content_genres` → `content_genres`
  - `**overrides` applied last (allow caller to supply credits, tracklist, external_ids, etc.)
  - Signals fields that have no Work equivalent (`include_variants`, `playback_type`, `role`, `fanedit_subtype`) are silently dropped
- [ ] Export from `mediavocab` (already exported via `Work`)
- [ ] **Acceptance**: `Work.from_signals(Signals.as_result(title="Inception", medium=MediaType.MOVIE, year=2010))` returns a valid Work; `work_hash()` on the result succeeds; new test

### B4 — `all_cuts()` name misleads (returns DERIVED_FROM, not "cuts")
- **File**: `mediavocab/helpers/queries.py`, `mediavocab/helpers/__init__.py`
- [ ] Rename `all_cuts` → `derived_from(work)` — name matches the actual relation kind
- [ ] Keep `all_cuts = derived_from` as an alias for one release cycle
- [ ] Update docstring of `derived_from`: "All DERIVED_FROM WorkRelations — includes alternative cuts, cover recordings, fanedits, adaptations, and any other work derived from this one"
- [ ] **Acceptance**: `derived_from(w)` returns the same result as `all_cuts(w)`; both names work; new test

### B5 — `Release.license` nullable guard friction
- **File**: `mediavocab/helpers/queries.py`, `mediavocab/helpers/__init__.py`
- [ ] Add `def release_is_open(release: Release) -> bool` — returns `release.license.is_open() if release.license else False`
- [ ] Add `def release_requires_attribution(release: Release) -> bool` — same pattern
- [ ] Add `def release_allows_commercial(release: Release) -> bool`
- [ ] **Acceptance**: `release_is_open(Release(work=w))` returns False (no license); `release_is_open(Release(work=w, license="CC-BY-4.0"))` returns True; new test

---

## Phase C — Locale cleanup (no new deps)

### C1 — Delete 506 orphaned `.voc` files (only used by deleted `classify_video`)
- **Files**: `mediavocab/locale/*/` — everything except the 11 voc names used by `title_parse.py`
- [ ] Keep only these basenames in every locale dir: `cut_colorized`, `cut_directors`, `cut_extended`, `cut_fanedit`, `cut_theatrical`, `cut_unrated`, `cut_upscaled`, `edition_anniversary`, `edition_criterion`, `edition_deluxe`, `edition_remastered`, `format_bluray`, `format_cassette`, `format_dvd`, `format_uhd`, `format_vinyl`, `language_dubbed`, `language_subbed`
- [ ] Delete all `.voc` files not in that list (506 files across all locale dirs)
- [ ] Verify `python -m pytest tests/test_locale.py tests/text/test_title_parse.py -v` still passes
- [ ] **Acceptance**: `find mediavocab/locale -name "*.voc" | wc -l` ≤ 144 (18 names × 8 locales max); tests pass

---

## Phase D — Documentation

### D1 — `content_form` in `work_hash` but not in routing gate — document the decision
- **File**: `docs/mediavocab_spec.md` §6.3, `docs/models.md`
- [ ] Add note in §6.3 (work_hash): "`content_form` is included in the hash (A8) because a TRAILER and the PRIMARY work share `(title, year, media_type)` and would otherwise collide. This is orthogonal to the routing gate: no provider declares a `content_form` axis, but callers who catalogue trailers separately need distinct identities."
- [ ] Add same note in `docs/models.md` under Signals section: `content_form` on Signals is a passthrough hint — the default `MetadataProvider.matches()` ignores it, but a custom provider may use it.

### D2 — `helpers/` stability contract — document what "non-normative" means
- **File**: `docs/models.md` (Helpers section)
- [ ] Add paragraph: "Helpers are stable for v1.x — signatures will not change in minor releases. They are 'non-normative' in the spec sense: they add no new semantics beyond what the models already express, and every helper can be replaced by two lines of list comprehension. Use them for convenience; don't depend on them for correctness."

### D3 — `edition` vs `packaging` vs `Work.edition` disambiguation
- **File**: `docs/mediavocab_spec.md` (§5.3 or new subsection)
- [ ] Add decision table:
  - `Work.edition` (str, identity field, in `work_hash`) — use when the edition fundamentally changes the creative content: "Theatrical", "Director's Cut", "Unrated". Two editions of a film that differ in content are two different Works.
  - `Work.variant_kind` (VariantKind enum) — the *type* of restructuring. Set alongside `Work.edition`.
  - `Release.packaging` (ReleasePackaging enum) — how *this release* ships: DELUXE, BOX_SET, REISSUE. Applies to the distribution format, not the content.
  - `Release.edition` (str) — free-form label for this specific release pressing: "Anniversary Edition", "Limited Red Vinyl". Not in `release_hash`; description-family.

### D4 — Add `docs/patterns/quality-and-ranking.md`
- **File**: `docs/patterns/quality-and-ranking.md` (new)
- [ ] Explain what was removed (`quality_score`, `best_release`) and why (application preferences, not vocabulary)
- [ ] Show how to implement ranking: sort by `(release.packaging, release.resolution, release.hdr, release.audio_channels)` using the enum ordering; provide a 15-line reference implementation callers can copy-paste
- [ ] Show `is_available(release, region, at)` as a pre-filter before ranking

### D5 — Add `docs/patterns/classifying-scraped-content.md`
- **File**: `docs/patterns/classifying-scraped-content.md` (new)
- [ ] Explain what was removed (`classify_video`, `ContentType`) and why
- [ ] Show the recommended pipeline: `title_parse(raw) → TitleParseResult` → build `Signals.as_query(title=result.title, year=result.year, variant_kind=result.variant_kind)` → pass to resolver → use `Work.from_signals(result_signals)` to get a typed Work
- [ ] Show how `content_genres` can be set from known channel tags or domain knowledge before resolution

---

## Phase E — Schema.org export (no new deps)

### E1 — `mediavocab.io.schema_org` module
- **File**: `mediavocab/io/__init__.py` (new dir), `mediavocab/io/schema_org.py` (new)
- [ ] Add `def work_to_schema_org(work: Work) -> dict` — returns a JSON-LD-compatible dict:
  - `@context: "https://schema.org"`
  - `@type`: derived from `media_type` (MOVIE→"Movie", MUSIC→"MusicRecording", BOOK→"Book", EPISODIC_SERIES→"TVSeries", PODCAST→"PodcastSeries", GAME→"VideoGame", COMIC→"ComicStory", etc.)
  - `name`: `work.title`
  - `datePublished`: `str(work.year)` if set
  - `inLanguage`: `work.language` if set
  - `duration`: ISO 8601 duration string from `work.runtime` if set (e.g. `PT1H47M`)
  - `genre`: `list(work.content_genres)` if set
  - `countryOfOrigin`: `{"@type": "Country", "name": work.country()}` if non-empty
- [ ] Add `def release_to_schema_org(release: Release) -> dict` — wraps `work_to_schema_org(release.work)` and adds:
  - `url`: `release.uri` if set
  - `contentUrl`: same
  - `encodingFormat`: `release.container` if set
  - `license`: `release.license.url` if set and non-empty
  - `availableInCountry`: `release.regions_available` if set
- [ ] Export `work_to_schema_org`, `release_to_schema_org` from `mediavocab.io`
- [ ] Add tests in `tests/test_schema_org.py`
- [ ] **Acceptance**: `work_to_schema_org(Work(title="Inception", media_type=MediaType.MOVIE, year=2010))["@type"] == "Movie"`

---

## Phase F — Final checks

### F1 — Update `NORMALISE_TITLE_VERSION` if `token_sort_ratio` changes `score()`
- [ ] `score()` now uses `max(fuzzy_ratio, token_sort_ratio)` for titles — this changes score outputs but NOT `normalise_title()` behaviour
- [ ] `NORMALISE_TITLE_VERSION` only tracks `normalise_title()` — no bump needed for score changes
- [ ] Add test asserting known `score()` values didn't regress (compare a few golden pairs)

### F2 — Pre-release checklist for v1.1.0
- [ ] All A–E phases checked off
- [ ] `python -m pytest tests/ -q` — zero failures
- [ ] Coverage ≥ 85%
- [ ] `ruff check mediavocab/` — clean
- [ ] `pip-audit` — clean
- [ ] `python -m py_compile examples/*.py` — clean
- [ ] Do NOT edit `version.py`
- [ ] Merge `dev` → `master` to trigger `release_workflow.yml`

---

## Verification commands

```bash
python -m pytest tests/ -q --tb=short
ruff check mediavocab/

python -c "
from mediavocab import Work, Release, MediaType, SPEC_VERSION, KNOWN_GENRES
from mediavocab.text import merge_all, score_breakdown, token_sort_ratio
from mediavocab.helpers import group_by_hash, is_available, derived_from, release_is_open
w = Work.from_signals(__import__('mediavocab').Signals.as_result(title='Inception', medium=MediaType.MOVIE, year=2010))
print('Work.from_signals:', w.title, w.year)
print('SPEC_VERSION:', SPEC_VERSION)
print('token_sort_ratio:', token_sort_ratio('The Dark Knight', 'Dark Knight, The'))
print('mediavocab OK')
"
```
