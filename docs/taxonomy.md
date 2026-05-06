# Taxonomy reference

All enums inherit `(str, Enum)` so values compare equal to their string
representation: `MediaType.MOVIE == "movie"`. This makes them safe to use in
JSON, env vars, and dict keys without conversion.

## `MediaType` (17 values)

The top-level classification of a Work. Determines schema, external databases,
and comparison tolerances.

| Value | Use for |
|---|---|
| `MOVIE` | Feature films, short films, documentaries (with `GENRE_DOCUMENTARY`) |
| `TV` | Episodic video — series and individual episodes |
| `MUSIC` | Audio with music-pipeline identity (artist, ISRC, MusicBrainz) |
| `MUSIC_VIDEO` | Promotional / performance video for a musical work |
| `PODCAST` | Episodic non-music audio via RSS or podcast platforms |
| `AUDIOBOOK` | Complete narrated literary work, single narrator |
| `AUDIO_DRAMA` | Performed audio with cast, director, sound design |
| `RADIO` | Stations and broadcast programmes |
| `BOOK` | Text-based written works |
| `COMIC` | Sequential art (singles, GNs, manga, manhwa, manhua, webcomics) |
| `GAME` | Video games (any platform) |
| `INTERACTIVE_FICTION` | Text-/voice-driven branching narrative (Inform, Twine, Alexa Skills) |
| `STAGE` | Live theatrical productions (plays, musicals, opera, ballet) |
| `SOUND_EFFECT` | Short triggered audio clips (one-shots) |
| `AMBIENT_SOUNDS` | Procedurally generated / looping environment audio |
| `GENERIC` | Type unknown; further resolution may clarify |
| `NOT_MEDIA` | Terminal classifier sentinel — definitely not a media request |

## `VariantKind`

Cuts: `THEATRICAL`, `DIRECTORS`, `EXTENDED`. Fan: `FANEDIT`, `TV_TO_MOVIE`,
`MOVIE_TO_TV`. Restoration: `PRESERVATION`, `COLORIZED`, `REMASTERED`,
`UPSCALED`. Packaging: `DELUXE`, `REISSUE`, `COMPILATION`, `REGIONAL`,
`BOOTLEG`. Catch-all: `OTHER`.

A canonical/default edition uses `variant_kind=None` — `STANDARD` is
intentionally absent.

## `EntityKind` (7 values)

| Value | Use for |
|---|---|
| `PERSON` | Any human individual |
| `GROUP` | Band, ensemble, theatre company, comedy duo (has temporal members) |
| `ORGANISATION` | Label, publisher, studio, broadcaster, dev studio |
| `SERIES` | Container: TV franchise, book series, podcast show |
| `DEVICE` | Physical playback endpoint: smart speaker, smart plug, console |
| `EVENT` | Bounded real-world grouping: tour, festival, convention |
| `OTHER` | Catch-all |

`Entity.extra["primary_role"]` records professional identity ("primarily an
actor") when needed; that's not a schema concern.

## `RelationRole`

Music: `PERFORMER`, `COMPOSER`, `LYRICIST`, `PRODUCER`, `FEATURING`, `REMIXER`.
Film/TV: `DIRECTOR`, `SCREENWRITER`, `ACTOR`, `CINEMATOGRAPHER`, `EDITOR`.
Books/comics: `AUTHOR`, `ILLUSTRATOR`, `TRANSLATOR`, `NARRATOR`.
Podcast/radio: `HOST`, `GUEST`. Game: `DEVELOPER`, `PORTER`. Release
infrastructure: `PUBLISHER`, `LABEL`, `DISTRIBUTOR`. Generic fallback:
`CREATOR`, `OTHER`.

`PRODUCER` means *music producer*. A film producer is `CREATOR` with a free
text `role`.

## `CreditSection`

`PRINCIPAL` / `GUEST` / `STAFF`. Same three-way split applies to band
members vs. session players vs. studio crew, and to film cast vs. cameos
vs. crew.

## `MembershipStatus`

`CURRENT`, `PAST`, `LIVE`, `GUEST`, `INACTIVE`. **`date_to=None` does not
mean "current"** — check `status` (a defunct band's last member has
`date_to=None` + `status=INACTIVE`).

## `ReleaseStatus`

`RELEASED`, `ANNOUNCED`, `IN_PRODUCTION`, `CANCELLED`, `WITHDRAWN`, `UNKNOWN`.

`WITHDRAWN` is the "shipped, then pulled" state — out of print, removed from
streaming, rights reverted. Distinct from `CANCELLED` (never shipped).

## `StreamMode`

`ON_DEMAND` (default) / `LIVE` / `CONTINUOUS`. Looping a track is
`StreamMode` on the Release — *not* an identity property of the Work.

## `WorkRelationKind`

`COVERS`, `SAMPLES`, `ADAPTED_FROM`, `SEQUEL_TO`, `PREQUEL_TO`, `PART_OF`,
`LIVE_VERSION`, `REMIX_OF`, `SOUNDTRACK_FOR`, `PROMOTES`, `BONUS_FOR`,
`DELETED_SCENE`. Used by the optional `WorkRelation` model.

`PROMOTES` covers trailers, teasers, and promotional spots. `BONUS_FOR`
covers behind-the-scenes featurettes, gag reels, and commentary tracks.
`DELETED_SCENE` covers scenes cut from another work and not present in its
canonical edit.

## `genre.py` constants

Canonical lowercase spellings — additive only. The package ships constants for
the major narrative genres (`HORROR`, `COMEDY`, `DRAMA`, `THRILLER`, `SCI_FI`,
`FANTASY`, `ROMANCE`, `WESTERN`, `MYSTERY`, `ACTION`, `ADVENTURE`, `CRIME`,
`WAR`, `HISTORICAL`, `BIOGRAPHY`, `MUSICAL`, `FAMILY`), the major music genres
(`ROCK`, `POP`, `JAZZ`, `CLASSICAL`, `ELECTRONIC`, `METAL`, `PUNK`, `FOLK`,
`BLUES`, `COUNTRY`, `INDIE`, `REGGAE`, `LATIN`, `RNB`, `SOUL`, `FUNK`, `DISCO`,
`HOUSE`, `TECHNO`, `TRANCE`, `DUBSTEP`, `DRUM_AND_BASS`), and niche tags
(`ASMR`, `AMBIENT`, `MOTION_COMIC`, `VOICE_GAME`, `SFX_NATURE`, etc.).
Cross-type tags (`ADULT`, `AI_GENERATED`) apply alongside any other.



Genre is a free `List[str]` on `Work.content_genres`. The `mediavocab.taxonomy.genre`
module exposes canonical lowercase spellings as constants
(`GENRE_ANIME`, `GENRE_ASMR`, `GENRE_ADULT`, `GENRE_MOTION_COMIC`,
`GENRE_SFX_NATURE`, …) so consumer projects spell the same genres the same
way. Adding new constants is non-breaking; renaming an existing constant value
is a breaking change.
