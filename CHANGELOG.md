# Changelog

## 0.1.0 — 2026-05-06

Initial release.

- `mediavocab.taxonomy`: `MediaType`, `VariantKind`, `EntityKind`, `RelationRole`,
  `CreditSection`, `MembershipStatus`, `ReleaseStatus`, `StreamMode`,
  `WorkRelationKind`, plus `genre.py` constants.
- `mediavocab.models`: `Work`, `Release`, `Appearance`, `WorkRelation`, `Entity`,
  `EntityRef`, `Membership`, `Credit`, `Conflict`, well-known `external_ids` keys.
- `mediavocab.text`: `normalize`, `compare` (with `score`, `merge`, `work_hash`,
  `RUNTIME_TOLERANCE_S`), `iso` (ISO 639-1/-2 + ISO 3166-1 alpha-2 helpers).
- `mediavocab.helpers`: builder shortcuts and classifier predicates.
