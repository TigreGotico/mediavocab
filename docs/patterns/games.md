# Games

User story for catalogueing a game library across native releases,
console ports, romhacks, DLC, and standalone expansions.

## Canonical model

- **Canonical game = `Work`**, ports / ROMs / platform variants = `Release`.
  The Work is the abstract game; the Release encodes the runtime target
  via `Release.platform` (`"SNES"`, `"PC"`, `"PS4"`, `"Switch"`) and the
  distribution form via `Release.container` (`"ROM"`, `"Steam"`, `"PSN"`).
- **Console ports** are different Releases of the same Work, optionally
  credited with `RelationRole.PORTER` for the porting studio.
- **Romhacks** are different Works (the romhack is its own creative
  work) with a `WorkRelation(kind=ADAPTED_FROM)` pointing to the original.
- **DLC** (non-standalone) is its own Work linked via
  `WorkRelation(kind=DLC_FOR)` to the base game.
- **Standalone expansions** are separate Works linked via
  `WorkRelation(kind=EXPANSION_OF)` — they ship independently but extend
  the base Work.
- **The emulator / player** is the consumer's concern, not modelled.

External-id constants: `IGDB`, `MOBYGAMES`, `STEAM`, `GOG` in
`mediavocab.models.external_ids` (when present).

## Worked example: *Super Mario World* across platforms

```python
from mediavocab import (
    Credit, CreditSection, EntityKind, EntityRef, MediaType, OrganisationKind,
    RelationRole, Release, Work, WorkRelation, WorkRelationKind,
)

nintendo = EntityRef(name="Nintendo", kind=EntityKind.ORGANISATION)

smw = Work(
    title="Super Mario World",
    media_type=MediaType.GAME,
    year=1990,
    production_country="JP",
    credits=[Credit(entity=nintendo, role="Developer",
                    relation_role=RelationRole.DEVELOPER,
                    section=CreditSection.STAFF)],
    external_ids={"igdb": "1070", "mobygames": "6791"},
)

# Original SNES cartridge, Virtual Console re-release, Switch Online.
# Same Work, three Releases.
snes = Release(work=smw, platform="SNES", container="Cartridge",
               region="JP", release_date="1990-11-21")
virtual_console = Release(work=smw, platform="Wii", container="Virtual Console",
                          region="US", release_date="2007-02-05")
switch_online = Release(work=smw, platform="Switch", container="Online",
                        region="US", release_date="2019-09-05")

# A standalone expansion is a NEW Work linked to the base game.
yoshi_island = Work(
    title="Super Mario World 2: Yoshi's Island",
    media_type=MediaType.GAME, year=1995,
    production_country="JP",
    relations=[WorkRelation(kind=WorkRelationKind.EXPANSION_OF, target=smw)],
    external_ids={"igdb": "1072"},
)

# A romhack is a new Work, ADAPTED_FROM the original.
smw_kaizo = Work(
    title="Kaizo Mario World",
    media_type=MediaType.GAME, year=2007,
    production_country="JP",
    relations=[WorkRelation(kind=WorkRelationKind.ADAPTED_FROM, target=smw,
                            note="Fan-made difficulty-extreme romhack")],
)
```

## Why not a `MediaType` per platform?

A1 fails: SNES games and PS4 games share the same authoritative database
(IGDB), the same mandatory schema (developer / publisher / platform), and
the same comparison tolerances. The platform is a *Release* axis (T6);
MediaType stays as `GAME` across every port.
