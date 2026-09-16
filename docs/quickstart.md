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
    publication_country="US",
)
```

`Work` is the *canonical* creative work — abstract, no playback URI. To
represent a specific manifestation (a CD pressing, a remaster, a stream URL)
wrap the Work in a `Release`:

```python
from mediavocab import Release, VariantKind, Work, WorkRelation, WorkRelationKind

# Per §3.4, a remaster is a NEW Work, not a Release variant.
remaster_work = Work(
    title="Master of Puppets (Remastered)",
    media_type=MediaType.MUSIC, year=2017,
    runtime=515.0, language="en", publication_country="US",
    variant_kind=VariantKind.REMASTERED,
    relations=[WorkRelation(kind=WorkRelationKind.DERIVED_FROM, target=w)],
)
remaster = Release(
    work=remaster_work,
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
print(work_hash(w))               # stable SHA-256 (64 hex chars)
```

## Parse raw titles

```python
from mediavocab.text import parse_title

r = parse_title("Blade Runner (1982) [Director's Cut] [4K UHD].mkv")
# r.title="Blade Runner"  r.year=1982  r.variant_kind=VariantKind.DIRECTORS
# r.source_format="4K UHD"
```

Locale-aware via the optional `lang=` parameter (`"pt-pt"`, `"es"`,
`"fr-fr"`, …) — the `.voc` keyword tree lives at
`mediavocab/locale/<lang>/`.

## Resolve across providers

`mediavocab.Signals` is the disambiguation bag every cross-source resolver
shares. The `playback_type` field gates which providers are invoked — orthogonal to
`medium` (A6):

```python
from mediavocab import (
    Signals, MediaType, PlaybackType, ExternalIds,
    MetadataProvider, ProviderMatch,
)
from mediavocab.models.signals import compare_signals, signal_hash
from mediavocab import infer_playback_type
from mediavocab.text import release_hash, isbn10_to_13

# "play me Blade Runner" — VIDEO playback_type skips audio-only providers
local = Signals(
    title="Blade Runner", year=1982, medium=MediaType.MOVIE,
    playback_type=PlaybackType.VIDEO,
)

# When the caller has no verb hint, infer from the media type:
# infer_playback_type(MediaType.PODCAST) → PlaybackType.AUDIO
local_audio = Signals(
    title="Hardcore History", medium=MediaType.PODCAST,
    playback_type=infer_playback_type(MediaType.PODCAST),
)

ids = ExternalIds(isbn_10="0-261-10328-8")     # ISBN-13 auto-paired
print(ids.streams)                              # → typed list of playable URLs

# Per-edition dedup across mirrors / availability changes
print(release_hash(remaster))
```

## Filter to available releases

Each cut is its own Work (§3.4); `release.work.variant_kind` carries the
cut and `release.packaging` the edition. mediavocab ships the
availability predicate; ranking by preference (4K > 1080p, Atmos >
stereo) is application logic — see
[`patterns/quality-and-ranking.md`](./patterns/quality-and-ranking.md)
for a reference scorer.

```python
from mediavocab import (
    MediaType, Release, ReleasePackaging, VariantKind, Work,
)
from mediavocab.helpers import is_available

theatrical_work = Work(title="Alien", media_type=MediaType.MOVIE,
                       year=1979, runtime=117 * 60.0,
                       production_country="US",
                       variant_kind=VariantKind.THEATRICAL)
directors_work = Work(title="Alien", media_type=MediaType.MOVIE,
                      year=2003, runtime=116 * 60.0,
                      production_country="US",
                      variant_kind=VariantKind.DIRECTORS)

theatrical = Release(work=theatrical_work, container="Blu-ray",
                     resolution="1080p", audio_channels="5.1",
                     uri="file:///x/theatrical.mkv")
directors  = Release(work=directors_work, container="UHD Blu-ray",
                     resolution="2160p", hdr="Dolby Vision",
                     audio_channels="Atmos",
                     packaging=ReleasePackaging.DELUXE,
                     uri="file:///x/directors.mkv")

accessible = [r for r in (theatrical, directors)
              if is_available(r, region="US")]
```

See `docs/text-utilities.md` for the full text / parsing / classifier
surface and `docs/models.md` for the model catalogue.
