# mediavocab
<!-- agent-hint
covers: what mediavocab is, the install, a quickstart and the documentation pages
source: pyproject.toml, mediavocab/__init__.py
generated: no
verify: diff <(sed -n '/^```python/,/^```$/p' README.md | sed '1d;$d' | python -) <(grep -o '^print(.*# [^ ]*' README.md | sed 's/.*# //')
see: docs/README.md, docs/overview.md
-->

Reference vocabulary and pydantic data model for cataloguing media works:
movies, music, books, comics, games, podcasts, audio dramas, radio,
sound effects, and procedural ambient streams: all in a single shared
schema.

`mediavocab` is a foundation library. It defines the *vocabulary* (enums,
genre constants) and the *structural models* (Work, Release, Entity, Credit,
Membership, Appearance). Application logic (provider clients, resolvers,
playback, UI) lives outside this package.

## Install

```bash
pip install mediavocab
```

## Quickstart

```python
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType,
    RelationRole, Release, VariantKind, Work,
)
from mediavocab.text import score, work_hash

# Each cut is its own Work (spec §3.4).
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

# A Release manifests a Work. One Work has many Releases.
bluray = Release(work=theatrical, container="Blu-ray", region="US",
                 uri="file:///library/blade-runner.mkv")

print(work_hash(theatrical))            # 3556a92e13ac5b48ef2c6a523bc7551edfc588eb7491fcf03faaf21ec17b3dc9
print(score(theatrical, theatrical))    # 1.0 (self-match)
```

More examples are in [`examples/`](./examples/): albums, band lineups,
radio stations, IoT device routing, work comparison, and the pipeline
sentinels `NOT_MEDIA` and `CONTROL`.

## Documentation

| Page | Read it for |
| :--- | :--- |
| [Overview](docs/overview.md) | the modules, the design rules, and the packages that depend on mediavocab |
| [Quickstart](docs/quickstart.md) | a walk-through of the main models |
| [Specification](docs/mediavocab_spec.md) | the axioms and theorems that the code implements |
| [Index](docs/README.md) | every reference page and pattern guide |

Contributors: [AGENTS.md](AGENTS.md) gives the repo map and the test commands.

## License

Apache 2.0. See [LICENSE](./LICENSE).
