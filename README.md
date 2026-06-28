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
band lineups, radio stations, IoT device routing, work comparison, and the
pipeline-sentinel `NOT_MEDIA` / `CONTROL` flow.

## What's in the box

| Module | Contents |
|---|---|
| `mediavocab.taxonomy` | `MediaType` (+ `PIPELINE_SENTINELS`), `VariantKind`, `ReleasePackaging`, `EntityKind`, `OrganisationKind`, `RelationRole`, `CreditSection`, `MembershipKind`, `TemporalState`, `ReleaseStatus`, `StreamMode`, `WorkRelationKind`, `ReleaseRelationKind`, `ContentForm`, `ProgrammeFormat`, `AccessibilityKind`, `PlaybackType`, plus `GENRE_*` string constants. Zero deps. |
| `mediavocab.models` | `Work`, `Release`, `Appearance`, `Chapter`, `AccessibilityTrack`, `AvailabilityWindow`, `LocalizedTitle`, `WorkRelation`, `ReleaseRelation`, `Entity`, `EntityRef`, `Membership`, `Credit`, `ExternalIds`, `License`, `Signals`. Pydantic v2. |
| `mediavocab.text` | Normalisation, fuzzy matching, work / release comparison and scoring, SHA-256 identity hashes (`work_hash` / `release_hash`), merge with `MergeStrategy` / `IdentityConflict`, title parser, content classifier, ISO 639 / 3166 / 8601 / ISBN helpers. Stdlib only. |
| `mediavocab.helpers` | Classifier predicates (`is_not_media`, `is_device_entity`, `is_continuous_release`), credit lookups (`director`, `author`, `performers`, `filmography_of`, `episodes_of`), and release availability / rights predicates (`is_available`, `release_is_open`, `release_allows_commercial`). Non-normative. |

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

## Traceability — code cites the spec

The formal specification ([`docs/mediavocab_spec.md`](./docs/mediavocab_spec.md),
`SPEC_VERSION`) is **prescriptive**: it is the source of truth, and the code
implements it. Its §2 axioms (A1–A9) and theorems (T1–T9), together with §3–§8,
admit and justify every axis, enum value, model field, and operation.

So the two stay bidirectionally traceable, every public enum, model, and
operation carries a **greppable clause citation** in its docstring naming the
axiom / theorem / section that admits it, in the form `(spec: <clause>)` — e.g.
`(spec: A1, §3.2/§4.1)` on `MediaType`, `(spec: A8a, §3.3/§4.2)` on
`ContentForm`, `(spec: §6.3, A6)` on `work_hash`. Field-level comments cite the
§1.5 identity / routing / description family and, for identity-hash inputs, the
hash rule (e.g. `content_form` → A8b enters `work_hash` §6.3; routing fields →
excluded by A6). Validators cite the axiom they enforce (sentinel rejection →
T8; one-MediaType-for-life → A4; `org_kind` warn → §4.5/A9).

Grep the convention with `grep -rn "(spec:" mediavocab/`. To find which clause
governs a symbol, open it; to find the code for a clause, grep the clause id
(e.g. `grep -rn "A8b" mediavocab/`).

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
