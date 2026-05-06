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
    source_format="FLAC 24/96",
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
