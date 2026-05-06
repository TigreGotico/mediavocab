# Interactive fiction and voice games

`MediaType.INTERACTIVE_FICTION` covers parser-based IF (Inform 7, Infocom),
choice-based IF (Twine, ChoiceScript, Ink), and voice-driven narrative apps
(Alexa Skills, Google Actions, Mycroft Skills).

## Why a separate type from `GAME`

`GAME` records belong on IGDB, MobyGames, Steam — platforms tracking binary
distributions. `INTERACTIVE_FICTION` records belong on **IFDB.org** (the
Interactive Fiction Database) and ifiction.org. The schemas diverge:

| | `GAME` | `INTERACTIVE_FICTION` |
|---|---|---|
| Principal credit | developer / studio | author |
| Distribution | platform binary (Steam, PSN) | story file or skill ID |
| `source_format` | `"PC"`, `"PS4"`, `"Switch"` | `"Z-machine"`, `"Glulx"`, `"Twine"`, `"Alexa Skill"` |
| External DBs | `igdb`, `mobygames`, `steam` | `ifdb`, `ifiction`, `alexa_skill` |

A graphic adventure with a parser (Sierra-era titles) is `GAME` — it ships as
a platform binary. A voice-only branching narrative on Alexa is
`INTERACTIVE_FICTION` — there is no binary at all.

## Modelling

```python
from mediavocab import (
    MediaType, Work, Release, Credit, EntityKind, EntityRef, RelationRole,
)
from mediavocab.taxonomy import GENRE_PARSER_IF, GENRE_BRANCHING
from mediavocab.models import external_ids as eid

work = Work(
    title="Counterfeit Monkey",
    media_type=MediaType.INTERACTIVE_FICTION,
    year=2012,
    content_genres=[GENRE_PARSER_IF, GENRE_BRANCHING],
    credits=[Credit(
        entity=EntityRef(name="Emily Short", kind=EntityKind.PERSON),
        role="author",
        relation_role=RelationRole.AUTHOR,
    )],
    external_ids={eid.IFDB: "lr40jhwqgyx9rzfr"},
)
Release(work=work, source_format="Glulx", uri="https://...")
```

Voice-game IF: same MediaType, `source_format="Alexa Skill"`,
`content_genres=[GENRE_VOICE_GAME, GENRE_BRANCHING]`,
`external_ids={"alexa_skill": "amzn1.ask.skill.<uuid>"}`.

## IFDB naming collision (resolved)

Two databases have historically been called "IFDB":

- **IFDB.org** — Interactive Fiction Database. `external_ids` key: `ifdb`.
- **Internet Fanedit Database** (the fanedit.org community catalogue).
  `external_ids` key: `fanedit_ifdb`.

The shorter `ifdb` is reserved for the Interactive Fiction Database, which is
the more widely cited externally. Fanedit catalogues use `fanedit_ifdb`.
