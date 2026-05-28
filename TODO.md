# mediavocab — Production Roadmap

All phases complete. **601 tests passing, 88% coverage, ruff clean.**

---

## Status: v1.1.0 ready ✅

### Completed this session

| Phase | What was done |
|-------|---------------|
| 0 | Baseline verified |
| 1.1 | `ExternalIds.extra` → `Dict[str, Any]` |
| 1.2 | `ProviderMatch.confidence` already validated via Field |
| 1.3 | `Credit` logs WARNING on role/relation_role mismatch |
| 1.4 | `Release.license` → `Optional[License]`, coerces strings on intake |
| 1.5 | `KNOWN_GENRES` frozenset (85 genres), `Work.content_genres` normalised on intake |
| 1.6 | `Membership` date order already validated |
| 1.7 | `AvailabilityWindow` uses `iso_compare()` |
| 2 | `SignalsRole` enum + `as_query/as_observation/as_result` lifecycle constructors |
| 3 | Country slot validator already correct ("at most one") |
| 4 | `Programme`, `Schedule`, `ContentType`, `classify_video`, `quality_score`, `best_release` removed outright |
| 4/locale | `locale/__init__.py` rewritten to use `ovos-spec-tools` `LocaleResources` |
| 5 | `content_form` axis removed from routing gate → three-axis |
| 6.1 | `MetadataProvider.__init_subclass__` warns on unknown `genre_filter` values |
| 6.2 | 12 new genre constants added |
| 7 | 11 new external ID constants + `KNOWN_EXTERNAL_IDS` frozenset |
| 8 | `relations_of_kind`, `is_sequel_of`, `is_part_of_series`, `all_cuts`, `release_variants` helpers |
| 9 | `IDENTITY_FIELDS` frozenset (15 fields) |
| 10.3 | `NORMALISE_TITLE_VERSION = 1` pin |
| 11 | `examples/19` updated with lifecycle constructors; `examples/21` new (WorkRelation+VariantKind); stale examples 15 and 18 deleted |
| 12.1 | Coverage gate raised to 85%; `test_path` fixed |
| 12.2 | `KNOWN_EXTERNAL_IDS` frozenset |
| 12.3 | `pyproject.toml` classifier → `5 - Production/Stable`; `ovos-spec-tools` dep added |

### Docs updated
- `docs/mediavocab_spec.md` — A6 three-axis gate, country slot, hash stability pin
- `docs/models.md` — EntityRef vs Entity, WorkRelation vs ReleaseRelation, ExternalIds.extra, Signals lifecycle, MetadataProvider three-axis
- `docs/text-utilities.md` — IDENTITY_FIELDS documented
- `docs/patterns/writing-a-provider.md` — three-axis gate, `as_observation()`, `genre_filter` validation

### Tests added/updated
- `test_genres_canonical.py` — 12 new constants + `KNOWN_GENRES`
- `test_external_id_constants.py` — 11 new IDs + `KNOWN_EXTERNAL_IDS`
- `test_locale.py` — rewritten for ovos-spec-tools loader
- `test_new_features.py` — 27 new tests covering all additions

---

## Deferred to v2.0

Breaking changes — do not implement in v1.x:

- Replace three-role `Signals` with typed `QuerySignals` / `ObservationSignals` / `ResolvedSignals`
- Make `Credit.relation_role` mandatory (drop free-string-only path)
- Change `work_hash` quantum values if real-world collision data warrants it (bump `NORMALISE_TITLE_VERSION`)
- Extract locale `.voc` files to standalone `mediavocab-locale` package

---

## Release checklist for v1.1.0

- [x] All phases above complete
- [x] `python -m pytest tests/ -q` — 601 passed
- [x] `ruff check mediavocab/` — clean
- [x] Coverage ≥ 85% (current: 88%)
- [ ] `pip-audit` — run before release tag
- [ ] `python -m py_compile examples/*.py` — run before release tag
- [ ] Do NOT edit `version.py` — gh-automations bumps from commit prefixes
- [ ] Merge `dev` → `master` to trigger `release_workflow.yml`

---

## Verification

```bash
python -m pytest tests/ -q --tb=short
ruff check mediavocab/

python -c "
from mediavocab import Work, Release, Entity, MediaType
from mediavocab import work_hash, Signals, SignalsRole
from mediavocab import KNOWN_GENRES, KNOWN_EXTERNAL_IDS, NORMALISE_TITLE_VERSION
w = Work(title='Test', media_type=MediaType.MOVIE)
print('work_hash:', work_hash(w)[:16], '...')
print(len(KNOWN_GENRES), 'genres,', len(KNOWN_EXTERNAL_IDS), 'ext IDs')
print('NORMALISE_TITLE_VERSION:', NORMALISE_TITLE_VERSION)
q = Signals.as_query(title='Test')
assert q.role == SignalsRole.QUERY
print('mediavocab OK')
"
```
