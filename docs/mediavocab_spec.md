# mediavocab — Formal Specification

**Version:** 0.6-draft  
**Status:** Working draft — iterate before implementation  
**Scope:** Standalone vocabulary and data-model library for any software that catalogues,
resolves, plays, or recommends media content.

---

## 1. Purpose

Every project that touches media content independently re-defines the same vocabulary:
what kinds of media exist, what people and organisations are involved, how editions relate
to canonical works, how band members come and go. The definitions are subtly incompatible,
making cross-project data exchange painful.

`mediavocab` defines these concepts once, prescriptively. It provides the shared
data model; consuming packages provide the application logic — resolving,
scraping, playing, recommending.

### 1.1 Intended consumers

- Metadata resolution libraries
- Media scrapers and archivers
- Media players and streaming clients
- Recommendation engines, deduplication pipelines, library managers
- Any future project in this space

### 1.2 Non-goals

- Provider API clients
- Playback routing or intent classification
- Persistence, deduplication, or ID allocation
- NLU or voice assistant logic
- Any business logic specific to one consumer

---

## 2. Design axioms

These rules govern every inclusion and exclusion decision in this specification.
When in doubt, apply the axiom and document the reasoning.

1. **A `MediaType` value earns its place by changing the schema AND when no orthogonal axis would fit.**
   If two kinds of content require identical fields, the same external databases, and the
   same comparison tolerances, they are the same type. Genre tags distinguish them.

   If a distinction is real but the schema is unchanged, it is an *axis* (modality, regional
   variant, accessibility profile) — see axiom 13. The two-part test prevents the recurring
   failure mode where a real distinction is jammed into `MediaType` because no other home
   exists. Add the axis first; then ask whether `MediaType` still needs the new value.

2. **Genre is not type.**
   Anime is TV with a cultural origin. Documentary is a film with a non-fiction treatment.
   Noir is an aesthetic. None of these change the metadata schema enough to warrant a
   separate `MediaType` value.

3. **Absence is not a value.**
   "Standard edition" means `variant_kind = None`, not `variant_kind = STANDARD`.
   "Ongoing membership" means `date_to = None` combined with `status = CURRENT`.
   Never add an enum value to mark the absence of a distinction.

4. **Delivery mechanism is not identity.**
   A livestream of a radio station is not a different *kind* of content from the station
   itself — it is a Release with a streaming URI. `MediaType` describes what a work IS,
   not how it is delivered.
   **Corollary:** A physical playback device (smart speaker, cast target, smart plug
   connected to legacy hardware) is an `Entity` (`EntityKind.DEVICE`), not a Work.
   Device-mediated requests still resolve to a Work — "turn on the kitchen radio"
   resolves to a `RADIO` Work; "play jazz on Sonos" resolves to `MUSIC`. The device is
   the delivery channel; its identity belongs in `Entity`, not in `MediaType`.

5. **Membership is temporal, not binary.**
   `date_to = None` does NOT mean "current member". A defunct band's last known member
   has `date_to = None` and `status = INACTIVE`. Status and date range are orthogonal
   and must both be stored.

6. **Work ≠ Release ≠ Appearance.**
   "Battery" (the song), "Master of Puppets" (the album), and its position as track 1
   are three distinct concepts. Conflating them makes splits, compilations, reissues,
   and mirrors impossible to model correctly.

7. **Band roster ≠ release lineup.**
   Who is currently *in* a band is different from who *played on* a specific album.
   A producer, a session musician, and a guest vocalist contribute to a specific release
   but are not members of the band.

8. **A station is a Work, not a special case.**
   A radio station or TV channel has a stable cataloguable identity, multiple stream
   URLs (mirrors, bitrates, transmitters), and cross-references across providers exactly
   like a film. Its stream URLs are Releases. Its identity lives in `external_ids`.

9. **If the credit structure changes, it is a schema change — not a genre change.**
   A work that requires a cast list, a director, and a sound designer has a genuinely
   different schema from one that requires a single narrator. That schema difference
   warrants a distinct `MediaType`, regardless of superficial format similarity.
   (Corollary to axiom 1 and 2 — the test that admits `AUDIO_DRAMA`.)

10. **`MediaType` is determined by distribution schema, not by audio or aesthetic content.**
    A rap track is MUSIC because it has an ISRC and appears in music databases — not
    because it contains melody. An ASMR recording is MUSIC if distributed through a
    label, PODCAST if distributed via RSS. `content_genres` handles the aesthetic;
    `MediaType` handles the schema.

11. **Objective technical attributes are fields, not genres.**
    Colour, aspect ratio, frame rate, and similar measurable properties of a work belong
    as typed fields on `Work`, not in `content_genres`. Genre describes thematic or
    cultural character; a technical attribute describes the artefact itself.
    (Corollary that admits `color: Optional[bool]` on `Work`.)

12. **One Work, one `MediaType`. Distribution forks Releases, not Works.**
    A Work has a single `MediaType` for its lifetime. Two distribution channels of the
    same artefact produce two `Release`s of one Work — not two Works. If a single
    artefact has materially different schemas in two channels (an ASMR ISRC release on a
    label and the same recording on an RSS feed), it is two Works linked by a
    `WorkRelation`. The classifier MUST commit to one type at Work-construction time.

13. **Routing axes are orthogonal to identity.**
    A concern that doesn't change the schema earns a typed *field* (typically on `Signals`
    or as a `ClassVar` on `MetadataProvider`), **not** a `MediaType` value. The resolver
    gate is `(media, modality, content_genres, …)`; identity is `(media + identity-fields)`.

    `PlaybackModality` (AUDIO / VIDEO / INTERACTIVE / TEXT / UNKNOWN) is the first such
    axis: a request verb collapses cleanly onto it ("play X" ⇒ AUDIO; "watch X" ⇒ VIDEO),
    a provider declares which modalities it serves, and the gate filters dispatch
    accordingly. Trailers, behind-the-scenes clips, and reactions are not separate
    `MediaType`s — they are `MediaType.GENERIC` with a `content_genres` tag and (typically)
    the right modality.

    Axioms that follow this pattern: an axis must be (a) declarable on `MetadataProvider`
    as a `ClassVar[Set[X]]`, (b) optional on `Signals` (None = no preference), and
    (c) absent from `work_hash` and `release_hash`. Identity does not move; routing
    constrains dispatch.

14. **Provider output flows through typed fields OR `extra` — never both.**
    If a value has a typed home (`external_ids.musicbrainz_release_group`,
    `Signals.modality`, a typed `Stream` in `ExternalIds.streams`), the provider
    populates that. The same value MUST NOT also appear as a `ProviderEntity` relation,
    an `extra` key, or a free string elsewhere in the same match. The consolidator
    dedup contract assumes one source of truth per fact; double-writing produces silent
    conflicts and inflates `match_quality()` scores.

---

## 3. Package structure

```
mediavocab/
│
├── taxonomy/               # Pure str enums — zero dependencies
│   ├── __init__.py         # Re-exports all enums
│   ├── media_type.py       # MediaType
│   ├── variant.py          # VariantKind
│   ├── status.py           # ReleaseStatus, StreamMode
│   ├── entity.py           # EntityKind
│   ├── relation.py         # RelationRole, CreditSection
│   ├── membership.py       # MembershipStatus
│   └── genre.py            # String constants (not an enum)
│
├── models/                 # Pydantic v2 models — requires pydantic>=2
│   ├── __init__.py
│   ├── work.py             # Work, Release, Appearance
│   ├── entity.py           # Entity, EntityRef, Membership, Credit
│   ├── conflict.py         # Conflict (used by text.compare)
│   └── external_ids.py     # ExternalIds — typed wrapper over Dict[str, str] with well-known key constants
│
└── text/                   # stdlib only — zero dependencies
    ├── __init__.py
    ├── normalize.py        # Text normalisation and fuzzy matching
    ├── compare.py          # Work comparison and scoring
    └── iso.py              # ISO 639 / ISO 3166 helpers
```

### 3.1 Dependency rules

| Layer | Dependencies | Rationale |
|---|---|---|
| `taxonomy/` | none | Safe to import in any environment |
| `text/` | stdlib only (`re`, `unicodedata`, `difflib`, `hashlib`) | No framework lock-in |
| `models/` | `pydantic>=2` | Required, not optional — see §3.2 |

### 3.2 Why Pydantic is required, not optional

Maintaining parallel `dataclass` and Pydantic implementations of the same models doubles
maintenance burden and diverges over time. Every project complex enough to depend on
`mediavocab` already uses Pydantic. The "optional" path is never used in practice.

Consumers that genuinely cannot afford Pydantic (microcontrollers, minimal CLIs) import
only from `taxonomy/` and `text/`, which have zero dependencies. The models layer is a
separate concern.

---

## 4. Taxonomy

### 4.1 `MediaType`

**Purpose:** Determines the metadata schema, which external databases to query, and which
comparison tolerances apply. Two items with the same `MediaType` should be comparable
using a common field set.

**Inclusion criterion:** The candidate type requires a different set of mandatory fields,
is catalogued in different external databases, or requires different runtime/year comparison
tolerances from every existing type.

```python
class MediaType(str, Enum):
    MOVIE            = "movie"
    EPISODIC_SERIES  = "episodic_series"  # on-demand ordered episodes (anime, drama, sitcom)
    TV               = "tv"               # live linear / IPTV broadcast channel
    MUSIC            = "music"
    MUSIC_VIDEO = "music_video"
    PODCAST     = "podcast"
    AUDIOBOOK   = "audiobook"
    AUDIO_DRAMA = "audio_drama"
    RADIO       = "radio"
    BOOK        = "book"
    COMIC       = "comic"
    GAME                = "game"
    INTERACTIVE_FICTION = "interactive_fiction"
    SOUND_EFFECT        = "sound_effect"
    AMBIENT_SOUNDS      = "ambient_sounds"
    PLAYLIST            = "playlist"            # cross-media-type curated collection
    GENERIC             = "generic"
    NOT_MEDIA           = "not_media"
```

#### Value definitions

**`MOVIE`**  
Feature films and short films. Schema: title, director, cast, runtime, theatrical release
date, IMDB/TMDB IDs, production country. Runtime distinguishes short (≤ 40 min) from
feature — no separate type is needed. Documentaries, silent films, animated films, and
adult films are all MOVIE with an appropriate `content_genres` tag.

**`EPISODIC_SERIES`**  
On-demand episodic video — anime, drama, sitcoms, web series, streaming originals.
Anything with ordered episodes you can pause, resume, and binge. Schema: series title,
season, episode number, network, first air date, TVmaze/TVDB IDs. The `season` and
`episode` fields on `Work` handle the episode↔series distinction — a series record
has `season = None`, an episode record has both set.

**`TV`**  
Live linear / IPTV broadcast channels. Parallel to `RADIO`: the *channel* is the Work,
identified by the broadcaster, not by individual programmes airing on it. You cannot skip
ahead — schedule is publisher-controlled, content is continuous, and the same channel
yields a long stream of programmes over time. Use `EPISODIC_SERIES` for the on-demand
ordered-episodes case (anime, drama, etc.); a TV channel that *also* publishes recordings
of its programmes on-demand creates separate `EPISODIC_SERIES` Works for those.
TV channels/networks-as-organisations are tracked as `Entity` with
`EntityKind.ORGANISATION`.

**`MUSIC`**  
Audio recording distributed through music pipelines. Schema: artist, album, track number,
ISRC, duration, MusicBrainz recording ID, label. Runtime tolerance: ±3 seconds.

The criterion is **distribution schema**, not audio content. A rap track, a spoken word
poetry album, and an ASMR ambient recording are all MUSIC if they carry an ISRC, appear
in music databases (MusicBrainz, Discogs, Spotify), and are distributed through music
labels or aggregators. The presence or absence of melody is irrelevant to the type.
`content_genres` handles the aesthetic distinction (hip_hop, spoken_word, asmr, poetry).

The same audio content distributed as a podcast episode is `PODCAST` — the distribution
channel determines the type, not the content. An ASMR creator who releases on both
Spotify (as MUSIC) and their RSS feed (as PODCAST) produces two separate Releases of
the same underlying Work.

**`MUSIC_VIDEO`**  
Promotional or performance video for a musical work. Distinct from MUSIC because it has
a director field, different providers (Vevo, YouTube Music), and a runtime tolerance of
±30 seconds (live performance versions vary widely). A full concert film released
theatrically is `MOVIE` with `content_genres = [GENRE_CONCERT]`.

**`PODCAST`**  
Episodic non-music audio content distributed via RSS or a podcast platform. Schema: host,
show title, episode GUID, RSS feed URL, Podcast Index / Apple Podcasts IDs. Radio
programmes repackaged as ordered episodes belong here. Series / episode encoding
follows the convention in §5.5.

**`AUDIOBOOK`**  
Complete narrated literary work read by a single narrator. Schema: author, narrator,
chapter count, ISBN-derived IDs, Audible/LibriVox IDs. Distinct from PODCAST (a complete
work, not episodic), from BOOK (the primary artifact is audio, not text), and from
AUDIO_DRAMA (single narrator, no cast, no director). An author reading excerpts as a
promotional podcast is PODCAST.

**`AUDIO_DRAMA`**  
Fully performed audio production with a cast, director, and sound design. Schema: cast
(multiple actors), director, sound designer, screenwriter, production company IDs
(Big Finish, BBC Sounds, Audible Originals). Distinct from AUDIOBOOK by credit structure:
an audiobook has one narrator reading prose; an audio drama has a cast performing a
script. Admission criterion (axiom 9): the credit schema is fundamentally different —
a director and a cast list are required fields that do not exist on AUDIOBOOK.
Original audio dramas and dramatised adaptations of existing works both use this type.

**`RADIO`**  
Live linear audio broadcasting — stations and channels. A station is a `Work`
with `episode = None` and `runtime = None`; its stream URLs (mirrors, bitrates,
DAB vs web) are multiple `Release`s of the same Work. Cross-referencing across
providers uses `external_ids` exactly as for films.

`RADIO` is the audio-only counterpart to `TV`: both model live linear broadcast
channels where the *channel* is the Work. They are distinct MediaTypes (axiom 1)
because the schemas diverge — different external databases (radio-station
directories and RDS PI codes for `RADIO`; IPTV M3U / EPG sources and DVB
identifiers for `TV`), different Release shapes (audio codec/bitrate vs.
video codec/resolution), and different downstream tooling.

Individual radio programmes that are republished as ordered episodes (a series
podcast feed of past broadcasts) are modelled as `PODCAST` works; a fully
performed radio play is `AUDIO_DRAMA + GENRE_RADIO_DRAMA`. The `RADIO` type
covers the live broadcast service itself, not its archived programme catalogue.

**`BOOK`**  
Text-based written work: prose fiction, non-fiction, poetry collections, essays, short
story anthologies. Schema: ISBN, author, publisher, page count, edition, OpenLibrary /
Goodreads IDs. An ebook is a Release with `source_format = "EPUB"` or `"PDF"`.
Comic books and graphic novels are COMIC, not BOOK.

A single poem or short story is an `Appearance` within its collection Work, exactly as
a track is within an album — it is not a standalone BOOK Work unless published
independently. Spoken word recordings of written works are `AUDIOBOOK` (narrated prose)
or `MUSIC` (performed/recorded poetry with its own release identity).

**`COMIC`**  
Sequential art works: single issues, graphic novels, manga volumes, manhwa, manhua,
webcomics, and comic strips. Schema: issue/chapter number, story arc, variant cover
flag, publisher series, ComicVine / GCD / MangaDex IDs. Distinct from BOOK because
the metadata schema is structurally different (issue number, story arc, cover variant)
and the primary databases are different.

The `episode` field carries the issue / chapter number; `season` carries the
volume number where applicable; `series_title` carries the series / run title.
A standalone graphic novel with no issue structure has `episode = None`. Series
/ episode encoding otherwise follows the convention in §5.5.

A trade paperback collecting multiple issues is a `Work` with `VariantKind.COMPILATION`
and a `tracklist` of `Appearance` entries (one per collected issue). If it contains
original material (new introduction, bonus story) it earns its own Work identity;
a straight reprint is a Release with `variant_kind = COMPILATION`.

Cultural sub-types (manga, manhwa, manhua) use `content_genres` tags — they share the
same schema and databases only differ in supplementary coverage, not primary identity.
A narrated or animated presentation of a comic is a separate Work — see §8.6.

**`GAME`**  
Interactive software. The type exists so resolvers can route the verb "play"
(shared across every other media type) to the right pipeline — a query "play
Hades" disambiguates to the game, not to a song or film. Schema: platform,
developer, publisher, IGDB / RAWG IDs. Passive viewing of game footage (Let's
Plays, esports broadcasts) is `MOVIE`, `EPISODIC_SERIES`, or `PODCAST`
depending on distribution.

**`INTERACTIVE_FICTION`**  
Text- or voice-driven branching narrative software: parser-based adventures (Infocom,
Inform 7), choice-based fiction (Twine, ChoiceScript), voice-game skills (Alexa Skills,
Google Actions for narrative apps). Distinct from `GAME` because the schema differs:
no platform binary or graphics pipeline, author rather than developer studio, distinct
external database (IFDB.org — Interactive Fiction Database), source format is a story
file (`.z5`, `.gblorb`, `.html`, `.json`) or a voice-platform skill ID rather than a
console / Steam build. Schema: author, parser/engine, source format, IFDB ID,
ifiction.org ID, voice-skill ID. Runtime is undefined — sessions are user-paced and
branching, like a book. Use `GENRE_BRANCHING` for branching narratives, `GENRE_VOICE_GAME`
for voice-driven IF.

The criterion (axiom 1) is the database split: `GAME` records belong on IGDB / MobyGames /
Steam; `INTERACTIVE_FICTION` records belong on IFDB.org and ifiction.org. A graphic
adventure with a parser (Sierra-era titles) is `GAME` — it ships as a platform binary;
a voice-only narrative skill on Alexa is `INTERACTIVE_FICTION` — it has no binary at all.

**`SOUND_EFFECT`**  
A discrete, catalogued audio clip whose primary identity is a *category taxonomy* rather
than an artist or album. Schema: category hierarchy (`content_genres` carrying taxonomy
tags such as `sfx_animal`, `sfx_nature`, `sfx_mechanical`), runtime (precise, 0 s
tolerance), source library IDs. No artist, no ISRC, no album context. Catalogued in
dedicated sound libraries — freesound.org, BBC Sound Effects, ZapSplash, Soundsnap,
ZapSounds. Runtime tolerance: 0.0 s (clips are exactly what they are).

Admission criterion (axiom 1): the mandatory schema diverges from all existing types.
`MUSIC` requires artist/ISRC/music-database identity; `SOUND_EFFECT` requires none of
these and uses a different set of external databases. The "artist" concept is absent or
meaningless (a freesound.org uploader is not an artist in the music-pipeline sense).

Covers: animal sounds, nature field recordings distributed as individual clips (distinct
from `MUSIC` ambient albums), mechanical/industrial sounds, UI and game sound assets,
foley clips, and any short triggered audio whose catalogue identity is its category, not
its creator. Ambient soundscapes and rain recordings *distributed as music albums* (with
ISRC, on Spotify) are still `MUSIC` with `content_genres = [GENRE_SOUNDSCAPE]` — the
distribution schema determines the type (axiom 10).

A voice assistant request for "what sound does a dog make" resolves to a `SOUND_EFFECT`
Work. A request for "play a rain soundscape" may resolve to either `MUSIC` (a Spotify
album) or `SOUND_EFFECT` (a single clip from a sound library) depending on available
sources — the consuming player chooses.

**`AMBIENT_SOUNDS`**  
Background audio that is procedurally generated, algorithmically mixed, or composed as
a looping environmental texture — not a discrete recorded work. The defining
characteristic is the absence of a recording identity: no ISRC, no MusicBrainz entry,
no artist in the music-pipeline sense. The cataloguing axis is environment category and
generative parameters, not creator/release. Its "work" is a scene preset or environment
mix catalogued in a dedicated platform database (myNoise scene IDs, Moodist preset IDs,
Noisli mix IDs, Endel scene IDs).

Admission criterion (axiom 1): `MUSIC` requires artist/ISRC/music-database identity;
`SOUND_EFFECT` is a one-shot triggered clip. `AMBIENT_SOUNDS` has neither — these are
three genuinely different schemas with different external databases.

Covers: procedurally generated soundscapes (rain, café noise, forest), algorithmically
blended environments (myNoise, Moodist, Noisli, Endel), and looping field-recording
presets distributed through dedicated ambient audio platforms. Runtime is undefined or
user-controlled (the generator runs until stopped). Runtime tolerance: 0.0.

Note: continuous/looping playback is `StreamMode.CONTINUOUS` on the Release — a
playback concern, not an identity concern (axiom 4). A Brian Eno album played on loop
is still `MUSIC + GENRE_AMBIENT`; its ISRC and MusicBrainz identity do not change based
on how a player chooses to loop it. `AMBIENT_SOUNDS` is for content that has no
recording identity and could never have an ISRC regardless of playback mode.

#### Classifier: MUSIC vs SOUND_EFFECT vs AMBIENT_SOUNDS

When a recording could plausibly fit more than one of these three types, apply
this decision tree in order — first match wins:

1. The asset has an ISRC (or a MusicBrainz/Discogs ID) → **`MUSIC`**.
2. The asset is a discrete, finite recording (≤ 15 min) catalogued in a
   sound-effect library (Freesound, BBC Sound Effects, Soundsnap, ZapSplash) →
   **`SOUND_EFFECT`**.
3. The asset is procedurally generated, parameterised, or has user-controlled
   duration (myNoise, Moodist, Noisli, Endel) → **`AMBIENT_SOUNDS`**.
4. None of the above apply but the asset is short (≤ 60 s) and
   category-tagged → **`SOUND_EFFECT`** (lowest schema complexity wins ties).

**`PLAYLIST`**  
A user-curated cross-media-type collection: Spotify playlists, YouTube playlists,
M3U files, OPML podcast bundles. The constituent Works keep their own MediaType.
Schema: `tracklist` of `Appearance`s, `Credit` for the curator with `relation_role =
RelationRole.CURATOR`, distinct external databases (Spotify Playlist API,
YouTube Playlist API).

Identity is anchored at the **source** — the `external_ids` entry that points
at the upstream playlist record (e.g. `spotify_playlist_id`, `youtube_playlist_id`).
The same playlist may be reordered, have tracks added, or have tracks removed
without becoming a different Work; the source-side ID is stable across those
edits. This is consistent with §10.1: `tracklist` is in the *mutable* set;
the playlist's identity is its `external_ids` + `title` + `media_type`, not
its membership.

A single-media-type *published* compilation (a mixtape, a "best of" album)
stays at the underlying media type with `variant_kind = COMPILATION` — the
schema is the same as a regular release.

A standalone playlist with no upstream source (a hand-curated `.m3u`)
inherits its identity from the file path / URI; consumers that need
content-based dedup should hash `(title, [appearance.work.external_ids
for appearance in tracklist])` themselves — that hash is non-normative
and not part of `work_hash`.

See `docs/patterns/playlists-and-channels.md`.

**`GENERIC`**  
Unknown or unclassified content. Match confidence is penalised when `media_type` is
GENERIC. This is a valid operational state, not a permanent classification.

**`NOT_MEDIA`**  
This query or item has been positively identified as not a media playback request.
Used as a terminal classifier output to route non-media intents away from media handlers
before any Work resolution is attempted.

Examples: factual questions ("when is a director's birthday"), smart home commands not
involving media ("turn off the lights"), calendar events, reminders, entity information
queries ("who starred in X").

Distinction from `GENERIC`: `GENERIC` means "this IS a media item but its type is
unknown — resolution may clarify it." `NOT_MEDIA` means "this is definitively not a
media item — no Work exists to resolve." `NOT_MEDIA` is a terminal state; `GENERIC` is
a transient one. Match confidence is always 0.0 when `media_type` is `NOT_MEDIA`.

#### Excluded values — with justification

| Rejected value | Reason |
|---|---|
| `DOCUMENTARY` | Genre, not type. Same schema as MOVIE/TV. Use `content_genres`. |
| `ANIME` | Cultural/geographic category of animation. Same schema as TV/MOVIE. Use `content_genres`. |
| `CARTOON` | Production technique. Same schema as TV/MOVIE. Use `content_genres`. |
| `SHORT_FILM` | MOVIE with runtime ≤ 40 min. Use `content_genres = [GENRE_SHORT_FILM]` for explicit tagging. |
| `NEWS` | Genre. Distributed as TV, RADIO, or PODCAST depending on format. |
| `AUDIO` | Describes signal type, not content. Too coarse. |
| `VIDEO` | Same — describes signal type, not content. |
| `LIVESTREAM` | Delivery mechanism, not identity. A live stream is a Release with a streaming URI. The content is still RADIO, TV, MUSIC, etc. |
| `ADULT` | Content rating, orthogonal to type. Use a `content_rating` field. |
| `HENTAI` | Compound of anime (genre) + adult (rating). Two tags, not a type. |
| `ASMR` | Genre tag. Content is MUSIC or PODCAST by format. |
| `TRAILER` | Supplementary promotional material, not a primary work. |
| `BEHIND_THE_SCENES` | Supplementary material. Use a `content_genres` or `is_supplementary` flag. |
| `AUDIO_DESCRIPTION` | Accessibility track on existing content, not a standalone work type. |
| `VISUAL_STORY` | Platform-specific ephemeral format. Not stable enough for a foundation vocabulary. |
| `SILENT_MOVIE` | MOVIE + `audio_present = False`. No schema difference. `color = False` if also monochrome. |
| `BLACK_WHITE_MOVIE` | MOVIE + `color = False` on `Work`. Technical attribute, not a type or genre. |
| `RADIO_THEATRE` | Radio drama. Now covered by `AUDIO_DRAMA` + `content_genres = [GENRE_RADIO_DRAMA]`. |

---

### 4.2 `VariantKind`

**Purpose:** Records why a specific edition differs from the canonical work. Two items
with conflicting `VariantKind` values are distinct works, not duplicates. A missing
`variant_kind` (None) means the canonical/default edition — no value is needed to
represent "standard".

**Inclusion criterion:** The variant changes something detectable in metadata (runtime,
credits, track listing, visual treatment) AND is catalogued as a distinct entry in at
least one major database OR is produced by a recognised editorial/restoration process.

```python
class VariantKind(str, Enum):
    # Film cuts — changes to content by the original creators
    THEATRICAL   = "theatrical"
    DIRECTORS    = "directors"
    EXTENDED     = "extended"

    # Fan-created reworks
    FANEDIT      = "fanedit"      # catch-all; downstream packages may sub-classify
    TV_TO_MOVIE  = "tv_to_movie"  # multi-episode TV condensed into a film
    MOVIE_TO_TV  = "movie_to_tv"  # film re-cut into episodic form

    # Restoration and technical enhancement
    PRESERVATION = "preservation" # reconstruction of lost/degraded material
    COLORIZED    = "colorized"    # B&W original given colour treatment
    REMASTERED   = "remastered"   # improved A/V quality from original elements
    UPSCALED     = "upscaled"     # AI/manual resolution enhancement (no new elements)

    # Release packaging — music and home video
    DELUXE       = "deluxe"       # expanded with bonus tracks/discs
    REISSUE      = "reissue"      # later release, possibly altered track listing
    COMPILATION  = "compilation"  # aggregation from multiple sources
    REGIONAL     = "regional"     # geographically distinct edit (censorship, dubbing)
    BOOTLEG      = "bootleg"      # unofficial recording not sanctioned by rights holder:
                                  # audience recordings, unofficial live tapes, pirate
                                  # pressings of unreleased material. The Work identity
                                  # (artist, title, performance date) is real; the Release
                                  # is unauthorised. Bootlegs are always Releases, not Works.

    OTHER        = "other"        # known variant, type not classifiable above
```

#### Value notes

**`THEATRICAL`** — Explicit marker for the theatrical cut when a director's cut also exists
in the same library. Without a counterpart, `variant_kind = None` is preferred.

**`FANEDIT`** — Foundation-level catch-all. Downstream packages may sub-classify into
narrower kinds (e.g. FANFIX, FANMIX, FANEDIT_SHORT). These sub-types do not belong in
the foundation because they are specific to a single fanedit database.

**`TV_TO_MOVIE` / `MOVIE_TO_TV`** — Structural transformations that change the work's
narrative structure and cross the `MediaType` boundary. By axiom 12 ("one Work, one
MediaType"), the result is a **new Work**, not an edition of the source. The
`variant_kind` value tags *what kind* of derivative this Work is; the link back to
the source Work is recorded as `WorkRelation(kind=FANEDIT_OF, target=source)` (or
`ADAPTED_FROM` for non-fanedit transformations).

The same applies to `FANEDIT` when the recut materially restructures narrative —
Fanedit databases catalogue such fanedits as standalone entries with their
own external IDs. A minor recut that changes nothing structural (a shorter
opening credit, a colour-grade pass) may stay as a `Release.variant_kind=FANEDIT`
of the original Work.

**`PRESERVATION`** — Distinct from REMASTERED: a preservation reconstructs content from
degraded or partially lost source material, sometimes resulting in an incomplete work.
A remaster improves quality without reconstruction.

**`UPSCALED`** — Distinct from REMASTERED: no new source elements are used; the process
is purely computational. Relevant for libraries that track source quality provenance.

**`COMPILATION`** — Changes the work's structure fundamentally: it is a derived work
aggregating content from multiple other works, not a variant of a single work.

**`BOOTLEG`** — The performance or recording IS real (an audience tape of a 1975 concert,
an unreleased studio session that leaked). The Work is the performance; the Release is
the bootleg pressing or tape. `BOOTLEG` lives on the Release, not the Work, because
the same performance may exist as both an official release and a bootleg. A consumer
may choose to include or exclude bootleg Releases from their library; the canonical
Work is unaffected. Databases: Live Music Archive, Dime-a-Dozen, Wolfgang's Vault.

#### Excluded values — with justification

| Rejected value | Reason |
|---|---|
| `STANDARD` | Absence of a variant. `variant_kind = None` is the canonical edition. |
| `ORIGINAL` | Same as STANDARD. Redundant. |
| `FANFIX` | IFDB-specific sub-type of FANEDIT. Too narrow for foundation. |
| `FANMIX` | Same. |
| `FANEDIT_SHORT` | Same. |
| `BONUS_TRACKS` | A property of DELUXE or REISSUE, not a standalone variant. |

---

### 4.3 `EntityKind`

**Purpose:** Classifies the *structural type* of an entity — what schema it needs —
not its professional identity. A musician and a documentary director are both PERSON;
what they do on specific works is captured by RelationRole credits.

```python
class EntityKind(str, Enum):
    # Human individual
    PERSON       = "person"        # any human being

    # Group with temporal membership (members join and leave over time)
    GROUP        = "group"         # band, ensemble, theatre company, comedy duo, etc.

    # Legal / business entity (no individual members; has imprint relationships)
    ORGANISATION = "organisation"  # record label, publisher, film studio, game developer,
                                   # broadcaster, streaming service, production company

    # Container that is not itself a Work
    SERIES       = "series"        # TV franchise, book series, game series, podcast show

    DEVICE       = "device"        # physical playback endpoint: smart speaker, cast target,
                                   # smart plug connected to legacy hardware, set-top box,
                                   # media player (Kodi, Plex), game console as delivery device

    OTHER        = "other"
```

**Axiom:** If an EntityKind distinction does not change the model schema (fields,
validation, or query logic), it does not earn its own value. Professional identity
(`"this person is primarily an actor"`) belongs in `Entity.extra["primary_role"]`
or is inferable from their RelationRole credits — it is not a schema concern.

#### Why `GROUP` ≠ `PERSON`

A GROUP has a `memberships` list with temporal bounds (members join and leave over time).
A PERSON does not. Collapsing them makes lineup modelling impossible: you cannot store
"Cliff Burton was in Metallica from 1982 to 1986" without the GROUP/PERSON distinction.
A solo artist who forms a band is a PERSON entity that becomes a member of a GROUP entity.

#### Why `ORGANISATION` is one value, not LABEL / STUDIO / DEVELOPER / NETWORK

All of these are legal entities: name, country, founding year, external IDs, logo. None
has individual members or temporal membership. A consuming package that needs to
distinguish a record label from a film studio can use `Entity.extra["org_type"]` or
`Entity.part_of` — the schema is identical regardless.

#### Why `SERIES` is an EntityKind, not a `MediaType`

A series is a *container*, not a work. "The Dark Tower" book series contains seven Books.
"Doctor Who" is a TV series containing hundreds of TV episodes. The series itself has
metadata (title, author/creator, number of instalments) but is not a work you watch,
read, or listen to directly. Modelling it as an Entity allows `part_of` relations from
individual works to their containing series.

#### Why `DEVICE` is an EntityKind, not a `MediaType`

A smart plug connected to a radio, a Sonos speaker, a Chromecast, a Kodi box, or a game
console used as a playback endpoint are all addressed as delivery channels, not as media
works. The *content* being delivered (RADIO, MUSIC, MOVIE, GAME) is still a Work. The
device is how a consumer routes playback to a specific physical destination. Schema:
device name, category (audio/video/game), location/room, address (IP, device identifier)
in `external_ids`. A Home Assistant entity ID is a typical `external_ids` key. Device
identity is stable across sessions; routing logic (which URI to use for this device)
belongs to the consuming player, not to mediavocab.

---

### 4.4 `RelationRole`

**Purpose:** Describes how an entity participates in a specific work or release.
Distinct from `EntityKind` because the same entity can have different roles on different
works. A composer who also performs their own music has one Entity record and two
RelationRole values across different works.

```python
class RelationRole(str, Enum):
    CREATOR         = "creator"          # generic fallback; use a specific role when known

    # Music
    PERFORMER       = "performer"        # principal artist on a recording
    COMPOSER        = "composer"         # wrote the music
    LYRICIST        = "lyricist"         # wrote the lyrics
    PRODUCER        = "producer"         # music producer
    FEATURING       = "featuring"        # credited featured artist
    REMIXER         = "remixer"

    # Film and TV
    DIRECTOR        = "director"
    SCREENWRITER    = "screenwriter"
    ACTOR           = "actor"
    CINEMATOGRAPHER = "cinematographer"
    EDITOR          = "editor"           # film/video editor

    # Book and comic
    AUTHOR          = "author"
    ILLUSTRATOR     = "illustrator"
    TRANSLATOR      = "translator"
    NARRATOR        = "narrator"         # audiobook narrator

    # Podcast and radio
    HOST            = "host"
    GUEST           = "guest"
    CURATOR         = "curator"          # selected/ordered other people's works
                                         # (playlists, anthologies, compilation editors)

    # Game
    DEVELOPER       = "developer"        # studio or individual that created the game
    PORTER          = "porter"           # responsible for a platform port

    # Release infrastructure (applies across media types)
    PUBLISHER       = "publisher"        # book publisher or game publisher
    LABEL           = "label"            # record label
    DISTRIBUTOR     = "distributor"

    OTHER           = "other"
```

#### Note on PRODUCER

PRODUCER in this enum means *music producer* (the person who shapes the sound of a
recording: arrangement, mixing, studio direction). It does not mean *film producer*
(the person who finances and oversees film production). A film producer is modelled
as `RelationRole.CREATOR` with a `role` note of "Executive Producer" or "Line Producer"
until a dedicated value is added. This distinction is intentional: film producer credits
are rarely useful for metadata disambiguation, while music producers are a core identity
signal.

---

### 4.5 `MembershipStatus`

**Purpose:** Records the current state of a time-sliced membership relationship.

**Critical invariant:** `date_to = None` does NOT mean "current". A defunct band's last
known member has `date_to = None` (the end date was not recorded) and
`status = INACTIVE` (the band is no longer active). Status and date range are orthogonal
and must both be stored. This lesson comes from real-world band-lineup datasets, where
bands with decades of history cannot be accurately represented without this distinction.

```python
class MembershipStatus(str, Enum):
    CURRENT   = "current"    # actively in the group now
    PAST      = "past"       # confirmed former member; date_to should be set
    TOURING   = "touring"    # touring/live member only; not on studio recordings.
                             # Renamed from LIVE to avoid collision with
                             # StreamMode.LIVE and WorkRelationKind.LIVE_VERSION.
    GUEST     = "guest"      # session or guest contributor; not a member
    INACTIVE  = "inactive"   # group is dormant or disbanded; last known status
```

#### Usage rules

- An entity with `status = CURRENT` and `date_to = None` IS an active member.
- An entity with `status = PAST` and `date_to = None` was a member but the departure
  date is unknown — do not infer they are current.
- An entity with `status = INACTIVE` means the group itself is inactive; the
  membership status at time of inactivity is preserved.
- An artist can have multiple `Membership` records for the same band if they left and
  rejoined (each stint is a separate record with its own date range and status).
- `TOURING` and `GUEST` members do not appear on the principal lineup of studio
  recordings; they appear in the `GUEST` section of release credits.

---

### 4.6 `CreditSection`

**Purpose:** Classifies which section of a release's credits an entity appears in.
Generalises across all media types: a film's cast/crew split, a book's author/editor/
publisher split, and a metal album's band-members/guests/staff split all use the same
three-way taxonomy.

```python
class CreditSection(str, Enum):
    PRINCIPAL = "principal"  # band members / main cast / core authors / primary creators
    GUEST     = "guest"      # featured artists / session musicians / cameos / guest authors
    STAFF     = "staff"      # production staff: producer, engineer, editor, cover artist,
                             # publisher, distributor — not creative contributors to the work itself
```

---

### 4.7 `ReleaseStatus`

**Purpose:** Lifecycle state of a work. Affects whether metadata resolution should be
attempted (no external database will have a record for a rumoured, unconfirmed work).

```python
class ReleaseStatus(str, Enum):
    RELEASED      = "released"
    ANNOUNCED     = "announced"       # confirmed; release date may be unknown
    IN_PRODUCTION = "in_production"   # filming, recording, or development underway
    CANCELLED     = "cancelled"       # confirmed as not releasing
    WITHDRAWN     = "withdrawn"       # was released, no longer commercially available
                                      # (out of print, removed from streaming, rights reverted).
                                      # Distinct from CANCELLED: the work shipped, then was
                                      # pulled. The Work is real; the named Release is gone.
    UNKNOWN       = "unknown"         # status cannot be determined
```

`RUMOURED` is excluded: a rumoured work has no verifiable record in any authoritative
database. If a work is only rumoured, it should not be catalogued as a Work at all.

---

### 4.8 `StreamMode`

**Purpose:** Describes how the content of a Release is delivered at playback time.
This is a property of the Release (the delivery), not of the Work (the content).

```python
class StreamMode(str, Enum):
    ON_DEMAND  = "on_demand"   # finite, seekable, available at any time (default)
    LIVE       = "live"        # real-time broadcast; may become ON_DEMAND after broadcast
    CONTINUOUS = "continuous"  # infinite or rolling; no defined end (live radio, IPTV)
```

A live concert stream starts as `LIVE` and may become `ON_DEMAND` when archived.
A radio station stream is always `CONTINUOUS`. A downloaded album track is `ON_DEMAND`.
The underlying Work does not change; only the Release's `stream_mode` changes.

---

### 4.9 `genre.py` — string constants, not an enum

Genre is inherently extensible, culturally variable, and not universally agreed upon.
A closed enum would require constant additions and cultural negotiation. Instead,
`genre.py` defines canonical string spellings as module-level constants. Consuming
packages may use any string in the `content_genres` field; these constants ensure
consistent spelling when the genre is known.

```python
# Canonical genre constant spellings
# Film and TV
GENRE_DOCUMENTARY    = "documentary"
GENRE_ANIMATION      = "animation"      # animated production technique
GENRE_ANIME          = "anime"          # animation of Japanese cultural origin
GENRE_SHORT_FILM     = "short_film"     # runtime ≤ 40 min; use with MOVIE
GENRE_NOIR           = "noir"
GENRE_CONCERT        = "concert"        # filmed live music performance
GENRE_STAND_UP       = "stand_up_comedy"
GENRE_TALK_SHOW      = "talk_show"
GENRE_REALITY        = "reality"
GENRE_NEWS           = "news"
GENRE_SPORTS         = "sports"
GENRE_BEHIND_SCENES  = "behind_the_scenes"
GENRE_TRAILER        = "trailer"        # promotional preview; not a primary work

# Audio
GENRE_RADIO_DRAMA    = "radio_drama"    # use with AUDIO_DRAMA; historically radio-native
GENRE_ASMR           = "asmr"
GENRE_AMBIENT        = "ambient"        # sustained, atmospheric audio; no narrative
GENRE_SOUNDSCAPE     = "soundscape"     # field recordings, natural environments
GENRE_NATURE_SOUNDS  = "nature_sounds"  # rain, ocean, birdsong — subset of soundscape
GENRE_WHITE_NOISE    = "white_noise"    # noise-spectrum sleep/focus audio

# Sound effect taxonomy (use with SOUND_EFFECT)
GENRE_SFX_ANIMAL     = "sfx_animal"     # animal vocalisations
GENRE_SFX_NATURE     = "sfx_nature"     # weather, water, wind, natural environment
GENRE_SFX_MECHANICAL = "sfx_mechanical" # machines, vehicles, tools
GENRE_SFX_HUMAN      = "sfx_human"      # footsteps, crowds, body sounds
GENRE_SFX_UI         = "sfx_ui"         # interface, notification, game UI sounds
GENRE_SFX_FOLEY      = "sfx_foley"      # production foley assets

# Comics
GENRE_MANGA          = "manga"          # Japanese sequential art (COMIC + Japanese origin)
GENRE_MANHWA         = "manhwa"         # Korean sequential art
GENRE_MANHUA         = "manhua"         # Chinese sequential art
GENRE_WEBCOMIC       = "webcomic"       # originally published online, often no print run
GENRE_MOTION_COMIC   = "motion_comic"   # video adaptation of comic panels; MediaType is MOVIE or TV, not COMIC

# Written/spoken word
GENRE_POETRY         = "poetry"         # BOOK (collection) or MUSIC/PODCAST (recorded)
GENRE_SPOKEN_WORD    = "spoken_word"    # performed speech released through music pipelines
GENRE_ESSAY          = "essay"
GENRE_SHORT_STORY    = "short_story"    # usually an Appearance within a BOOK collection
GENRE_HIP_HOP        = "hip_hop"        # rhythmic speech over beats; MediaType is still MUSIC
GENRE_EDUCATIONAL    = "educational"    # lecture, course, tutorial; any MediaType

# Photo / image collections (use with BOOK)
GENRE_PHOTO_BOOK     = "photo_book"     # photo collection; user-paced viewing
GENRE_SLIDESHOW      = "slideshow"      # ordered image sequence; user- or timer-paced

# Interactive fiction (use with INTERACTIVE_FICTION)
GENRE_PARSER_IF      = "parser_if"      # parser-based, e.g. Inform / Infocom
GENRE_CHOICE_IF      = "choice_if"      # choice-based, e.g. Twine / ChoiceScript
GENRE_VOICE_GAME     = "voice_game"     # voice-driven IF (Alexa Skill, Google Action)
GENRE_BRANCHING      = "branching"      # branching narrative; applies across IF/BOOK/GAME

# Canonical narrative genres (apply to MOVIE / TV / BOOK / COMIC / GAME / IF)
GENRE_HORROR         = "horror"
GENRE_COMEDY         = "comedy"
GENRE_DRAMA          = "drama"
GENRE_THRILLER       = "thriller"
GENRE_SCI_FI         = "sci_fi"
GENRE_FANTASY        = "fantasy"
GENRE_ROMANCE        = "romance"
GENRE_WESTERN        = "western"
GENRE_MYSTERY        = "mystery"
GENRE_ACTION         = "action"
GENRE_ADVENTURE      = "adventure"
GENRE_CRIME          = "crime"
GENRE_WAR            = "war"
GENRE_HISTORICAL     = "historical"
GENRE_BIOGRAPHY      = "biography"
GENRE_MUSICAL        = "musical"        # film/stage with sung musical numbers as primary form
GENRE_FAMILY         = "family"         # broad-appeal child + adult; not strictly children's

# Canonical music genres
GENRE_ROCK           = "rock"
GENRE_POP            = "pop"
GENRE_JAZZ           = "jazz"
GENRE_CLASSICAL      = "classical"
GENRE_ELECTRONIC     = "electronic"
GENRE_METAL          = "metal"
GENRE_PUNK           = "punk"
GENRE_FOLK           = "folk"
GENRE_BLUES          = "blues"
GENRE_COUNTRY        = "country"
GENRE_INDIE          = "indie"
GENRE_REGGAE         = "reggae"
GENRE_LATIN          = "latin"
GENRE_RNB            = "rnb"
GENRE_SOUL           = "soul"
GENRE_FUNK           = "funk"
GENRE_DISCO          = "disco"
GENRE_HOUSE          = "house"
GENRE_TECHNO         = "techno"
GENRE_TRANCE         = "trance"
GENRE_DUBSTEP        = "dubstep"
GENRE_DRUM_AND_BASS  = "drum_and_bass"

# Cross-type
GENRE_ADULT          = "adult"          # explicit sexual content; applies to any MediaType
GENRE_AI_GENERATED   = "ai_generated"   # primary creative content produced by an AI system
```

### 4.10 `PlaybackModality` — the playback-intent axis

Orthogonal to `MediaType` (axiom 13). A request verb collapses cleanly onto a modality at
the consumer side: *"play X"* ⇒ AUDIO; *"watch X"* / *"show me X"* ⇒ VIDEO; *"open X"* /
*"read X"* ⇒ TEXT or INTERACTIVE depending on context. The resolver gates providers on
the modality the caller hints at, so a `Signals(medium=GENERIC, modality=AUDIO)` never
touches TVmaze or pyfanedit.

```python
class PlaybackModality(str, Enum):
    AUDIO       = "audio"
    VIDEO       = "video"
    INTERACTIVE = "interactive"   # game, interactive fiction
    TEXT        = "text"          # book, comic, ebook
    UNKNOWN     = "unknown"        # GENERIC / PLAYLIST / NOT_MEDIA / no hint
```

**Default `MediaType → PlaybackModality` mapping** (`mediavocab.taxonomy.modality.MEDIA_TYPE_TO_MODALITY`):

| Modality | MediaTypes |
|---|---|
| `AUDIO` | `MUSIC`, `PODCAST`, `AUDIOBOOK`, `AUDIO_DRAMA`, `RADIO`, `SOUND_EFFECT`, `AMBIENT_SOUNDS` |
| `VIDEO` | `MOVIE`, `EPISODIC_SERIES`, `TV`, `MUSIC_VIDEO` |
| `TEXT` | `BOOK`, `COMIC` |
| `INTERACTIVE` | `GAME`, `INTERACTIVE_FICTION` |
| `UNKNOWN` | `PLAYLIST`, `GENERIC`, `NOT_MEDIA` |

`PLAYLIST` is `UNKNOWN` because membership decides the modality — the consumer infers
from the first track. `NOT_MEDIA` is `UNKNOWN` because it is by definition not playback.
`GENERIC` is `UNKNOWN` and the modality hint on `Signals` is exactly the field that
disambiguates it for routing — *"play this thing"* (AUDIO) versus *"show me this thing"*
(VIDEO) on the same MediaType.

**Routing rule** (`MetadataProvider.matches`, axiom 13):

```
(no `media`    declared OR signals.medium   in self.media)
AND
(no `modality` declared OR signals.modality in self.modality)
AND
(no `genre_filter` declared OR self.genre_filter ∩ signals.content_genres)
```

Each axis short-circuits independently. A provider declares
`modality = {PlaybackModality.AUDIO}` to opt out of video routing without claiming any
particular `MediaType`.

**No `DEVICE` modality.** Per axiom 4, devices are `Entity(EntityKind.DEVICE)`;
*"turn on the kitchen light"* is `MediaType.NOT_MEDIA`. `PlaybackModality` is for
media-playback intent only.

**No field on `Work` or `Release`.** Modality is a routing concern, not identity (axiom 13).
A `Work` whose modality consumers want to know is a `Work` whose `MediaType` already
carries that information through `infer_modality(work.media_type)`. Persisting an
explicit modality on `Work` would invite drift between two sources of truth.

---

## 5. Models

### 5.1 `EntityRef`

A lightweight reference to an entity used inside `Work`, `Credit`, `Membership`, and
`Appearance` models. Not a full entity record — it is a pointer to be resolved by the
consumer against their entity store.

```python
class EntityRef(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    kind: EntityKind
    external_ids: Dict[str, str] = {}   # e.g. {"musicbrainz_artist": "...", "imdb_person": "..."}
```

---

### 5.2 `Membership`

A time-sliced membership of an entity in a group. One artist who leaves and rejoins a
band has two Membership records: one with `status = PAST` and a date range, one with
`status = CURRENT` and an open end.

```python
class Membership(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: EntityRef
    roles: List[str]                      # ["vocals", "guitar"] — lowercase instrument or function strings
    status: MembershipStatus
    date_from: Optional[str] = None       # year ("1986") or ISO date ("1986-03-01")
    date_to: Optional[str] = None         # None does NOT mean current; check status
    note: Optional[str] = None            # free text; "left due to creative differences"
```

**`roles` strings:** Use lowercase, canonical instrument/function names where possible
(e.g. `"vocals"`, `"lead guitar"`, `"bass"`, `"drums"`, `"keyboards"`). These are
free-text — no closed enum — because instrument names are too numerous and culturally varied.
Consumer packages may define their own canonical lists; mediavocab imposes no validation.

---

### 5.3 `Credit`

An entity's contribution to a specific Work. Captures who played/wrote/produced/
engineered on a particular work, not who is generally associated with a band or project.

```python
class Credit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: EntityRef
    role: str                             # free text from source: "Electric Guitar", "Mix Engineer"
    relation_role: RelationRole           # typed role for programmatic routing
    section: CreditSection = CreditSection.PRINCIPAL
    note: Optional[str] = None            # "(tracks 1–4 only)", "(R.I.P. 1998)"
```

**Credit list order is the editorial credit order.** Poster billing, liner notes,
opening titles — `Work.credits[0]` is "billed first." Consumers that merge credits
from multiple providers should preserve first-seen order.

**`role` vs `relation_role`:** `role` preserves the raw credit string from the
source (e.g. "Bass Guitar", "Score Composer", "Cover Artwork") for display. `relation_role`
maps it to the closed `RelationRole` enum so consumer code can route without string-matching.
When the raw role is not available (programmatically constructed credits), set `role` to
`relation_role.value`.

---

### 5.4 `Appearance`

The position of a canonical Work within a Release container (album, anthology, playlist,
split release). Handles track reuse across releases, title overrides in reissues, bonus
track marking, and per-track band attribution in split releases.

```python
class Appearance(BaseModel):
    model_config = ConfigDict(extra="ignore")

    work: "Work"                           # canonical song, chapter, episode
    position: int                          # track/chapter/episode number within container
    disc: int = 1                          # disc number for multi-disc releases
    offset: Optional[float] = None         # seconds into the parent Release where this
                                           # member starts. Used by continuous mixes
                                           # (DJ sets, megamixes, live concerts) where
                                           # `position` alone is insufficient. None = the
                                           # parent uses simple ordering and members do not
                                           # occupy a fixed offset.
    title_override: Optional[str] = None   # if re-titled on this release
    length_override: Optional[float] = None # seconds; None = use work.runtime
    is_bonus: bool = False
    attributed_to: Optional[EntityRef] = None  # split releases: which band owns this track
```

#### Appearance and split releases

A split release (two or more bands sharing a single release, common in punk and metal)
is modelled as a Release whose `tracklist` contains Appearance records where each
Appearance has `attributed_to` pointing to the relevant band EntityRef. The Release
itself has multiple entries in `credits` (one PERFORMER credit per band).

**`attributed_to` rule:** On a split release, every Appearance **must** set
`attributed_to`; leaving it `None` is ambiguous and will cause incorrect band-track
associations at query time. On non-split releases it remains `None`.

---

### 5.5 `Work`

The abstract canonical creative work. Does not contain playback URIs or release-specific
metadata — those live in Release. Two records describing the same song on two different
albums share a Work; they differ only in their Release and Appearance.

```python
class Work(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    media_type: MediaType = MediaType.GENERIC

    # Temporal and geographic provenance
    year: Optional[int] = None             # original release/broadcast year of this specific Work.
                                           # For an EPISODIC_SERIES *episode*: episode air year
                                           # (not series debut year). For a remaster: original
                                           # release year (the remaster's date is on Release).
    runtime: Optional[float] = None        # seconds. `None` is overloaded — unknown vs.
                                           # indeterminate (user-paced / open-ended). Mediavocab
                                           # does not distinguish; consumers needing the difference
                                           # check `Release.stream_mode == CONTINUOUS` or use
                                           # media_type heuristics (BOOK / COMIC /
                                           # INTERACTIVE_FICTION / TV / RADIO → indeterminate).
    language: str = ""                     # ISO 639-1 or 639-2. `""` = unknown OR not applicable
                                           # (instrumental music, non-verbal film). Consumers
                                           # needing the distinction set `extra["language_na"] = True`.
                                           # Not validated at model level (use text.iso).
    original_languages: List[str] = []     # multi-language originals (Quebec film FR+EN,
                                           # simulcast anime JP+EN, bilingual hip-hop tracks).
                                           # `language` remains the primary; `original_languages`
                                           # carries the full list when the work was authored in
                                           # several at once. Empty list = single-language Work.
    country: str = ""                      # ISO 3166-1 alpha-2 — origin country. Same conflation
                                           # rule as language. Per-MediaType convention:
                                           #   MOVIE / EPISODIC_SERIES → production country
                                           #   MUSIC                  → label country (or artist
                                           #                            primary nationality if no label)
                                           #   RADIO / TV             → broadcaster headquarters
                                           #   BOOK                   → first-publication country
                                           #   GAME / IF              → developer country
                                           # International co-productions with no single origin: "".

    # Episode / series structure (TV, podcast, radio programmes)
    season: Optional[int] = None
    episode: Optional[int] = None          # default ordering — broadcast order for TV,
                                           # release order for film franchises
    series_title: Optional[str] = None     # containing series name, denormalised for convenience;
                                           # if a SERIES Entity exists, its name should match this
    episode_orderings: Dict[str, int] = {} # alternative orderings keyed by name:
                                           # {"production": 7, "broadcast": 5,
                                           #  "chronological": 12, "recommended": 3}.
                                           # Free string keys — common values are
                                           # "production", "broadcast", "chronological",
                                           # "recommended" (Star Wars Machete, anime release
                                           # vs production). `episode` mirrors the default ordering.

    # Edition
    variant_kind: Optional[VariantKind] = None
    edition: str = ""                      # free text: "Criterion Collection", "Deluxe Edition"
    source_format: str = ""                # original capture/broadcast format: "35mm", "DAB",
                                           # "Analogue tape". Use Release.source_format for
                                           # distribution format (Blu-ray, FLAC, EPUB).

    # Technical attributes — objective properties of the artefact (axiom 11)
    color: Optional[bool] = None           # True = colour, False = monochrome/B&W, None = unknown
    audio_present: Optional[bool] = None   # False = silent film; None = unknown/not applicable
    # Note: aspect_ratio and frame_rate are left to `extra` until a consumer requires them

    # Content classification — List[str] because works routinely belong to multiple genres
    # (anime + adult, documentary + sports, noir + comedy).  Use genre.py constants.
    content_genres: List[str] = []
    release_status: ReleaseStatus = ReleaseStatus.RELEASED

    # Discovery
    aka: List[str] = []                    # alternative titles, plain — typos, alternate
                                           # spellings, abbreviations. Not part of identity hash.
    localized_titles: List[Tuple[str, str]] = []
                                           # language-tagged titles for cross-locale matching:
                                           # [("Le Voyage dans la Lune", "fr"),
                                           #  ("A Trip to the Moon", "en")].
                                           # Used by language-aware fuzzy matchers; not part of
                                           # identity hash. Resolves Open Q5.

    # Credits — who contributed to THIS specific work
    credits: List[Credit] = []

    # Container / tracklist — for albums, anthologies, playlists
    tracklist: List[Appearance] = []

    # Cross-references
    external_ids: Dict[str, str] = {}      # {"imdb": "tt0078748", "musicbrainz_recording": "..."}
    extra: Dict[str, Any] = {}             # escape hatch for consumer-specific fields;
                                           # use sparingly — if two consumers need the same key,
                                           # it earns a real field. Suggested keys:
                                           # "primary_role" (EntityKind.PERSON sub-classification),
                                           # "org_type" (ORGANISATION sub-classification)
```

#### Series vs episode encoding

The `season` / `episode` / `series_title` fields are shared across every
episodic media type. The convention is uniform:

- A *series / show / channel / collection* Work has `episode = None`
  (and usually `season = None`).
- An individual *episode / chapter / issue / programme* Work has
  `episode` set, optionally with `season`. `series_title` carries the
  parent series' name, denormalised for convenience; if a `SERIES`
  Entity exists, its `name` should match.

Applies identically to `EPISODIC_SERIES`, `PODCAST`, `RADIO` programmes
republished as ordered episodes (modelled as `PODCAST`), `AUDIO_DRAMA`,
and `COMIC` (where `episode` carries issue/chapter and `season` carries
volume).

#### Work and channel-as-Work types

A `RADIO` station, a `TV` channel, and a `PODCAST` show all use the same
shape: `episode = None`, `runtime = None`, `external_ids` carrying the
provider IDs (radio-station directories, IPTV M3U sources, podcast
platform IDs). Stream URLs / RSS feeds are `Release`s of that Work.
Individual programmes are separate Works with `episode` set and either
`series_title` or a `Credit` to the parent station Entity via
`RelationRole.DISTRIBUTOR`.

---

### 5.6 `Release`

A specific physical or digital manifestation of a Work. One Work may have many Releases:
the original CD, a remaster, a streaming release, a regional variant, a fan recut.

```python
class Chapter(BaseModel):
    """A timestamped marker within a Release: audiobook chapter, podcast chapter
    marker, DVD scene break, "skip the intro" point. Chapters are NOT separate
    Works — a chapter is a navigation aid, not a creative work in its own right.
    """
    model_config = ConfigDict(extra="ignore")

    offset: float                          # seconds from start of the Release
    title: str = ""                        # "Chapter 1", "Skip Intro", "Final Battle"
    image: str = ""                        # optional thumbnail URL
    end: Optional[float] = None            # explicit end offset; None = until next chapter / end


class AccessibilityTrack(BaseModel):
    """A per-Release accessibility asset: subtitle/caption file, audio
    description track, sign-language insert, lyric/transcript file.
    Distinct from VariantKind — the underlying Work is unchanged; the
    Release simply ships an additional track or asset.
    """
    model_config = ConfigDict(extra="ignore")

    kind: str                              # "subtitles", "captions", "audio_description",
                                           # "sign_language", "transcript", "lyrics".
                                           # Free string — accessibility taxonomy is evolving.
    language: str = ""                     # ISO 639-1
    uri: str = ""
    forced: bool = False                   # subtitle "forced" flag (foreign-language inserts)
    sdh: bool = False                      # subtitles for deaf/hard-of-hearing
    note: Optional[str] = None


class Release(BaseModel):
    model_config = ConfigDict(extra="ignore")

    work: Work                             # the canonical work this release manifests

    # Edition
    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    region: str = ""                       # ISO 3166-1 alpha-2 — release market

    # Format — three orthogonal axes; replaces the old overloaded `source_format`
    container: str = ""                    # physical or distribution medium:
                                           #   "Blu-ray", "4K UHD", "DVD", "Vinyl", "CD",
                                           #   "Cassette", "Digital", "Streaming", "Skill",
                                           #   "ROM", "Z-machine", "Glulx", "Twine", "EPUB"
    codec: str = ""                        # audio/video codec:
                                           #   "FLAC", "MP3", "AAC", "Opus",
                                           #   "H.264", "H.265", "AV1", "ProRes"
    bitrate: str = ""                      # audio codec bitrate / fidelity tag:
                                           #   "320kbps", "128kbps", "24/96", "lossless".
                                           # Video resolution lives in `resolution`, not here.
    platform: str = ""                     # game / IF runtime target:
                                           #   "PC", "PS4", "Switch", "SNES", "Alexa Skill",
                                           #   "Google Action", "Inform 7"
                                           # Empty for non-game/IF media.
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    # Quality / fidelity — typed fields for "play me the best version" workflows.
    # All optional; missing means "unknown / not applicable for this medium".
    resolution: str = ""                   # "480p", "720p", "1080p", "2160p" (4K), "4320p" (8K)
    hdr: str = ""                          # "", "HDR10", "HDR10+", "Dolby Vision", "HLG"
    audio_channels: str = ""               # "mono", "stereo", "5.1", "7.1", "Atmos"
    sample_rate: Optional[int] = None      # Hz — 44100, 48000, 96000, 192000

    # Localisation — three orthogonal axes; do NOT collapse into VariantKind.REGIONAL
    audio_language: str = ""               # ISO 639-1 of the primary audio track
    subtitle_languages: List[str] = []     # ISO 639-1 codes for available subtitle tracks
    # `region` (above) records the release market. (region, audio_language,
    # subtitle_languages) form the dub/sub/market triple. `VariantKind.REGIONAL` is for
    # editorial differences (censorship cuts, alternate scenes), NOT for language tracks.

    # Release metadata
    release_status: ReleaseStatus = ReleaseStatus.RELEASED
                                          # Status of THIS specific Release. May differ from
                                          # `work.release_status`: e.g. a Work with several
                                          # editions where one has been WITHDRAWN (out of
                                          # print) while the Work overall remains RELEASED.
                                          # Precedence rule: a consumer asking
                                          # "is this thing available?" reads `Release.release_status`;
                                          # asking "does this thing exist?" reads
                                          # `work.release_status`.
    release_date: Optional[str] = None    # ISO date or year string

    # Rights and availability — typed instead of buried in extra
    license: str = ""                      # "all_rights_reserved" (default if commercial),
                                           # "public_domain", "cc_by", "cc_by_sa", "cc0", etc.
    region_locked: Optional[bool] = None   # True = access is restricted by region (allowed
                                           # regions in `regions_available`); False = worldwide;
                                           # None = unknown.
    regions_available: List[str] = []      # ISO 3166-1 alpha-2 codes. Meaning is gated by
                                           # `region_locked`: if True, this is the allowlist
                                           # (empty = unknown allowlist); if False or None,
                                           # the field is informational only.
    available_from: Optional[str] = None   # ISO date — when this Release becomes (or became) available
    available_until: Optional[str] = None  # ISO date — when access is scheduled to end (e.g.
                                           # "leaves Netflix on 2026-01-31"). None = no scheduled end.
    availability_windows: List[Tuple[Optional[str], Optional[str]]] = []
                                           # Cycled availability ("Disney vault" pattern):
                                           # ordered list of (from, until) ISO-date pairs. Either
                                           # side may be None for open-ended bookends. Use only
                                           # when there are *multiple* windows; the simple single-
                                           # window case stays in `available_from` / `available_until`.

    # Playback
    uri: str = ""                          # stream URL, file path, or platform deep link
    image: str = ""                        # cover art URL

    # Mid-Release navigation and accessibility
    chapters: List[Chapter] = []           # ordered by `offset`; empty = no chapter info
    accessibility: List[AccessibilityTrack] = []

    # Composite Releases (box sets, anthology Blu-rays). A box set is a single Release
    # that aggregates several Works WITHOUT a synthetic container Work. `contents` lists
    # the constituent Works as Appearances. `work` of the Release should be set to the
    # principal Work (the headline title of the set) or to a dedicated "set" Work when
    # the contents have no headline. Empty = ordinary single-Work Release.
    contents: List[Appearance] = []

    # Scoring
    match_confidence: float = 0.0         # [0.0, 1.0]; set by resolver, not by data entry

    # Infrastructure
    label: Optional[EntityRef] = None
    distributor: Optional[EntityRef] = None

    # Cross-references
    external_ids: Dict[str, str] = {}
    extra: Dict[str, Any] = {}
```

#### Work vs Release — decision guide

| The question | Answer |
|---|---|
| Is "Alien" the same film as "Alien (Director's Cut)"? | Same Work, different Releases (`variant_kind = DIRECTORS`) |
| Is "Battery" on the original album the same as on a compilation? | Same Work, two Appearances in two different Release containers |
| Are the primary stream URL and backup mirror of BBC Radio 4 the same? | Same Work, two Releases with different URIs |
| Is the 1986 CD pressing and the 2016 remaster of Master of Puppets the same album? | Same Work, two Releases (`variant_kind = REMASTERED` on the second) |
| Is a cover version of Hallelujah the same Work as the original? | Different Works; a `covers` relation may link them (see §6) |

**Inheritance:** Release has no identity fields of its own. Identity
(title, year, runtime, language, country, credits, content_genres) is
always read through `release.work`; the Release model deliberately does
not declare those fields and a consumer must never copy them onto the
Release. Release-level fields are strictly manifestation: `variant_kind`,
`edition`, `region`, format / quality / stream fields, localisation,
`uri`, `image`, `chapters`, `accessibility`, rights / availability,
`contents`. Release values never back-propagate into Work.

**`Work.tracklist` vs `Release.contents`** — both are `List[Appearance]`
but answer different questions:

- `Work.tracklist` is the *canonical* track / chapter / episode order
  of a single Work — the album's intended sequence, the book's chapter
  list, the comic series' issue order. It is identity-level: the same
  Work always has the same tracklist.
- `Release.contents` is the *aggregation* of multiple distinct Works in
  one box-set or anthology Release — a Blu-ray boxed trilogy, a deluxe
  multi-album set, a season collected on one DVD. It is manifestation-
  level: different editions can group different Works without affecting
  any of the underlying Works.

A reissued album with bonus tracks remains a single Work and a single
tracklist; the bonus tracks are `Appearance`s with `is_bonus=True`. A
boxed set of three previously-released albums uses
`Release.contents`, leaves each album's `Work.tracklist` untouched, and
sets `Release.work` to the principal album (or to a dedicated "set"
Work when there is no principal).

---

### 5.7 `Entity`

A person, band, organisation, or collection that participates in Works. Entities are
distinct from Works — an Entity does not have a `media_type` and cannot be played.

```python
class Entity(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    kind: EntityKind
    aliases: List[str] = []

    # Band/group roster — temporal, with MembershipStatus
    memberships: List[Membership] = []     # for GROUP: member list over time
                                           # for SERIES: constituent works (via Appearance)

    # Organisational hierarchy
    part_of: Optional[EntityRef] = None   # member of a label group, imprint, franchise

    # Lifecycle
    status: Optional[str] = None          # "active", "split-up", "on hold", "changed name";
                                           # free text (not enum) because group lifecycle
                                           # vocabulary varies heavily across databases
    years_active: List[str] = []          # ["1986-1991", "1993-present"]
    formed: Optional[str] = None          # year or ISO date
    disbanded: Optional[str] = None       # year or ISO date

    # Cross-references
    external_ids: Dict[str, str] = {}
    extra: Dict[str, Any] = {}
```

---

### 5.8 `License`

`Release.license: str` is the canonical persisted form for licence
information — an SPDX-style identifier (`"CC-BY-SA-4.0"`,
`"all_rights_reserved"`, …) or the empty string for "unknown."
`License` is the typed companion for callers who want to filter on
rights without string-matching every variation.

```python
class License(BaseModel):
    identifier: str = ""               # SPDX-style or free string
    name: str = ""
    url: str = ""
    attribution: bool = True           # credit required (CC default)
    share_alike: bool = False          # derivatives must adopt same licence
    commercial: bool = True            # commercial use permitted
    derivatives: bool = True           # derivative works permitted
    is_public_domain: bool = False     # PD / CC0 / PDM

    def is_open(self) -> bool: ...
    @classmethod
    def from_spdx(cls, spdx: str) -> "License": ...
```

`License.from_spdx()` parses the well-known Creative Commons family
(`CC0-1.0`, `CC-BY`, `CC-BY-SA`, `CC-BY-NC`, `CC-BY-NC-SA`, `CC-BY-ND`,
`CC-BY-NC-ND`), the public-domain forms (`PDM`, `public_domain`), and
falls back to a fully-restricted licence for unknown identifiers. The
returned model is a *view* — `Release.license` stays the source of
truth.

### 5.9 `Programme` and `Schedule`

Live linear broadcast (`MediaType.TV`, `MediaType.RADIO`) needs a
schedule model: *what is airing on this channel at what time*. The
channel-as-Work captures stable channel identity; `Schedule` and
`Programme` capture the airing axis.

```python
class Programme(BaseModel):
    """A single airing of a Work on a broadcast channel."""
    work: EntityRef                          # the content Work being aired
    channel: EntityRef                       # the broadcast channel Work / Entity
    starts_at: str                           # ISO datetime; aired-at start
    ends_at: Optional[str] = None
    runtime: Optional[float] = None          # seconds
    is_live: bool = False
    is_repeat: bool = False
    extra: Dict[str, Any] = {}


class Schedule(BaseModel):
    """An ordered list of Programme slots for a single channel."""
    channel: EntityRef
    programmes: List[Programme] = []
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    source: str = ""                         # "tunein", "tvmaze", "epg.xml", …
    fetched_at: Optional[str] = None
    extra: Dict[str, Any] = {}
```

A `Programme` is a *slot* — it locates a Work in time on a specific
channel. The same episode airing on two channels yields two Programme
records, one Work. Schedules are append-only at the model level; to
refresh, replace the `Schedule` wholesale.

mediavocab does not model "what's on right now" as a function — query
the schedule for the slot whose `[starts_at, ends_at)` contains the
consumer's clock.

### 5.10 `Signals` — scope and pipeline usage

`Signals` is the **query / disambiguation** model. Persisted records are `Work`s; the
taxonomy and `Work` / `Release` / `Entity` models do not use `Signals`. **`Signals` exists
*only* in the resolver pipeline.**

The same shape carries three roles, distinguished by direction of flow:

1. **Query** (caller → resolver). The caller fills in what they know:
   ```python
   Signals(title="Inception", year=2010,
           medium=MediaType.MOVIE,
           modality=PlaybackModality.VIDEO)
   ```
   Used by `MetadataProvider.matches(signals)` to gate dispatch, then passed to
   `MetadataProvider.lookup(signals)` to fetch.

2. **Observation** (provider → consolidator). The provider re-emits a `Signals` on its
   `ProviderMatch.signals` to describe what *it* believes the work is. The consolidator
   compares observations across providers via `compare_signals()` and discards conflicts.

3. **Result** (consolidator → caller). The merged consensus on `ResolveResult.signals`,
   produced by `merge_signals()` over the accepted matches. This is the closest thing the
   resolver pipeline produces to a `Work` — but it is **not** a `Work`: no canonical hash,
   no `credits`, no `tracklist`, no `accessibility` profile. A consumer that needs a
   `Work` calls a separate constructor (e.g.
   `metadatarr.canonicalize.work_from_resolve_result`); there is no implicit
   `Signals → Work` coercion.

**Why the field overlap with `Work` is intentional.** Cross-provider comparison needs
identical comparable structure; the duplication is the reason the comparator can be
written once. The orthogonality axiom (axiom 13) keeps `Signals`-only fields off `Work`:

| `Signals`-only field | Why it doesn't belong on `Work` |
|---|---|
| `include_variants: bool` | Query-only fan-out hint. Not an identity claim. |
| `fanedit_subtype: str` | Sub-classification used by query-time filtering, not stored. |
| `modality: PlaybackModality` | Routing axis (axiom 13). A `Work`'s modality is derived from its `MediaType`. |

| `Work`-only field | Why it doesn't belong on `Signals` |
|---|---|
| `credits` | Identity-shaping; not derivable from a single provider response. |
| `tracklist` | Container-shape; resolved post-merge, not per-provider. |
| `accessibility`, `chapters` | Per-Release; `Signals` is per-Work. |
| `aka`, `localized_titles` | Aliases; merged at canonicalisation, not at lookup. |
| `external_ids` (typed) | `Signals` carries IDs only via `ProviderMatch.external_ids`, never on the bag itself. |

**`compare_signals()` skips `modality`.** The modality is a query hint, never an
observation; comparing it across providers would always tie or always disagree depending
on the caller. `signal_hash()` likewise excludes it. This follows the third clause of
axiom 13: routing-axis fields are absent from identity hashes.

---

## 6. Relationships between Works

The `credits` field on `Work` handles entity→work relationships (who made this).
Work→work relationships (covers, adaptations, sequels, compilations, fanedits) use
the `WorkRelation` model defined below.

```python
class WorkRelationKind(str, Enum):
    COVERS         = "covers"          # this work is a cover/recording of another
    SAMPLES        = "samples"         # this work samples another
    ADAPTED_FROM   = "adapted_from"    # film adapted from a book, game based on a film
    SEQUEL_TO      = "sequel_to"
    PREQUEL_TO     = "prequel_to"
    PART_OF        = "part_of"         # episode/chapter/track within a series/album/season
    LIVE_VERSION   = "live_version"    # live recording of a studio track
    REMIX_OF       = "remix_of"
    SOUNDTRACK_FOR = "soundtrack_for"  # this album is the OST for that film
    BONUS_FOR      = "bonus_for"       # supplementary content tied to another work:
                                       # trailers and teasers, behind-the-scenes featurettes,
                                       # gag reels, commentaries, deleted scenes. Use a free
                                       # `note` field on `WorkRelation` to disambiguate.
    FANEDIT_OF     = "fanedit_of"      # this Work is a fanedit/recut of the target. Use
                                       # alongside `Work.variant_kind` (FANEDIT, TV_TO_MOVIE,
                                       # MOVIE_TO_TV) to tag the kind of recut.
    DLC_FOR        = "dlc_for"         # game DLC tied to a base game (the DLC ships as its
                                       # own Work — different external IDs, distinct schema —
                                       # but is meaningless without the base game).
    EXPANSION_OF   = "expansion_of"    # standalone expansion of a base game / IF (works
                                       # without the base, but is the same franchise lineage).

class WorkRelation(BaseModel):
    kind: WorkRelationKind
    target: "Work"
    note: Optional[str] = None
```

### 6.1 Release-level relations

Some relationships are *per-edition*, not per-Work: a 2025 Atmos
remaster supersedes the 2017 stereo remaster of the same album. The
underlying Work is unchanged, but the Release graph chains through
the manifestation timeline. Use `ReleaseRelation` for these.

```python
class ReleaseRelationKind(str, Enum):
    SUPERSEDES   = "supersedes"        # this Release replaces an earlier one
    REMASTER_OF  = "remaster_of"       # explicit remaster lineage (newer remaster of older one)
    REISSUE_OF   = "reissue_of"        # later commercial release of the same edition
    PORT_OF      = "port_of"           # platform port of a game / IF (same Work, new platform)
    DERIVED_FROM = "derived_from"      # generic catch-all

class ReleaseRelation(BaseModel):
    kind: ReleaseRelationKind
    target: "Release"
    note: Optional[str] = None
```

Use sparingly. Most Release-to-Release distinctions are encoded by
the format / quality / variant fields plus `release_hash` — a 4K
Blu-ray of the same cut is *already* distinguishable from a DVD.
`ReleaseRelation` is for explicit *lineage* claims a consumer wants
to surface ("this remaster supersedes that one and you should hide
the older record").

**`target` is a forward reference, not a deep embed.** A consumer that
serialises a graph of related Works must avoid recursive nesting (a
`COVERS` chain or `PART_OF` series will otherwise blow the wire format).
Idiomatic use: store relations with a `target` that carries only the
fields needed to resolve identity later — typically `title`, `year`,
`media_type`, and one entry in `external_ids` — and resolve to a full
Work record on the consumer side.

**Where do relations live?** mediavocab does not pin
relations to a specific field on `Work`. The two viable positions:

- **Co-located on Work.** Add `Work.relations: List[WorkRelation] = []`.
  Cheap to author, fast to read, but every Work record carries the
  graph edges out of it — splits a `Work.model_dump()` from cleanly
  representing identity vs. relationship.
- **External relation table.** Keep `Work` flat; consumers store
  `WorkRelation` records keyed by `(work_hash, kind)`. This matches
  how the canonical-Work / sidecar-relation split works in
  resolver-driven pipelines.

mediavocab itself does **not** include `relations` on `Work` for now —
the `WorkRelation` model is shipped, the field is consumer choice. If
a future spec version adds the field, the field shape is fixed
(`List[WorkRelation]`).

---

## 7. Text utilities

### 7.1 `text.normalize`

All functions operate on Unicode strings. Normalisation is applied before any comparison
to ensure "café" == "cafe", "feat. Drake" is stripped, and punctuation differences do
not produce false negatives.

```python
def strip_diacritics(text: str) -> str:
    """NFKD decomposition, drop combining marks. Preserves base characters of any
    script (Cyrillic, CJK, Greek). 'café' → 'cafe'."""

def normalize(text: str) -> str:
    """Full normalisation pipeline:
    1. strip_diacritics
    2. lowercase
    3. remove featured artist credits: (feat|ft|featuring) ...
    4. remove parenthetical and bracketed suffixes
    5. collapse non-word characters to spaces
    6. strip leading/trailing whitespace, collapse internal whitespace
    Result is suitable for fuzzy comparison."""

def fuzzy_ratio(a: str, b: str) -> float:
    """SequenceMatcher ratio on normalize(a) vs normalize(b). Range [0.0, 1.0].
    0.0 = completely different, 1.0 = identical after normalisation."""

def best_match(query: str, candidates: List[str]) -> Tuple[str, float]:
    """Return (best_candidate, score) from candidates. Applies fuzzy_ratio to each.
    Useful for AKA alias matching."""

def title_words(text: str) -> List[str]:
    """Tokenise into meaningful words. Strips common stopwords and articles (the, a, an,
    der, die, das, le, la, los, las). Useful for keyword-based search."""
```

### 7.2 `text.compare`

Pairwise comparison of two Works to determine whether they describe the same item and
how well a candidate matches a query.

#### Default tolerances

```python
TITLE_MIN   = 0.92   # minimum fuzzy_ratio for title agreement
ARTIST_MIN  = 0.90   # minimum fuzzy_ratio for artist/director agreement
YEAR_WINDOW = 1      # maximum year difference for agreement

RUNTIME_TOLERANCE_S: Dict[MediaType, float] = {
    MediaType.MOVIE:       120.0,   # recuts and extended editions vary widely
    MediaType.EPISODIC_SERIES: 30.0,   # episodes are runtime-padded
    MediaType.TV:               0.0,   # live broadcast — runtime not identity
    MediaType.MUSIC:         3.0,   # studio recordings are precisely timed
    MediaType.MUSIC_VIDEO:  30.0,   # live versions vary
    MediaType.PODCAST:      60.0,   # episode length is approximate
    MediaType.AUDIOBOOK:    60.0,
    MediaType.AUDIO_DRAMA:  60.0,   # episode length is approximate; same as PODCAST
    MediaType.RADIO:         0.0,   # stations have no runtime; programmes use PODCAST
    MediaType.BOOK:          0.0,   # page count is exact
    MediaType.COMIC:         0.0,
    MediaType.GAME:                0.0,
    MediaType.INTERACTIVE_FICTION: 0.0,   # session-based, user-paced
    MediaType.SOUND_EFFECT:        0.0,   # clips are exactly timed; no tolerance
    MediaType.AMBIENT_SOUNDS: 0.0,   # generative/looping; runtime is undefined
    MediaType.GENERIC:        5.0,
    MediaType.NOT_MEDIA:     0.0,   # not applicable; included for exhaustive enum coverage
}
```

#### Functions

```python
class Conflict(BaseModel):
    field: str
    ours: Any
    theirs: Any

def compare(a: Work, b: Work) -> List[Conflict]:
    """Return overlapping fields that disagree.

    Compared fields (only when both sides have a value):
        title (fuzzy), year, country, runtime (within RUNTIME_TOLERANCE_S),
        media_type, language, season, episode, series_title,
        variant_kind, edition, source_format.

    Out-of-scope fields (never trigger a Conflict):
        aka, localized_titles, content_genres, credits, tracklist,
        external_ids, extra, release_status, color, audio_present,
        episode_orderings — these are mutable / merged, not identity.

    Absence of a field on either side is NOT a conflict — it is unknown.
    Empty list means no contradictions found (may still be a weak match)."""

def score(query: Work, candidate: Work) -> float:
    """[0.0, 1.0] match quality.
    Hard penalties (multiplicative):
    - Title fuzzy ratio is the primary driver; AKA aliases and localized_titles
      are tried as fallbacks.
    - Year mismatch beyond YEAR_WINDOW halves the score.
    - MediaType mismatch halves the score (GENERIC is permissive).
    - For episodic media (EPISODIC_SERIES/PODCAST/RADIO/AUDIO_DRAMA),
      `series_title` mismatch halves the score; mismatching season/episode
      (when both sides specify them) halves it again.
    - country mismatch halves the score (when both sides specify it).
    - language mismatch halves the score (when both sides specify it).

    Bonuses (additive, capped at 1.0):
    - variant_kind agreement adds 0.02 (correct cut > correct film).
    - content_genres overlap adds 0.01 per overlapping tag.
    """

def merge(*works: Work) -> Work:
    """First non-empty/non-None value wins per field. aka lists are unioned.
    Useful for combining partial records from multiple providers."""

def work_hash(w: Work) -> str:
    """Stable SHA1 over identity fields: title (normalised), year, country,
    runtime (rounded), media_type, language, season, episode, series_title,
    variant_kind, edition, source_format.
    credits, aka, localized_titles, content_genres, and episode_orderings
    are excluded — they are not part of canonical identity.
    `series_title` is included because two shows can share season+episode+title
    (S01E01 'Pilot' is a common collision); excluding it produces hash
    collisions for EPISODIC_SERIES, PODCAST, RADIO, and AUDIO_DRAMA works.
    Work has no dedicated artist field; artist identity is expressed via
    RelationRole credits and must be resolved before hashing if needed by the
    consumer. Used as a seed for canonical IDs; same work from different
    providers should produce the same hash."""
```

### 7.3 `text.iso`

```python
def validate_language(code: str) -> str:
    """Validate ISO 639-1 (2-letter) or ISO 639-2 (3-letter) language code.
    Returns normalised lowercase code. Raises ValueError if invalid."""

def validate_country(code: str) -> str:
    """Validate ISO 3166-1 alpha-2 country code.
    Returns normalised uppercase code. Raises ValueError if invalid."""

def normalize_language(v: str) -> str:
    """Accept full language name, 2-letter, or 3-letter code; return ISO 639-1.
    'English' → 'en', 'EN' → 'en', 'eng' → 'en'.
    Raises ValueError for unrecognised input."""

def normalize_country(v: str) -> str:
    """Accept full country name or alpha-2 code; return ISO 3166-1 alpha-2 uppercase.
    'United States' → 'US', 'gb' → 'GB'.
    Raises ValueError for unrecognised input."""
```

---

## 8. Application patterns

`mediavocab` provides vocabulary and structure. All application logic lives
downstream. Detailed application patterns are kept out of this spec to keep it
focused on normative model definitions; they live in `docs/patterns/`. Each
pattern resolves to existing `MediaType`, `EntityKind`, and
`Work`/`Release`/`Entity` fields — no new schema.

- Adult media → `docs/patterns/adult-media.md`
- Games → `docs/patterns/games.md`
- Soundtracks → `docs/patterns/soundtracks.md`
- Motion comics → `docs/patterns/motion-comics.md`
- Independent creators & AI-generated content → `docs/patterns/independent-creators.md`
- Educational content → `docs/patterns/independent-creators.md` (educational subsection)
- IoT devices → `docs/patterns/iot-devices.md`
- Interactive fiction & voice games → `docs/patterns/interactive-fiction.md`
- Reader-paced & user-paced content → `docs/patterns/reader-paced-content.md`
- Mid-Release navigation (`Chapter`) → `docs/patterns/reader-paced-content.md`
- Accessibility tracks → `docs/patterns/accessibility.md`
- Playlists, live-streamer channels, branching narratives → `docs/patterns/playlists-and-channels.md`
- Stage productions → `docs/patterns/stage.md`
- Box sets and composite Releases → `docs/patterns/box-sets.md`
- Format, quality, rights, and availability → `docs/patterns/quality-rights-availability.md`
- Multiple episode orderings → see `Work.episode_orderings` field docs in §5.5

---

## 9. Open questions

Questions 1, 3, 5, and 7 are resolved in the spec body. Questions 2, 4, and 6 remain
open for v1.0 decision.

1. ~~**Work→work relations (§6):** Deferred to v1.1. Stored in `Work.extra` for now;
   a `WorkRelation` model will be added once consumers demonstrate divergence.~~ **Resolved.**

2. ~~**Tracklist on Work vs Release:**~~ **Resolved.** `Work.tracklist`
   is the canonical track / chapter / episode order of a single Work
   (identity-level); `Release.contents` is the Work-aggregation field
   for box sets and anthologies (manifestation-level). Per-edition
   bonus tracks are `Appearance` entries with `is_bonus=True` on the
   Work tracklist. See §5.6.

3. ~~**Channel/station as Work vs Entity:**~~ **Resolved in §5.5.** A
   broadcast station is a `Work`; the broadcasting organisation is an
   `Entity` with `EntityKind.ORGANISATION`.

4. **Free-string vocabularies vs typed registries** — partially
   resolved.
   - `external_ids` now offers **both** representations: the canonical
     ``Work.external_ids: Dict[str, str]`` with well-known key
     constants in ``mediavocab.models.external_ids``, AND the typed
     ``ExternalIds`` Pydantic model (~50 known fields, ISBN
     auto-pairing, ``merge`` with first-writer-wins, ``streams``
     extraction). Either is acceptable — convert via
     ``ExternalIds.from_dict()`` / ``.to_dict()``. **Resolved for
     external_ids.**
   - `content_genres` remains `List[str]` with `GENRE_*` string
     constants. Adding the typed-model variant for genres is deferred
     until a consumer demonstrates the need. **Open for content_genres.**

5. ~~**Multi-language `aka`:**~~ **Resolved.** `Work.aka` remains
   `List[str]` for plain alternative spellings; `Work.localized_titles:
   List[Tuple[str, str]]` carries language-tagged titles for
   cross-locale matching. Both are excluded from the identity hash.

6. ~~**Adult/explicit content modelling:**~~ **Resolved.**
   `GENRE_ADULT` covers the content flag; scene-level Work, performer
   Entity, and adult-database `external_ids` keys live in
   `docs/patterns/adult-media.md`.

---

## 10. Versioning and stability

- **`taxonomy/`** — stable from v1.0. Enum values are never removed; new values may
  be added in minor versions. Renaming a value is a breaking change.
- **`models/`** — stable from v1.0. Fields are never removed; optional fields may be
  added in minor versions. Changing a field type is a breaking change.
- **`text/`** — function signatures are stable from v1.0. Tolerance defaults may be
  tuned in minor versions with changelog notes.
- **`genre.py` constants** — additive only. New constants may be added in any version.
  Changing a constant string value is a breaking change.

### 10.1 Field mutability after canonicalisation

Once a Work has been canonicalised (assigned a `work_hash`), consumers must
treat its fields as falling into two classes:

**Immutable** — changing these produces a *different* Work. A consumer that
discovers a different value has discovered a different Work, not new
information about the same one:

- `media_type`, `year`, `runtime`, `country`, `language`, `season`, `episode`,
  `series_title`, `variant_kind`, `edition`, `source_format`

(These are the inputs to `work_hash`; cf. §7.2.)

**Mutable** — these accumulate over time as more sources are merged. A new
provider supplying additional values is *enrichment*, not a conflict:

- `aka`, `localized_titles`, `content_genres`, `credits`, `tracklist`,
  `external_ids`, `extra`, `release_status`

**`tracklist` on a `PLAYLIST` Work** is mutable in the §10.1 sense even
though "what tracks are in the playlist" is the playlist's reason to
exist. A reordered or membership-edited Spotify playlist is *the same
playlist* in source-side terms (same `spotify_playlist_id`); the hash
agrees by design. Consumers that need to detect "the playlist contents
changed" should compare `tracklist` directly against a snapshot, not
infer it from `work_hash`.

A consumer rescanning a source and finding a *different* immutable value
should treat the new record as a separate Work and resolve the conflict
upstream (typically by retiring the older record). The hash contract in §7.2
guarantees that future spec versions will not retroactively invalidate
existing hashes.

### 10.2 The `extra` escape hatch — what it is, what it isn't

Every model that surfaces external metadata carries an `extra` dict
(`Work.extra`, `Release.extra`, `Entity.extra`, `Programme.extra`,
`Schedule.extra`, `ExternalIds.extra`). This is an explicit landfill
for *provider-specific values that have not yet earned a typed field*.

**The contract**

1. **Strings preferred, lists / numbers tolerated.** New code should
   write strings only. `Programme.extra`, `Schedule.extra`, and
   `ExternalIds.extra` are typed `Dict[str, str]` — the validator will
   reject non-string values. `Work.extra`, `Release.extra`, and
   `Entity.extra` keep `Dict[str, Any]` for backwards compatibility
   with existing consumers that store lists (genre tags, stream URL
   arrays); new fields written here SHOULD still be strings.

2. **Promotion is the goal.** A key that appears across two or more
   providers, or that downstream consumers branch on, is a candidate
   for promotion to a typed field on the next minor release. The
   `extra` is a staging area, not a final destination.

3. **Identity-irrelevant.** No `extra` key participates in `work_hash`
   or `release_hash`. If you need a value to anchor identity, it is
   not an `extra` entry — promote it to a typed field first.

4. **Provider-namespaced when ambiguous.** Two providers writing the
   same key (`url`, `image`, `source`) collide silently. Prefix with
   the provider when the key is not universally well-defined:
   `bandcamp_band_id`, `audiodb_artist_id`. The same convention used
   for typed fields in `ExternalIds`.

5. **No mediavocab-internal use.** mediavocab itself never *reads*
   `extra` values. Consumers are free to read and write; the spec
   makes no assertion about what's in there. Anything mediavocab
   ships normative behaviour around must be a typed field.
