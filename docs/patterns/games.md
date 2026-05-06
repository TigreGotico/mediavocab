# Games

See spec §8.4 for full discussion. Key patterns:

- **Canonical game = `Work`**, ports / ROMs / platform variants = `Release`.
  The Work is the abstract game; the Release encodes platform via
  `source_format` (`"SNES ROM"`, `"PC"`, `"PS4"`, `"Switch"`).
- **Console ports** are different Releases of the same Work, optionally
  credited with `RelationRole.PORTER` for the porting studio.
- **Romhacks** are different Works (the romhack is its own creative work)
  with a `WorkRelation(kind=ADAPTED_FROM)` pointing to the original.
- **The emulator / player** is the consumer's concern, not modelled.

External-id constants: `igdb`, `mobygames`, `steam`, `gog` in
`mediavocab.models.external_ids`.
