# mediavocab

Reference vocabulary and pydantic data model for cataloguing media works:
movies, music, books, comics, games, podcasts, audio dramas, radio,
sound effects, and procedural ambient streams — all in a single shared
schema.

`mediavocab` is a foundation library. It defines the *vocabulary* (enums,
genre constants) and the *structural models* (Work, Release, Entity, Credit,
Membership, Appearance). Application logic — provider clients, resolvers,
playback, UI — lives outside this package.

## Install

```bash
pip install mediavocab
```

The only runtime dependency is `pydantic>=2`. The `taxonomy/` and `text/`
subpackages import nothing beyond the stdlib, so they are safe to vendor in
minimal environments.

## Quickstart

```python
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType,
    RelationRole, Release, VariantKind, Work, WorkRelation, WorkRelationKind,
)
from mediavocab.text import score, work_hash

# Each cut is its own Work (spec §3.4); director's cut links via WorkRelation.
theatrical = Work(
    title="Blade Runner", media_type=MediaType.MOVIE,
    year=1982, runtime=117 * 60.0, production_country="US",
    variant_kind=VariantKind.THEATRICAL,
    credits=[Credit(
        entity=EntityRef(name="Ridley Scott", kind=EntityKind.PERSON),
        role="Director", relation_role=RelationRole.DIRECTOR,
        section=CreditSection.PRINCIPAL,
    )],
)
directors = Work(
    title="Blade Runner", media_type=MediaType.MOVIE,
    year=1992, runtime=116 * 60.0, production_country="US",
    variant_kind=VariantKind.DIRECTORS,
    relations=[WorkRelation(kind=WorkRelationKind.DERIVED_FROM, target=theatrical)],
)

# A Release manifests a Work — many formats, mirrors, packages per Work.
bluray = Release(work=theatrical, container="Blu-ray", region="US",
                 uri="file:///library/blade-runner.mkv")

print(work_hash(theatrical))            # stable SHA-256 identity hash
print(score(theatrical, theatrical))    # 1.0 (self-match)
```

More walked-through examples in [`examples/`](./examples/) covering albums,
band lineups, radio stations, IoT device routing, work comparison, the
pipeline-sentinel `NOT_MEDIA` / `CONTROL` flow, and broadcast schedules.

## What's in the box

| Module | Contents |
|---|---|
| `mediavocab.taxonomy` | `MediaType` (+ `PIPELINE_SENTINELS`), `VariantKind`, `ReleasePackaging`, `EntityKind`, `OrganisationKind`, `RelationRole`, `CreditSection`, `MembershipKind`, `TemporalState`, `ReleaseStatus`, `StreamMode`, `WorkRelationKind`, `ReleaseRelationKind`, `ContentForm`, `ProgrammeFormat`, `AccessibilityKind`, `PlaybackType`, plus `GENRE_*` string constants. Zero deps. |
| `mediavocab.models` | `Work`, `Release`, `Appearance`, `Chapter`, `AccessibilityTrack`, `AvailabilityWindow`, `LocalizedTitle`, `WorkRelation`, `ReleaseRelation`, `Entity`, `EntityRef`, `Membership`, `Credit`, `Programme`, `Schedule`, `ExternalIds`, `License`, `Signals`. Pydantic v2. |
| `mediavocab.text` | Normalisation, fuzzy matching, work / release comparison and scoring, SHA-256 identity hashes (`work_hash` / `release_hash`), merge with `MergeStrategy` / `IdentityConflict`, title parser, content classifier, ISO 639 / 3166 / 8601 / ISBN helpers. Stdlib only. |
| `mediavocab.helpers` | Classifier predicates (`is_not_media`, `is_device_entity`, `is_continuous_release`), credit lookups (`director`, `author`, `performers`, `filmography_of`, `episodes_of`), and release ranking (`quality_score`, `best_release`). Non-normative. |

## Design highlights

- **A type earns its place by changing the schema (A1).** `SOUND_EFFECT`,
  `PROCEDURAL_AMBIENT`, `AUDIO_DRAMA`, `MUSIC_VIDEO`, etc. each catalogue
  against different external databases or with different runtime tolerances.
- **Devices are entities, not works (A3).** `EntityKind.DEVICE` represents
  physical playback endpoints. The Work is still a RADIO/MOVIE/MUSIC; the
  device is how the consumer routes playback. A receiver-class device
  additionally has a `Work` counterpart for *"turn on the radio"* invocation.
- **Pipeline sentinels never reach a canonical Work (T8).** `MediaType.GENERIC`,
  `NOT_MEDIA`, and `CONTROL` live on the resolver bag and are rejected at
  `Work` construction.
- **Each cut is its own Work (§3.4).** Theatrical, director's, extended,
  remaster, fanedit — restructurings of the canonical artefact each get a
  new Work linked by `WorkRelation`. `ReleasePackaging` (deluxe / reissue /
  box-set / bootleg) is independent — that's how an edition ships.
- **`PlaybackType` is derived from `MediaType` (A6).** `AUDIO` / `VIDEO` /
  `PAGED` / `INTERACTIVE` routes resolver dispatch by playback intent. Never
  persisted on Work or Release. Declare
  `playback_type: ClassVar[Set[PlaybackType]]` on each provider.
- **Genre is a free `List[str]`** with canonical spellings in
  `mediavocab.taxonomy.genre`. ASMR, ambient, anime, adult, etc. are genre
  tags applied across multiple media types — not types of their own (T1).
  Programme formats (documentary, concert, talk show) live in
  `ProgrammeFormat`, not in genres.

See [`docs/`](./docs/) for full reference and pattern guides.

## Workspace position

`mediavocab` sits at the bottom of the stack. Every other package in
this workspace depends on it:

```
                          mediavocab
                              ▲
        ┌───────────┬─────────┼─────────┬───────────┐
        │           │         │         │           │
      tutubo   pyfanedit   pymetal   pyo*…       py_bandcamp / nuvem-de-som
        ▲           ▲         ▲                       ▲
        └────────┬──┴─────────┴───────────────────────┘
                 │
              metadatarr  ◄── canonical resolver, ships every provider above
                 ▲
                 │
           media-archivist  ◄── source-DB orchestrator + sidecars + CLI/server
```

- **mediavocab**: vocabulary + structural models (this package).
- **tutubo**, **pyfanedit**, **pymetal**, **py_bandcamp**, **nuvem_de_som**,
  **radiosoma**, **tunein**, **audiobooker**: API clients / scrapers. Each
  emits `mediavocab.Work` / `Release` / `Entity` directly.
- **metadatarr**: cross-source resolver framework. Bundles every
  first-party scraper as a hard runtime dep (no extras juggling) and
  ships ~24 providers under `metadatarr.resolve.providers`.
- **media-archivist**: local source-DB indexer / canonicalizer /
  CLI / web server. Consumes metadatarr's resolver.

## Testing

```bash
pip install -e ".[test]"
pytest -q
```

## License

Apache 2.0. See [LICENSE](./LICENSE).
