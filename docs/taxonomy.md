# Taxonomy reference

All enums inherit `(str, Enum)` so values compare equal to their string
representation: `MediaType.MOVIE == "movie"`. Safe to use in JSON, env
vars, and dict keys without conversion.

## `MediaType` (20 values: 17 concrete + 3 pipeline sentinels)

The top-level classification of a Work. Determines schema, external
databases, and comparison tolerances (A1).

| Value | Use for |
|---|---|
| `MOVIE` | Feature films (with `ProgrammeFormat.DOCUMENTARY` for feature documentaries) |
| `SHORT_FILM` | Festival-circuit short film (≤40 min); disjoint databases per A1(b) |
| `EPISODIC_SERIES` | On-demand episodic video — anime, drama, sitcom, web series |
| `TV` | Live linear / IPTV broadcast channel (parallel to `RADIO`; channel-as-Work) |
| `MUSIC` | Audio with music-pipeline identity (artist, ISRC, MusicBrainz) |
| `MUSIC_VIDEO` | Promotional / performance video for a musical work |
| `PODCAST` | Episodic non-music audio via RSS or podcast platforms |
| `AUDIOBOOK` | Complete narrated literary work, single narrator |
| `AUDIO_DRAMA` | Performed audio with cast, director, sound design |
| `RADIO` | Live linear audio broadcast channel |
| `BOOK` | Text-based written works |
| `COMIC` | Sequential art (singles, GNs, manga, manhwa, manhua, webcomics) |
| `GAME` | Video games (any platform) |
| `INTERACTIVE_FICTION` | Text-/voice-driven branching narrative (Inform, Twine, Alexa Skills) |
| `SOUND_EFFECT` | Short triggered audio clips (one-shots) |
| `PROCEDURAL_AMBIENT` | Generator-platform ambient audio (myNoise, Moodist, Noisli, Endel) |
| `PLAYLIST` | Cross-media-type curated collection (Spotify / YouTube playlist, M3U) |
| `GENERIC` | Pipeline sentinel — type unknown; rejected at Work construction (T8) |
| `NOT_MEDIA` | Pipeline sentinel — definitely not a media request; rejected on Work |
| `CONTROL` | Pipeline sentinel — playback-control verb; rejected on Work |

`PIPELINE_SENTINELS = {GENERIC, NOT_MEDIA, CONTROL}` is exported as a
frozenset for membership checks.

## `VariantKind` (Work-only — §3.4)

Restructurings of the canonical artefact. Each cut is its own Work
linked by `WorkRelation`.

Cuts: `THEATRICAL`, `DIRECTORS`, `EXTENDED`, `FANEDIT`.
Cross-MediaType transformations: `TV_TO_MOVIE`, `MOVIE_TO_TV`.
Restoration: `PRESERVATION`, `COLORIZED`, `REMASTERED`, `UPSCALED`.
Derived aggregations: `COMPILATION`.
Catch-all: `OTHER`.

A canonical/default edition uses `variant_kind=None` — `STANDARD` is
intentionally absent (A2).

## `ReleasePackaging` — Release-level packaging (§3.5)

How a Release is packaged independently of the Works it carries.

`DELUXE`, `REISSUE`, `REGIONAL`, `BOOTLEG`, `BOX_SET`, `PROMO`, `OTHER`.

Description-family (A6); excluded from `release_hash`.

## `ContentForm` — experiential kind (§3.3)

`PRIMARY` (default), `TRAILER`, `TEASER`, `EXCERPT`, `BEHIND_SCENES`,
`REACTION`, `SOCIAL_CLIP`, `SUPPLEMENT`, `OTHER`.

The one human-perception axis admitted to `work_hash` (A8b) — a trailer
for *Inception* and the film *Inception* would otherwise collide on
`(title, year, media_type)`.

## `ProgrammeFormat` — structural format (§3.7)

`CONCERT`, `STAND_UP`, `TALK_SHOW`, `REALITY`, `NEWS`, `SPORTS`, `QUIZ`,
`DOCUMENTARY`, `OTHER`.

Routing axis on `Work.programme_format`; excluded from `work_hash` (A6).

## `EntityKind` and `OrganisationKind`

`PERSON`, `GROUP`, `ORGANISATION`, `SERIES`, `DEVICE`, `OTHER`.

When `kind == ORGANISATION`, `Entity.org_kind` must be set to one of
`LABEL`, `PUBLISHER`, `STUDIO`, `BROADCASTER`, `DEVELOPER`,
`STREAMING_SERVICE`, `DISTRIBUTOR`, `OTHER` (validator enforced).

`PERSON` entities may set `birth_year` / `death_year`; rejected on other
kinds.

## `RelationRole`

Music: `PERFORMER`, `COMPOSER`, `LYRICIST`, `PRODUCER`, `FEATURING`,
`REMIXER`.
Film/TV: `DIRECTOR`, `SCREENWRITER`, `ACTOR`, `CINEMATOGRAPHER`, `EDITOR`.
Books/comics: `AUTHOR`, `ILLUSTRATOR`, `TRANSLATOR`, `NARRATOR`.
Podcast/radio: `HOST`, `GUEST`, `CURATOR`.
Game: `DEVELOPER`, `PORTER`.
Release infrastructure: `PUBLISHER`, `LABEL`, `DISTRIBUTOR`.
Fallback: `CREATOR`, `OTHER`.

`PRODUCER` means *music producer*. A film producer is `CREATOR` with a
free-text `role` note.

## `CreditSection`

`PRINCIPAL` / `GUEST` / `STAFF`. Same three-way split applies to band
members vs. session players vs. studio crew, and to film cast vs.
cameos vs. crew.

## `MembershipKind` × `TemporalState` (§4.8)

Two orthogonal facets (A5). **`date_to=None` does not mean "current"** —
check `temporal`.

`MembershipKind`: `MEMBER`, `TOURING`, `SESSION`.
`TemporalState`: `ACTIVE`, `ENDED`, `INACTIVE_GROUP`.

A current touring member is `(kind=TOURING, temporal=ACTIVE,
date_to=None)`. A defunct band's last guitarist is `(kind=MEMBER,
temporal=INACTIVE_GROUP, date_to=None)`.

## `ReleaseStatus`

`RELEASED`, `ANNOUNCED`, `IN_PRODUCTION`, `CANCELLED`, `WITHDRAWN`,
`UNKNOWN`.

`WITHDRAWN` = "shipped, then pulled" (out of print, removed from
streaming, rights reverted). Distinct from `CANCELLED` (never shipped).

## `StreamMode`

`ON_DEMAND` (default) / `LIVE` / `CONTINUOUS`. Looping a track is
`StreamMode` on the Release — *not* an identity property of the Work
(A3).

## `WorkRelationKind`

`COVERS`, `SAMPLES`, `ADAPTED_FROM`, `SEQUEL_TO`, `PREQUEL_TO`,
`PART_OF`, `LIVE_VERSION`, `REMIX_OF`, `SOUNDTRACK_FOR`, `BONUS_FOR`,
`FANEDIT_OF`, `DLC_FOR`, `EXPANSION_OF`, `DERIVED_FROM`.

`BONUS_FOR` is the catch-all for supplementary content attached to
another Work. `FANEDIT_OF` links a fanedit Work back to its source.
`DERIVED_FROM` is the generic catch-all for cross-channel reissues and
remasters that produce new Works (§3.4).

## `ReleaseRelationKind`

`SUPERSEDES`, `PORT_OF`, `MIRROR_OF`, `DERIVED_FROM`. Use sparingly —
most distinctions are encoded by format / packaging fields plus
`release_hash`.

## `AccessibilityKind`

`SUBTITLES`, `CAPTIONS`, `AUDIO_DESCRIPTION`, `SIGN_LANGUAGE`,
`TRANSCRIPT`, `LYRICS`. Used on `AccessibilityTrack.kind`.

## `PlaybackType` — derived routing axis (§3.8, §4.11)

`mediavocab/taxonomy/modality.py` — derived from `MediaType` (A6);
never persisted on Work or Release.

| Value | Intent |
|---|---|
| `AUDIO` | `MUSIC`, `PODCAST`, `AUDIOBOOK`, `AUDIO_DRAMA`, `RADIO`, `SOUND_EFFECT`, `PROCEDURAL_AMBIENT` |
| `VIDEO` | `MOVIE`, `SHORT_FILM`, `EPISODIC_SERIES`, `TV`, `MUSIC_VIDEO` |
| `PAGED` | `BOOK`, `COMIC` |
| `INTERACTIVE` | `GAME`, `INTERACTIVE_FICTION` |
| `UNKNOWN` | `PLAYLIST`, pipeline sentinels, or no playback intent |

`infer_playback_type(media_type) -> PlaybackType` reads
`MEDIA_TYPE_TO_PLAYBACK_TYPE`. Pass to `Signals.playback_type` when the
caller has no explicit verb hint and wants to constrain the resolver
gate.

Provider declaration:
```python
playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.AUDIO}
```
Empty set means universal. When non-empty, a `Signals` with
`playback_type=None` always passes; a set `Signals.playback_type` must
be a member.

## `genre.py` constants

Canonical lowercase spellings — additive only. Narrative genres
(`HORROR`, `COMEDY`, `DRAMA`, `THRILLER`, `SCI_FI`, `FANTASY`,
`ROMANCE`, `WESTERN`, `MYSTERY`, `ACTION`, `ADVENTURE`, `CRIME`, `WAR`,
`HISTORICAL`, `BIOGRAPHY`, `MUSICAL`, `FAMILY`, `NOIR`), music genres
(`ROCK`, `POP`, `JAZZ`, `CLASSICAL`, `ELECTRONIC`, `METAL`, `PUNK`,
`FOLK`, `BLUES`, `COUNTRY`, `INDIE`, `REGGAE`, `LATIN`, `HIP_HOP`,
`RNB`, `SOUL`, `FUNK`, `DISCO`, `HOUSE`, `TECHNO`, `TRANCE`, `DUBSTEP`,
`DRUM_AND_BASS`), and niche tags (`ASMR`, `AMBIENT`, `MOTION_COMIC`,
`VOICE_GAME`, `SFX_NATURE`, …). Cross-type tags (`ADULT`,
`AI_GENERATED`) apply alongside any other.

Programme formats (concert, stand-up, talk-show, reality, news, sports,
documentary) are NOT in `genre.py` — they live in `ProgrammeFormat`.

Genre is a free `List[str]` on `Work.content_genres`. Adding new
constants is non-breaking; renaming an existing constant value is a
breaking change.
