# mediavocab — Fix Roadmap

All phases complete. **626 tests, 96% coverage, ruff clean.**

---

## Status: v1.1.0 ready ✅

### Implemented this session (design critique fixes)

| Phase | What was done |
|-------|---------------|
| **A1** | `Work.extra`, `Release.extra`, `Entity.extra` → `Dict[str, Any]` (was a typing lie) |
| **A2** | `KNOWN_GENRES` built from explicit tuple instead of fragile `globals()` scan |
| **A3** | `Work.content_genres` warns on unknown genre values at intake |
| **A4** | `SPEC_VERSION = "1.1"` constant exported from `mediavocab` |
| **A5** | `merge_all(works)` batch merge added |
| **A6** | `ScoreBreakdown` dataclass + `score_breakdown()` per-field decomposition |
| **A7** | `group_by_hash(works)` dedup helper |
| **A8** | `is_available(release, region, at)` availability predicate |
| **A9** | `token_sort_ratio()` in `normalize.py`; `score()`, `match_quality()`, `score_breakdown()` use `max(fuzzy, token_sort)` for titles |
| **B1** | `Credit.relation_role` → `Optional[RelationRole] = None`; warns when absent |
| **B2** | `Entity(kind=ORGANISATION, org_kind=None)` → warns instead of raises |
| **B3** | `Work.from_signals(signals, **overrides)` classmethod |
| **B4** | `derived_from(work)` canonical name; `all_cuts` kept as alias |
| **B5** | `release_is_open/requires_attribution/allows_commercial` helpers |
| **C1** | 512 orphaned `.voc` files deleted (only 18 remain, all used by `title_parse`) |
| **D1** | `docs/mediavocab_spec.md` — edition/packaging disambiguation table |
| **D2** | `docs/models.md` — helpers stability contract clarified |
| **D3** | `docs/mediavocab_spec.md` — `content_form` in hash reasoning documented |
| **D4** | `docs/patterns/quality-and-ranking.md` — new pattern replacing removed `quality_score` |
| **D5** | `docs/patterns/classifying-scraped-content.md` — new pattern replacing removed `classify_video` |
| **E1** | `mediavocab.io.schema_org` — `work_to_schema_org()`, `release_to_schema_org()`; 16 tests |

---

## Remaining known limitations (deferred, no fix without new deps or breaking change)

| Issue | Reason deferred |
|-------|----------------|
| `work_hash` includes `content_form` but routing gate doesn't — documented but inconsistent | Changing the hash is a v1.x-frozen breaking change |
| `ExternalIds.extra="forbid"` vs `.extra` field name collision | Renaming `.extra` is breaking |
| Rights territory model (exclusion-based) | Would require a new `RightsTerritory` model — v2.0 |
| Temporal credits (who had which role and when) | Would require breaking `Credit` model |
| Signals lifecycle still one type (three roles) | Full typed split (`QuerySignals` / `ObservationSignals`) is v2.0 |
| Better fuzzy matching (token_set_ratio w/ multiset intersection) | `rapidfuzz` would help but no new deps |
| ISO language BCP 47 (`zh-Hant`, `sr-Latn`) | `langcodes` would help but no new deps |

---

## Release checklist for v1.1.0

- [x] All phases above complete
- [x] `python -m pytest tests/ -q` — 626 passed
- [x] Coverage ≥ 85% (current: 96%)
- [x] `ruff check mediavocab/` — clean
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
from mediavocab import Work, MediaType, SPEC_VERSION, KNOWN_GENRES
from mediavocab import Signals, SignalsRole
from mediavocab.text import merge_all, score_breakdown, token_sort_ratio
from mediavocab.helpers import group_by_hash, is_available, derived_from, release_is_open
from mediavocab.io import work_to_schema_org

s = Signals.as_observation(title='Inception', medium=MediaType.MOVIE, year=2010).as_result()
w = Work.from_signals(s)
schema = work_to_schema_org(w)

print('SPEC_VERSION:', SPEC_VERSION)
print('Work.from_signals:', w.title, w.year)
print('schema @type:', schema['@type'])
print('token_sort_ratio:', round(token_sort_ratio('The Dark Knight', 'Dark Knight, The'), 3))
print('score_breakdown:', score_breakdown(w, w).total)
print('mediavocab OK')
"
```
