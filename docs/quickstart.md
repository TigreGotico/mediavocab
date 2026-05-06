# Quickstart

```bash
pip install mediavocab
```

## Build a Work

```python
from mediavocab import MediaType, Work

w = Work(
    title="Master of Puppets",
    media_type=MediaType.MUSIC,
    year=1986,
    runtime=515.0,
    language="en",
    country="US",
)
```

`Work` is the *canonical* creative work — abstract, no playback URI. To
represent a specific manifestation (a CD pressing, a remaster, a stream URL)
wrap the Work in a `Release`:

```python
from mediavocab import Release, VariantKind

remaster = Release(
    work=w,
    variant_kind=VariantKind.REMASTERED,
    release_date="2017-11-10",
    uri="file:///library/master-of-puppets-2017.flac",
    container="Digital", codec="FLAC", bitrate="24/96",
)
```

## Add credits

```python
from mediavocab import Credit, EntityKind, EntityRef, RelationRole, CreditSection

w.credits.append(Credit(
    entity=EntityRef(name="James Hetfield", kind=EntityKind.PERSON),
    role="vocals",
    relation_role=RelationRole.PERFORMER,
    section=CreditSection.PRINCIPAL,
))
```

## Compare and score

```python
from mediavocab.text import score, compare, work_hash

other = Work(title="Master of Puppets", media_type=MediaType.MUSIC, year=1986)
print(score(w, other))            # ~1.0
print(compare(w, other))          # []  (no conflicts)
print(work_hash(w))               # stable SHA-1 identity
```

## Use convenience builders

```python
from mediavocab.helpers import make_movie, make_episode, make_release

movie   = make_movie("Alien", year=1979, runtime=117*60.0, director="Ridley Scott")
episode = make_episode("Doctor Who", season=4, episode=10)
release = make_release(movie, "file:///x.mkv")
```

Builders are conveniences only — never required. Construct models directly when
you need fields the builders don't expose.

## Parse raw titles

```python
from mediavocab.text import parse_title

r = parse_title("Blade Runner (1982) [Director's Cut] [4K UHD].mkv")
# r.title="Blade Runner.mkv"  r.year=1982  r.variant_kind=VariantKind.DIRECTORS
# r.source_format="4K UHD"
```

Locale-aware via the optional `lang=` parameter (`"pt-pt"`, `"es"`,
`"fr-fr"`, …) — the `.voc` keyword tree lives at
`mediavocab/locale/<lang>/`.

## Resolve across providers

`mediavocab.Signals` is the disambiguation bag every cross-source
resolver shares; `MetadataProvider` is the typed Protocol every
provider implements:

```python
from mediavocab import (
    Signals, MediaType, ExternalIds,
    MetadataProvider, ProviderMatch,
)
from mediavocab.models.signals import compare_signals, signal_hash
from mediavocab.text import release_hash, isbn10_to_13

local = Signals(title="Blade Runner", year=1982, medium=MediaType.MOVIE)

ids = ExternalIds(isbn_10="0-261-10328-8")     # ISBN-13 auto-paired
print(ids.streams)                              # → typed list of playable URLs

# Per-edition dedup across mirrors / availability changes
print(release_hash(remaster))
```

## Pick the best available release

```python
from mediavocab.helpers.queries import best_release, quality_score

# theatrical BluRay vs 4K remaster
theatrical = make_release(movie, "file:///x/theatrical.mkv",
                          resolution="1080p", audio_channels="5.1")
remaster   = make_release(movie, "file:///x/4k-remaster.mkv",
                          variant_kind=VariantKind.REMASTERED,
                          resolution="2160p", hdr="Dolby Vision",
                          audio_channels="Atmos")

winner = best_release(theatrical, remaster)
print(winner.resolution)   # "2160p"
print(quality_score(theatrical))  # (5, 5, 0, 4, 0)  — lower than remaster
```

`best_release` returns `None` when called with no arguments. List order
breaks ties, so pre-order by preference (local file before stream) before
calling.

## Model a broadcast schedule

```python
from mediavocab import EntityRef, EntityKind
from mediavocab.models.work import Programme, Schedule

bbc_r4 = EntityRef(name="BBC Radio 4", kind=EntityKind.GROUP)
episode_ref = EntityRef(name="Desert Island Discs",
                        external_ids={"tvmaze": "12345"})

slot = Programme(
    work=episode_ref,
    channel=bbc_r4,
    starts_at="2026-05-06T09:00:00Z",
    ends_at="2026-05-06T09:45:00Z",
    is_repeat=False,
)

schedule = Schedule(
    channel=bbc_r4,
    programmes=[slot],
    valid_from="2026-05-06T00:00:00Z",
    valid_until="2026-05-07T00:00:00Z",
    source="tvmaze",
)

# Find what's on at a given instant
from datetime import datetime, timezone
now = "2026-05-06T09:20:00Z"
current = next(
    (p for p in schedule.programmes
     if p.starts_at <= now < (p.ends_at or now + "Z")),
    None,
)
```

`Programme` and `Schedule` are EPG-only models — they are not `Work`
subclasses and carry no playback URI. See `docs/patterns/scheduling.md`
for the full broadcast scheduling pattern.

See `docs/text-utilities.md` for the full text / parsing / classifier
surface and `docs/models.md` for the model catalogue.
