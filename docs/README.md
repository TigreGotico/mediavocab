# mediavocab documentation

Developer-facing reference for the `mediavocab` package. The top-level overview
lives in the repo [README](../README.md).

## Traceability — the spec is prescriptive

[`mediavocab_spec.md`](./mediavocab_spec.md) is the **prescriptive** source of
truth (`SPEC_VERSION`): its §2 axioms (A1–A9) and theorems (T1–T9) plus §3–§8
admit every axis, enum value, model field, and operation. The code implements
the spec and cites it back: every public enum, model, and operation carries a
greppable `(spec: <clause>)` citation in its docstring, field comments cite the
§1.5 identity / routing / description family and the hash rule for identity
inputs, and validators cite the axiom they enforce. Reading a symbol shows which
clause governs it; grep a clause id (e.g. `A8b`, `T8`) to find its code. The
reference pages below mirror the spec section-by-section.

## Index

- [Spec](./mediavocab_spec.md) — prescriptive formal specification (axioms / theorems)
- [Quickstart](./quickstart.md)
- [Taxonomy reference](./taxonomy.md) — every enum value
- [Models reference](./models.md) — every field, decision guides
- [Text utilities](./text-utilities.md) — normalize / compare / iso
- [Stability policy](./stability.md) — what's frozen for 1.x and how it's enforced
- [Migrating to 1.0](./migration-1.0.md) — removals / renames consumers must handle

### Pattern guides

Applied modelling examples for each subdomain:

- [Adult media](./patterns/adult-media.md)
- [Games](./patterns/games.md)
- [Interactive fiction and voice games](./patterns/interactive-fiction.md)
- [Soundtracks](./patterns/soundtracks.md)
- [Motion comics](./patterns/motion-comics.md)
- [Independent creators / YouTube / AI content](./patterns/independent-creators.md)
- [Classifying scraped content](./patterns/classifying-scraped-content.md)
- [Reader-paced and user-paced content](./patterns/reader-paced-content.md)
- [Accessibility tracks and localisation](./patterns/accessibility.md)
- [Box sets and composite Releases](./patterns/box-sets.md)
- [Format, quality, rights, and availability](./patterns/quality-rights-availability.md)
- [Quality and release ranking](./patterns/quality-and-ranking.md)
- [User playlists and live-streamer channels](./patterns/playlists-and-channels.md)
- [IoT devices](./patterns/iot-devices.md)
- [Radio station identity](./patterns/radio.md)
- [Playback-type routing](./patterns/playback-type.md)
- [Writing a metadata provider](./patterns/writing-a-provider.md)
