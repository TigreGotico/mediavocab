# mediavocab

Reference vocabulary and pydantic data model for cataloguing media works:
movies, music, books, comics, games, podcasts, audio dramas, radio,
sound effects, and ambient soundscapes — all in a single shared schema.

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
from mediavocab import MediaType, Work, Release, VariantKind
from mediavocab.helpers import make_movie, make_release
from mediavocab.text import score, work_hash

work = make_movie("Blade Runner", year=1982, runtime=117 * 60.0,
                  director="Ridley Scott")
theatrical = make_release(work, "file:///library/blade-runner/theatrical.mkv")
directors  = make_release(work, "file:///library/blade-runner/directors.mkv",
                          variant_kind=VariantKind.DIRECTORS)

print(work_hash(work))                           # stable identity hash
print(score(work, work))                         # 1.0 (self-match)
print(work.model_dump_json())                    # pydantic JSON
```

More walked-through examples in [`examples/`](./examples/) covering albums,
band lineups, radio stations, IoT device routing, work comparison, and the
`NOT_MEDIA` classifier sentinel.

## What's in the box

| Module | Contents |
|---|---|
| `mediavocab.taxonomy` | `MediaType`, `VariantKind`, `EntityKind`, `RelationRole`, `CreditSection`, `MembershipStatus`, `ReleaseStatus`, `StreamMode`, `WorkRelationKind`, plus `GENRE_*` string constants. Zero deps. |
| `mediavocab.models` | `Work`, `Release`, `Appearance`, `WorkRelation`, `Entity`, `EntityRef`, `Membership`, `Credit`, `Conflict`. Pydantic v2. |
| `mediavocab.text` | Normalisation, fuzzy matching, work comparison/scoring, ISO 639/3166 helpers. Stdlib only. |
| `mediavocab.helpers` | Convenience builders and classifier predicates. Non-normative. |

## Design highlights

- **A type earns its place by changing the schema.** `SOUND_EFFECT`,
  `AMBIENT_SOUNDS`, `AUDIO_DRAMA`, `MUSIC_VIDEO`, etc. each catalogue against
  different external databases or with different runtime tolerances.
- **Devices are entities, not works.** `EntityKind.DEVICE` represents physical
  playback endpoints (smart speakers, smart plugs, cast targets). The Work is
  still a RADIO/MOVIE/MUSIC; the device is how the consumer routes playback.
- **`NOT_MEDIA` is a terminal sentinel** for the classifier — distinct from
  `GENERIC`, which is a transient "type unknown, may resolve" state.
- **`Work` is canonical, `Release` is the manifestation.** A director's cut
  is a different Release of the same Work. A bootleg is a different Release
  of the same Work. The Work's identity hash never depends on Release
  metadata.
- **Genre is a free `List[str]`** with canonical spellings in
  `mediavocab.taxonomy.genre`. ASMR, ambient, anime, adult, etc. are genre
  tags applied across multiple media types — not types of their own.

See [`docs/`](./docs/) for full reference and pattern guides.

## Testing

```bash
pip install -e ".[test]"
pytest -q
```

## License

Apache 2.0. See [LICENSE](./LICENSE).
