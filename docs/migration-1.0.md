# Migrating to 1.0

The 1.0 line is the breaking cut. After it, removals/renames require a major
bump and a deprecation cycle (see [`stability.md`](stability.md)). This guide
lists every break a consumer must handle to move onto 1.0.

## Removed

| Removed | Replacement |
|---|---|
| `mediavocab.taxonomy.ContentType` (30-value enum) | `classify_video()` returns a multi-axis `ClassificationResult` (`media_type`, `content_form`, `programme_format`, `content_genres`). Collapse to a single facet in the consumer if needed. |
| `ContentType.to_routing()` | Read `media_type` / `content_genres` off the `ClassificationResult` directly. |
| `Programme`, `Schedule` (`models.work`) | Now-playing / schedule is ephemeral delivery state, not catalogue identity (A3). Model a played item as its own `Work`; carry timing in `extra`. |
| `PlaybackModality` | `PlaybackType` (`from mediavocab import PlaybackType`). |
| `taxonomy.modality.infer_modality` | `infer_playback_type`. |
| `text.classify_video_dict` | `classify_video()` → `ClassificationResult`. |

## Changed

| Was | Now |
|---|---|
| `Work.country` (method) | `Work.country` (**property**) — `work.country`, no parens. The value lives in a per-`MediaType` slot (`production_country` / `publication_country` / `broadcaster_country`); set via the slot or `COUNTRY_SLOT_FOR`. There is no flat `country=` kwarg. |
| `Release.codec` / `container` hashed verbatim | Canonicalised before hashing (`normalise_codec` / `normalise_container`) — `"audio/mpeg"` and `"mp3"` now dedup to one `release_hash`. **This changes release identity** for records that stored MIME-form codec/container. |

## Never existed (use these instead)

| Mistakenly referenced | Use |
|---|---|
| `genre.GENRE_NEWS` / `GENRE_TALK_SHOW` / `GENRE_SPORTS` | `ProgrammeFormat.NEWS` / `TALK_SHOW` / `SPORTS` — news/talk/sport are **formats**, not genres (T1). On a `Work`, set `programme_format`. |
| `CHANNEL` relation role | A channel is an `Entity` (`OrganisationKind`) or a `Work` (T4/T9), linked via `PUBLISHER` / `CREATOR`. |

## Notes

- Constructors are lenient (`extra="ignore"`) — an unknown kwarg is dropped
  silently, not rejected. Verify your objects carry what you set (`work.country`,
  field values) rather than assuming a wrong kwarg raised.
- `OrganisationKind` is British-spelled.
