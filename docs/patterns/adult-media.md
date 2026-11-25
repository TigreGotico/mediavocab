# Adult media
<!-- agent-hint
covers: how to model adult media
source: mediavocab/taxonomy/genre.py
generated: no
verify: python -m pytest -q tests/taxonomy/test_genre_constants.py
see: games.md
-->

Adult content fits the existing model with **no new types or enums**.
T1 (genre is not type) does the work: `GENRE_ADULT` is a content tag
applied across MediaTypes, not a type of its own.

- **Content flag**: `content_genres += [GENRE_ADULT]` on any Work, regardless
  of `MediaType`.
- **Scene vs feature**: a feature is a `Work` (`MediaType.MOVIE`). Scenes are
  Works with their own short runtime, collected as `Appearance` entries in
  the feature's `tracklist`. Identical to track-on-album.
- **Performer identity**: `Entity.aliases` for concurrent stage names. Multiple
  `Membership` records for time-sliced name periods (rare).
- **Studio / platform / self-publishing**: `EntityKind.ORGANISATION`. Subscription
  feeds (OnlyFans, Fansly) → `Entity` with platform-as-publisher. Per-clip
  posts get their own `Release` if individually addressable.
- **Hentai**: `MediaType` is `EPISODIC_SERIES` or `MOVIE`.
  `content_genres = [GENRE_ANIME, GENRE_ADULT]`.
- **`external_ids` keys**: `iafd`, `adultfilmdatabase` (constants in
  `mediavocab.models.external_ids`).

---
[← Migrating to 1.0](../migration-1.0.md) · [Home](../README.md) · [Games →](games.md)
