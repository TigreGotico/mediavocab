# Text utilities

`mediavocab.text` is stdlib-only — no external dependencies. Three modules.

## `mediavocab.text.normalize`

```python
strip_diacritics(text)         # 'café' → 'cafe'
normalize(text)                # full pipeline; suitable for fuzzy comparison
fuzzy_ratio(a, b) -> float     # SequenceMatcher on normalised strings, [0, 1]
best_match(query, candidates)  # → (best, score)
title_words(text)              # tokenise, strip articles
```

`normalize()` strips diacritics, lowercases, removes featured-artist credits
(`(feat. Drake)`, `ft. Someone`), removes parenthetical/bracketed suffixes,
collapses non-word characters, and trims whitespace. Output is canonical for
fuzzy matching.

## `mediavocab.text.compare`

```python
TITLE_MIN  = 0.92
ARTIST_MIN = 0.90
YEAR_WINDOW = 1

RUNTIME_TOLERANCE_S: dict[MediaType, float]    # per-type tolerance

compare(a, b) -> List[Conflict]   # only overlapping disagreements
score(query, candidate) -> float  # [0, 1] match quality
merge(*works) -> Work             # first non-empty value wins; aka unioned
work_hash(w) -> str               # stable SHA-1 over identity fields
```

`work_hash` deliberately excludes `credits`, `aka`, and `content_genres` —
those are not part of canonical identity. The same Work record produced by
two providers with different credit completeness should hash the same.

`score` halves on year mismatch beyond `YEAR_WINDOW`, halves on `MediaType`
mismatch (with `GENERIC` permissive on either side), halves on `country` and
`language` mismatch (when both sides specify them), and — for episodic media
(TV / PODCAST / RADIO / AUDIO_DRAMA) — additionally halves on
`series_title` mismatch and on differing `season` / `episode`. It adds small
bonuses for matching `variant_kind` and overlapping `content_genres`.

`work_hash` includes `series_title` in the identity tuple, alongside
`title`, `year`, `country`, `runtime`, `media_type`, `language`, `season`,
`episode`, `variant_kind`, `edition`, and `source_format`. This prevents
S01E01 collisions across different shows.

## `mediavocab.text.iso`

```python
validate_language(code)    # 'en' / 'eng' → 'en'; raises on unknown
validate_country(code)     # 'us' / 'US' → 'US'; raises on unknown
normalize_language(v)      # 'English' → 'en'
normalize_country(v)       # 'United States' → 'US'
```

Validation is strict — these helpers raise `ValueError` on unknown input.
Models do not auto-validate `language` / `country` fields; call these helpers
explicitly at consumer boundaries.

The embedded ISO data was generated from `pycountry` once at build time;
`pycountry` is **not** a runtime dependency.
