# Text utilities

`mediavocab.text` is stdlib-only — no external dependencies. Six
modules covering normalisation, comparison, parsing, classification,
and validation.

## `mediavocab.text.normalize`

```python
strip_diacritics(text)         # 'café' → 'cafe'
normalize(text)                # full pipeline; suitable for fuzzy comparison
fuzzy_ratio(a, b) -> float     # SequenceMatcher on normalised strings, [0, 1]
best_match(query, candidates)  # → (best, score)
title_words(text)              # tokenise, strip articles
```

`normalize()` strips diacritics, lowercases, removes featured-artist
credits (`(feat. Drake)`, `ft. Someone`), removes parenthetical /
bracketed suffixes, collapses non-word characters, and trims
whitespace. Output is canonical for fuzzy matching.

## `mediavocab.text.compare`

```python
TITLE_MIN  = 0.92
ARTIST_MIN = 0.90
YEAR_WINDOW = 1

# Per-MediaType runtime tolerance == hash quantum (spec §6.2).
# A positive integer N rounds runtime to the nearest N seconds before hashing
# and is also the maximum delta `compare` will accept without flagging a
# conflict. `QUANTUM_SKIP` (-1) excludes runtime from the hash entirely.
RUNTIME_HASH_QUANTUM_S: dict[MediaType, int]
RUNTIME_TOLERANCE_S = RUNTIME_HASH_QUANTUM_S   # alias for clarity at call sites

compare(a, b) -> List[Conflict]   # only overlapping disagreements
score(query, candidate) -> float  # [0, 1] match quality
merge(*works) -> Work             # first non-empty value wins; aka unioned
work_hash(w) -> str               # stable SHA-256 over Work identity fields
release_hash(r) -> str            # stable SHA-256 over Release identity fields

IDENTITY_FIELDS: frozenset[str]   # fields that trigger IdentityConflict on disagreement
```

`IDENTITY_FIELDS` is the authoritative set of 15 field names whose disagreement
constitutes two different Works (and raises `IdentityConflict` in strict merge):
`title`, `media_type`, `content_form`, `year`, `production_country`,
`publication_country`, `broadcaster_country`, `language`, `runtime`,
`season`, `episode`, `series_title`, `variant_kind`, `edition`, `source_format`.
Import via `from mediavocab.text import IDENTITY_FIELDS` or
`from mediavocab.text.compare import IDENTITY_FIELDS`.

`work_hash` deliberately excludes `credits`, `aka`, and
`content_genres` — those are mutable, not part of canonical identity.
The same Work record produced by two providers with different credit
completeness hashes the same. It includes `series_title` to prevent
S01E01 collisions across different shows.

`release_hash` combines `work_hash(release.work)` with the
manifestation-level identity (`variant_kind`, `edition`, `region`,
`container`, `codec`, `bitrate`, `platform`, `resolution`, `hdr`,
`audio_channels`, `sample_rate`, `audio_language`). Two Releases of
the same Work that differ only in `uri` / `image` /
`accessibility` / `release_status` hash identically; a director's
cut on Blu-ray vs DVD does not. Use as a per-edition dedup seed.

`score` halves on year mismatch beyond `YEAR_WINDOW`, halves on
`MediaType` mismatch (with `GENERIC` permissive on either side),
halves on `country` and `language` mismatch (when both sides specify
them), and — for episodic media (`EPISODIC_SERIES` / `PODCAST` /
`RADIO` / `AUDIO_DRAMA`) — additionally halves on `series_title`
mismatch and on differing `season` / `episode`. It adds small bonuses
for matching `variant_kind` and overlapping `content_genres`.

## `mediavocab.text.title_parse`

```python
parse_title(raw, lang=None) -> TitleParseResult
```

Pure regex + locale-vocab parser. Lifts `title`, `year`, `season`,
`episode`, `variant_kind` (a `mediavocab.VariantKind`), `edition`,
`source_format`, `language_hint`, and `aka` from raw title strings
like `"Star.Wars.Episode.IV.1977.Directors.Cut.1080p.BluRay"`. The
`lang` parameter selects the locale vocabulary — see
`mediavocab.locale` and `docs/patterns/...` for available languages.

## `mediavocab.text.classify`

```python
classify_video(title, description="", length=0,
               is_live=False, is_upcoming=False,
               is_official_artist=False, is_podcast=False,
               channel_tags=None, lang=None) -> ClassificationResult
extract_tags(title, description="", lang=None) -> List[str]
```

Title / description / metadata classifier returning a multi-axis
`ClassificationResult` with typed mediavocab fields:

| Field | Type | Notes |
|---|---|---|
| `media_type` | `Optional[MediaType]` | Inferred canonical type, or `None` |
| `content_form` | `ContentForm` | `PRIMARY` / `TRAILER` / `EXCERPT` / … |
| `content_genres` | `List[str]` | Genre tags from `GENRE_*` |
| `programme_format` | `Optional[ProgrammeFormat]` | Documentary / concert / news / … |
| `confidence` | `float` | Rough [0.0, 1.0] hint, not a guarantee |

All fields are optional or have safe defaults — partial results are
valid. `extract_tags` returns orthogonal genre / era / format labels
(horror, full-album, narrated, silent-era, …). Both are locale-aware
via the optional `lang` parameter.

## `mediavocab.text.isbn`

```python
normalize_isbn(value) -> Optional[str]   # strips formatting; preserves trailing X
isbn10_to_13(isbn10)  -> Optional[str]
isbn13_to_10(isbn13)  -> Optional[str]   # None for 979-prefixed (no ISBN-10 form)
```

Pure stdlib. Used by `ExternalIds` to auto-pair ISBN-10 / ISBN-13
representations on construction so two providers using different
conventions don't produce divergent records.

## `IsoDate` — annotated date/datetime validator

`mediavocab.text.IsoDate` (also `from mediavocab.text import IsoDate`) is a
pydantic `Annotated[str, AfterValidator]` type — `mediavocab/_iso_date.py:78`.
Use it on any model field that carries an ISO-8601 date or datetime string.

```python
from mediavocab.text import IsoDate, parse_iso_date
from pydantic import BaseModel

class MyModel(BaseModel):
    release_date: Optional[IsoDate] = None
```

Accepted forms: `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM[:SS[.fff]][Z|±HH:MM]`.
Empty string and `None` pass unchanged (absence is not a value — A2).
The string is returned verbatim; it is never normalised, so dedup hashes remain
stable even when sources provide different precisions.

`parse_iso_date(value) -> Optional[str]` — `mediavocab/_iso_date.py:35` — the
underlying validator function, callable directly when pydantic validation is not
in scope.

## `mediavocab.text.iso`

```python
validate_language(code)    # 'en' / 'eng' → 'en'; raises on unknown
validate_country(code)     # 'us' / 'US' → 'US'; raises on unknown
normalize_language(v)      # 'English' → 'en'
normalize_country(v)       # 'United States' → 'US'
```

Validation is strict — these helpers raise `ValueError` on unknown
input. Models do not auto-validate `language` / `country` fields; call
these helpers explicitly at consumer boundaries.

The embedded ISO data was generated from `pycountry` once at build
time; `pycountry` is **not** a runtime dependency.
