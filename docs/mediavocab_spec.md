# mediavocab — Formal Specification

**Version:** 0.5-draft  
**Status:** Working draft — iterate before implementation  
**Scope:** Standalone vocabulary and data-model library for any software that catalogues,
resolves, plays, or recommends media content.

---

## 1. Purpose

Every project that touches media content independently re-defines the same vocabulary:
what kinds of media exist, what people and organisations are involved, how editions relate
to canonical works, how band members come and go. The definitions are subtly incompatible,
making cross-project data exchange painful.

`mediavocab` defines these concepts once, prescriptively. It owns the shared **nouns**.
Consuming packages own the **verbs** — resolving, scraping, playing, recommending.

### 1.1 Intended consumers

- Metadata resolution libraries (metadatarr)
- Media scrapers and archivers (pymetal, pyfanedit)
- Media players and streaming clients (OCP)
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

1. **A type earns its place by changing the schema.**
   If two kinds of content require identical fields, the same external databases, and the
   same comparison tolerances, they are the same type. Genre tags distinguish them.

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
    label, PODCAST if distributed via RSS. The same content in two different distribution
    channels produces two Releases with the same Work but potentially different types.
    `content_genres` handles the aesthetic; `MediaType` handles the schema.

11. **Objective technical attributes are fields, not genres.**
    Colour, aspect ratio, frame rate, and similar measurable properties of a work belong
    as typed fields on `Work`, not in `content_genres`. Genre describes thematic or
    cultural character; a technical attribute describes the artefact itself.
    (Corollary that admits `color: Optional[bool]` on `Work`.)

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
    MOVIE       = "movie"
    TV          = "tv"
    MUSIC       = "music"
    MUSIC_VIDEO = "music_video"
    PODCAST     = "podcast"
    AUDIOBOOK   = "audiobook"
    AUDIO_DRAMA = "audio_drama"
    RADIO       = "radio"
    BOOK        = "book"
    COMIC       = "comic"
    GAME                = "game"
    INTERACTIVE_FICTION = "interactive_fiction"
    STAGE               = "stage"
    SOUND_EFFECT        = "sound_effect"
    AMBIENT_SOUNDS      = "ambient_sounds"
    GENERIC             = "generic"
    NOT_MEDIA           = "not_media"
```

#### Value definitions

**`MOVIE`**  
Feature films and short films. Schema: title, director, cast, runtime, theatrical release
date, IMDB/TMDB IDs, production country. Runtime distinguishes short (≤ 40 min) from
feature — no separate type is needed. Documentaries, silent films, animated films, and
adult films are all MOVIE with an appropriate `content_genres` tag.

**`TV`**  
Episodic video narrative intended for broadcast or streaming in episodes. Schema: series
title, season, episode number, network, first air date, TVmaze/TVDB IDs. The `season`
and `episode` fields on `Work` handle the episode↔series distinction — a series record
has `season = None`, an episode record has both set. TV channels/networks are tracked
as `Entity` with `EntityKind.ORGANISATION`; individual shows are `Work` with `MediaType.TV`.

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
programmes repackaged as podcasts belong here. A podcast series is a `Work` with
`episode = None`; individual episodes have `episode` set.

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
All radio content: individual programmes/shows AND broadcast stations/channels.
A station ("BBC Radio 4", "NTS Radio 1") is a `Work` with `episode = None` and no
runtime. Its stream URLs are Releases. Individual programmes ("The Archers S65E12")
are Works with `episode` set. Cross-referencing stations across providers (TuneIn,
RadioBrowser, RDS PI codes) uses `external_ids` exactly as for films. Multiple stream
URLs for the same station (mirrors, bitrates, DAB vs web) are modelled as multiple
Releases of the same Work.

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

The `episode` field on `Work` carries the issue or chapter number — structurally
identical to a TV episode number. The `season` field carries the volume number where
applicable. `series_title` carries the series/run title. A standalone graphic novel
with no issue structure has `episode = None`.

A trade paperback collecting multiple issues is a `Work` with `VariantKind.COMPILATION`
and a `tracklist` of `Appearance` entries (one per collected issue). If it contains
original material (new introduction, bonus story) it earns its own Work identity;
a straight reprint is a Release with `variant_kind = COMPILATION`.

Cultural sub-types (manga, manhwa, manhua) use `content_genres` tags — they share the
same schema and databases only differ in supplementary coverage, not primary identity.
A narrated or animated presentation of a comic is a separate Work — see §8.6.

**`GAME`**  
Interactive software. Present primarily for disambiguation: the verb "play" is shared
with all other media types. Schema: platform, developer, publisher, IGDB / RAWG IDs.
Passive viewing of game footage (Let's Plays, esports broadcasts) is TV or PODCAST
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

**`STAGE`**  
Live theatrical and performance arts: plays, musicals, opera, ballet, stand-up
sets *as performed live in a venue* (the recorded release of the same show is
`MOVIE`/`AUDIO_DRAMA`). Schema: production company, venue, opening night, run
end, cast, director, writer/composer; external IDs: IBDB (Broadway), Theatricalia,
Operabase. The Work is the *production* (a specific staging — RSC's 2008 Hamlet
with David Tennant); the underlying script (Shakespeare's *Hamlet*) is a `BOOK`
linked via `WorkRelation(kind=ADAPTED_FROM)`. Individual nightly performances
are `Release`s of the production Work, with `release_date` as the performance
date and the venue captured in `Release.extra` or as a `RelationRole.PERFORMER`
credit on the venue Entity.

The criterion (axiom 1) is the database split: theatrical productions live on
IBDB / Theatricalia / Operabase, not IMDB / TMDB. The credit schema is
distinct (writer + composer + director + choreographer + producer + lead
performers per role, often per-cast across the run).

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
sources — the consuming player (OCP) chooses.

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

**`FANEDIT`** — Foundation-level catch-all. Downstream packages (e.g. metadatarr via
pyfanedit) sub-classify into FANFIX, FANMIX, FANEDIT_SHORT, etc. These sub-types do not
belong in the foundation because they are specific to a single database (IFDB/fanedit.org).

**`TV_TO_MOVIE` / `MOVIE_TO_TV`** — Structural transformations that change the work's
relationship to its source. A TV-to-movie cut has a fundamentally different runtime and
narrative structure from any episode of the source series.

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

    EVENT        = "event"         # bounded real-world grouping above the production:
                                   # tour, festival, convention, season-of-screenings.
                                   # Has start/end dates, optional venues, member productions
                                   # or performances referenced from `Release.extra`/`Entity.part_of`.
                                   # Examples: "Pink Floyd 1980 The Wall Tour",
                                   # "Cannes 2024", "EVO 2023". Distinct from `SERIES` (a
                                   # cataloguing container without a real-world date range).

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
and must both be stored. This lesson comes from real data in metal-archives, where bands
with decades of lineup history cannot be accurately represented without this distinction.

```python
class MembershipStatus(str, Enum):
    CURRENT   = "current"    # actively in the group now
    PAST      = "past"       # confirmed former member; date_to should be set
    LIVE      = "live"       # touring/live member only; not on studio recordings
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
- `LIVE` and `GUEST` members do not appear on the principal lineup of studio recordings;
  they appear in the `GUEST` section of release credits.

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

# Canonical narrative genres (apply to MOVIE / TV / BOOK / COMIC / GAME / IF / STAGE)
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

An entity's contribution to a specific Work or Release. Captures who played/wrote/
produced/engineered on a particular recording, not who is generally associated with a
band or project.

```python
class Credit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    entity: EntityRef
    role: str                             # free text from source: "Electric Guitar", "Mix Engineer"
    relation_role: RelationRole           # typed role for programmatic routing (e.g. provider selection)
    section: CreditSection = CreditSection.PRINCIPAL
    position: Optional[int] = None        # editorial credit ordering (1-based) within (section,
                                          # relation_role). None = unspecified. Film opening titles,
                                          # liner notes, and book co-author orderings are
                                          # editorially significant; List ordering alone is not
                                          # reliable across JSON round-trips.
    note: Optional[str] = None            # "(tracks 1–4 only)", "(R.I.P. 1998)"
```

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
    year: Optional[int] = None             # original release/broadcast year of this specific Work;
                                           # for TV episodes: episode air year (not series debut year);
                                           # for remasters: original release year (remaster year → Release)
    runtime: Optional[float] = None        # seconds.
                                           # None has TWO meanings — distinguish at the consumer:
                                           #   1. Unknown — not yet resolved
                                           #   2. Indeterminate — user-paced or open-ended:
                                           #      books, comics, slideshows, interactive fiction,
                                           #      radio stations, IPTV, generative ambient.
                                           # Mediavocab does not encode the distinction — both are
                                           # `runtime=None`. Consumers needing it use Release.stream_mode
                                           # (CONTINUOUS implies open-ended) or media_type heuristics
                                           # (BOOK/COMIC/INTERACTIVE_FICTION → indeterminate).
    language: str = ""                     # ISO 639-1 or 639-2; "" = unknown OR not applicable
                                           # (e.g. instrumental music, non-verbal film). Mediavocab
                                           # does NOT distinguish unknown from not-applicable —
                                           # both use "". Consumers needing the distinction store
                                           # `extra["language_na"] = True` for the not-applicable
                                           # case. Not validated at model level (use text.iso).
    country: str = ""                      # ISO 3166-1 alpha-2 — origin country. "" = unknown OR
                                           # not applicable (international co-productions with no
                                           # single origin country). Same conflation rule as language.

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
                                           # "org_type" (ORGANISATION sub-classification),
                                           # "work_relation_*" (work→work links until §6 is formalised)
```

#### Work and radio stations

A radio station is a Work with `media_type = MediaType.RADIO`, `episode = None`,
`runtime = None`, and `external_ids` containing the station's IDs across provider
databases (TuneIn, RadioBrowser, RDS PI code, etc.). Its stream URLs are modelled as
Releases. Individual programmes on that station are separate Works with `episode` set
and a `Credit` linking to the station via `RelationRole.DISTRIBUTOR` or a `series_title`
pointing to the show name.

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
    bitrate: str = ""                      # codec parameters where relevant:
                                           #   "320kbps", "128kbps", "24/96", "1080p", "2160p"
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
    release_date: Optional[str] = None    # ISO date or year string

    # Rights and availability — typed instead of buried in extra
    license: str = ""                      # "all_rights_reserved" (default if commercial),
                                           # "public_domain", "cc_by", "cc_by_sa", "cc0", etc.
    region_locked: bool = False            # True if access is restricted by region; the allowed
                                           # regions are listed in `regions_available` (when known)
    regions_available: List[str] = []      # ISO 3166-1 alpha-2; empty = unknown or worldwide
    available_from: Optional[str] = None   # ISO date — when this Release becomes (or became) available
    available_until: Optional[str] = None  # ISO date — when access is scheduled to end (e.g.
                                           # "leaves Netflix on 2026-01-31"). None = no scheduled end.

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

    # Release-level credits. Used when a credit applies to THIS specific Release but
    # not to the Work at large: a featured artist on a remix or radio edit, a
    # remastering engineer, a session musician on a deluxe-edition bonus track,
    # a translator credited on a localised edition. Work-level credits remain on
    # `Work.credits`; Release credits supplement them.
    credits: List[Credit] = []

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

## 6. Relationships between Works

The `credits` field on `Work` handles entity→work relationships (who made this).
Work→work relationships (covers, adaptations, sequels, compilations) require a separate
model. This is defined for completeness; implementation is deferred to a future version.

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
    PROMOTES       = "promotes"        # this work promotes another (trailer, teaser, ad)
    BONUS_FOR      = "bonus_for"       # behind-the-scenes featurette, gag reel, commentary
    DELETED_SCENE  = "deleted_scene"   # scene cut from another work; not in the canonical edit

class WorkRelation(BaseModel):
    kind: WorkRelationKind
    target: "Work"
    note: Optional[str] = None
```

Work→work relations are stored on the `Work.extra` field until this is formalised.

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
    MediaType.TV:           30.0,   # broadcast padding varies; episodes are rounded
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
    MediaType.STAGE:               0.0,   # nightly performances vary; no tolerance applies
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
    Absence of a field on either side is NOT a conflict — it is unknown.
    Empty list means no contradictions found (may still be a weak match)."""

def score(query: Work, candidate: Work) -> float:
    """[0.0, 1.0] match quality.
    Hard penalties (multiplicative):
    - Title fuzzy ratio is the primary driver; AKA aliases and localized_titles
      are tried as fallbacks.
    - Year mismatch beyond YEAR_WINDOW halves the score.
    - MediaType mismatch halves the score (GENERIC is permissive).
    - For episodic media (TV/PODCAST/RADIO/AUDIO_DRAMA), `series_title` mismatch
      halves the score; mismatching season/episode (when both sides specify
      them) halves it again.
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
    collisions for TV, PODCAST, RADIO, AUDIO_DRAMA, and STAGE works.
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

## 8. What consuming packages do

`mediavocab` provides vocabulary and structure. All application logic lives downstream.

| Package | Uses from mediavocab | Adds on top |
|---|---|---|
| **metadatarr** | MediaType, VariantKind, EntityKind, RelationRole, Work, Release, Entity, Membership, Credit, text/* | Provider API clients, ExternalIds (IMDB, MBID, ISBN…), resolution pipeline, Pydantic Signals model, provider registry |
| **pymetal** | EntityKind (GROUP, PERSON, ORGANISATION), RelationRole, MembershipStatus, CreditSection, Membership, Credit, Entity | Metal-archives scraper, Band/Artist/Release/Song/TrackAppearance models with MA-specific fields |
| **pyfanedit** | VariantKind, Work, Release | fanedit.org / IFDB scraper, FANEDIT sub-type map (FANFIX, FANMIX, etc.) |
| **OCP / player** | MediaType (incl. SOUND_EFFECT), StreamMode, RelationRole, Work, Release | PlaybackType, PlayerState, intent routing, skill registration |
| **Any library manager** | taxonomy/* (zero deps) | UI models, persistence layer, recommendation logic |

### 8.1 How metadatarr's `Signals` maps to `Work`

metadatarr uses a `Signals` model (a subset of Work fields) for the disambiguation
phase before a full record is resolved. After resolution, a `Signals` instance can be
promoted to a `Work`. The mapping is direct: all `Signals` fields exist on `Work`.
`Signals`-specific fields (`include_variants`, `aka` as fallback candidates) are
`Work.extra` or handled in the resolution layer.

### 8.2 How pymetal's `LineupMember` maps to `Membership`

pymetal's `LineupMember` (band_id, artist_id, role, status, date_from, date_to) maps
directly to `Membership` (entity: EntityRef, roles: List[str], status: MembershipStatus,
date_from, date_to). pymetal's `CreditSection` and `ReleaseLineup` map to
`CreditSection` and `Credit`. The mediavocab models were designed with pymetal's
real-world data as the primary test case.

### 8.3 Adult media modelling patterns

Adult content fits the existing model without new types or enums. This section documents
the canonical patterns for each structural concern.

#### Content flag

Mark any Work with `content_genres = GENRE_ADULT`. This applies regardless of `MediaType`
— a feature film, a short scene, a photo set described as a Book/Comic, and a podcast
interview all use the same flag. Consumers filter on it independently of type.

#### Scene vs feature

An adult feature film is a `Work` (`MediaType.MOVIE`). Individual scenes within it are
also Works (`MediaType.MOVIE`, short runtime), collected as `Appearance` entries in the
feature's `tracklist`. This is identical to the track-on-album pattern.

```
Work: "Film Title" (full feature, ~90 min)
  tracklist:
    Appearance(position=1, work=Work("Scene 1", runtime=1200))
    Appearance(position=2, work=Work("Scene 2", runtime=900))
    ...
```

Scenes are indexed independently in adult databases (IAFD scene IDs, etc.) and should
carry their own `external_ids`. A scene released standalone (clip store, subscription
feed) gets its own Release with a URI.

#### Performer identity and stage names

Adult performers frequently use multiple stage names across their career, retire names,
or return under new aliases. This is the same problem as pymetal's band member aliases —
solved by `Entity.aliases` for concurrent known names, and by multiple `Membership`
records for time-sliced name periods when the stage name itself changed.

```python
Entity(
    name="Current Stage Name",
    kind=EntityKind.PERSON,
    aliases=["Former Stage Name", "Alternate Spelling"],
    # If the name change has a known date, use Membership records:
    memberships=[
        Membership(
            entity=EntityRef(name="Former Stage Name", kind=EntityKind.PERSON),
            roles=["performer"],
            status=MembershipStatus.PAST,
            date_from="2010",
            date_to="2015",
        ),
    ],
    external_ids={
        "iafd_performer": "...",
        "babepedia": "...",
        "freeones": "...",
    },
)
```

The `note` field on `Membership` accommodates annotations like "name change after studio
switch" or "returned from retirement".

#### Studio vs platform vs self-publishing creator

| Scenario | EntityKind | Notes |
|---|---|---|
| Traditional production studio | `ORGANISATION` | Brazzers, Wicked, Evil Angel |
| Subscription platform | `ORGANISATION` | OnlyFans, Fansly, ManyVids |
| Self-publishing creator | `PERSON` + `PUBLISHER` role | Performer IS the studio; dual credit |
| Clip store aggregator | `ORGANISATION` | Clips4Sale, MFC Share |

A self-publishing creator (OnlyFans model) appears in a Work's `credits` twice:
once as `RelationRole.PERFORMER` (CreditSection.PRINCIPAL) and once as
`RelationRole.PUBLISHER` (CreditSection.STAFF). No new EntityKind is needed.

#### Subscription feeds and content aggregation

A performer's OnlyFans feed or a studio's subscription channel is a `Work` with
`MediaType.TV` (episodic) or `MediaType.RADIO` (continuous feed), `stream_mode =
StreamMode.CONTINUOUS` or `ON_DEMAND` depending on delivery. Individual posts/scenes
are Works linked via `Appearance`. The feed itself is identified by its platform URL
in `external_ids`.

#### Databases as `external_ids` keys

Well-known adult database keys for `Work.external_ids` and `Entity.external_ids`:

```python
# Works
EID_IAFD_MOVIE     = "iafd_movie"
EID_ADULTDVDEMPIRE = "adult_dvd_empire"
EID_AEBN           = "aebn"

# Performers (Entity)
EID_IAFD_PERFORMER = "iafd_performer"
EID_BABEPEDIA      = "babepedia"
EID_FREEONES       = "freeones"
```

These follow the same pattern as `EID_IMDB`, `EID_MUSICBRAINZ_RECORDING`, etc. —
string keys defined as constants in `external_ids.py`, no schema enforcement.

#### Hentai

Hentai is anime + adult content: `content_genres = [GENRE_ANIME, GENRE_ADULT]`.
No new type. This is exactly why `content_genres` is `List[str]` — a work belongs
to multiple genres simultaneously. `MediaType` is TV or MOVIE depending on format.
Hentai manga is `MediaType.COMIC` with the same two genre tags.

#### What does NOT change

- `MediaType` — no new values. Adult features are MOVIE; clips are MOVIE (short);
  photo sets distributed as downloads are BOOK or left to `extra`.
- `VariantKind` — no new values. Compilation scenes, regional cuts, remasters all
  use existing values.
- `CreditSection` — PRINCIPAL for performers, STAFF for director/producer/editor.
- `RelationRole` — ACTOR for on-screen performers, DIRECTOR, PRODUCER as usual.

---

### 8.4 Game modelling patterns

#### Canonical game, ROM, and platform port

A game title is a `Work` (`MediaType.GAME`). Releases cover the different physical and
digital manifestations:

```
Work: "Chrono Trigger" (1995, JP, MediaType.GAME)
  external_ids: {"igdb": "...", "mobygames": "...", "rawg": "..."}
  credits:
    - EntityRef("Square", ORGANISATION) / RelationRole.DEVELOPER / CreditSection.PRINCIPAL
    - EntityRef("Nintendo", PUBLISHER) / RelationRole.PUBLISHER / CreditSection.STAFF

Release: SNES cartridge (JP)      source_format="SNES", region="JP", release_date="1995"
Release: SNES cartridge (US)      source_format="SNES", region="US", variant_kind=REGIONAL
Release: SNES ROM image           source_format="SNES ROM", uri="sha1:..."
Release: Nintendo DS port (2008)  → separate Work (see ports below)
Release: Steam (PC, 2011)         source_format="PC", uri="steam://..."
```

#### Console ports

A port to a different platform is a **new Work**, not a Release, because:
- It may have different content (cut features, added content, different bugs fixed)
- It has different credits (the porting team may differ from the original developer)
- It is catalogued as a distinct entry in IGDB, MobyGames, etc.

The port Work links to the original via `WorkRelation(kind=ADAPTED_FROM)`:

```python
Work(
    title="Chrono Trigger",
    year=2008,
    media_type=MediaType.GAME,
    credits=[Credit(entity=EntityRef("Square Enix", EntityKind.ORGANISATION), ...)],
    extra={"relations": [WorkRelation(kind=WorkRelationKind.ADAPTED_FROM,
                                      target=snes_work,
                                      note="Nintendo DS port")]},
)
```

#### Romhacks

A romhack is to a game what a fanedit is to a film. Model as a new Work with
`variant_kind = VariantKind.FANEDIT` and `WorkRelation(kind=ADAPTED_FROM)` pointing
to the original. The romhack creator is credited as `RelationRole.CREATOR` in
`CreditSection.PRINCIPAL`.

#### The emulator / player

Out of scope. The emulator (RetroArch, MAME, Dolphin) is the playback engine, not the
media. It does not belong in `mediavocab`. At most, the emulator developer may appear
as `EntityKind.ORGANISATION` in a consuming application's own data, but that is not a
vocabulary concern.

---

### 8.5 Soundtrack modelling patterns

A soundtrack connects the music domain to the film/TV/game domain. Three distinct cases:

#### 1. Original score (composed for the work)

The score is a `Work` (`MediaType.MUSIC`, album-level) linked to the parent film/game
via `WorkRelation(kind=SOUNDTRACK_FOR)`. The composer is credited on the score Work;
the score is also referenced in the film Work's credits as `RelationRole.COMPOSER`.

```
Work: "Alien" (1979, MOVIE)
  credits: [Credit(EntityRef("Jerry Goldsmith"), COMPOSER, STAFF)]

Work: "Alien: Original Motion Picture Score" (1979, MUSIC)
  extra: {"relations": [WorkRelation(kind=SOUNDTRACK_FOR, target=alien_film)]}
  credits: [Credit(EntityRef("Jerry Goldsmith"), PERFORMER + COMPOSER, PRINCIPAL)]
```

#### 2. Compilation soundtrack (licensed tracks)

A compilation soundtrack (`VariantKind.COMPILATION`) is a `Work` (`MediaType.MUSIC`)
whose `tracklist` lists each licensed track as an `Appearance`. Each track is its own
canonical `Work` (the original song). The Appearance carries no `title_override` unless
it is an edit made for the film.

```
Work: "Guardians of the Galaxy: Awesome Mix Vol. 1" (MUSIC, COMPILATION)
  tracklist:
    Appearance(position=1, work=Work("Hooked on a Feeling", MUSIC, ...))
    Appearance(position=2, work=Work("Go All the Way", MUSIC, ...))
    ...
  extra: {"relations": [WorkRelation(kind=SOUNDTRACK_FOR, target=guardians_film)]}
```

#### 3. Game soundtrack

Identical to original score. The game OST is a `Work` (`MediaType.MUSIC`) with
`WorkRelation(kind=SOUNDTRACK_FOR)` pointing to the game `Work`. Released OSTs often
have their own IMDB/Discogs/MusicBrainz entries and are tracked independently.

If the OST was never officially released as a standalone album, its tracks may still
appear as Works inside the game Work's `tracklist` — the game acts as both Work and
container for its music in that case.

#### 4. Audio drama / audiobook score

Same pattern as film score. An AUDIO_DRAMA production with an original score links to
a MUSIC Work via `SOUNDTRACK_FOR`. This is uncommon but occurs in major productions
(BBC Radio full-cast dramas, Big Finish productions).

#### Summary

| Scenario | Model |
|---|---|
| Original composed score | MUSIC Work + `SOUNDTRACK_FOR` relation to film/game |
| Licensed compilation | MUSIC Work, `COMPILATION` variant, tracklist of existing MUSIC Works |
| Unreleased in-game music | Tracks as Appearances inside the GAME Work's tracklist |
| Composer credit on the film | `RelationRole.COMPOSER` Credit on the film Work |

---

### 8.6 Motion comics and narrated comic formats

A motion comic takes static comic panels and adds narration, voice acting, minimal
animation, sound effects, and music. The credit schema changes: there is now a cast,
a director, a sound designer. By axiom 9 (credit structure change = schema change),
this is a **new Work**, not a Release of the source comic.

```
Work: "Watchmen Motion Comic" (2008, MediaType.TV)
  content_genres: ["motion_comic"]
  credits:
    - EntityRef("Tom Stechschulte", ACTOR) — sole narrator, all characters
    - EntityRef("Jake Strider Hughes", DIRECTOR)
  external_ids: {"imdb": "tt1335296"}
  extra: {"relations": [WorkRelation(kind=ADAPTED_FROM, target=watchmen_comic_work)]}
```

The source comic Work (`MediaType.COMIC`) is unchanged. The motion comic Work
(`MediaType.TV` or `MOVIE`) links back via `ADAPTED_FROM`. Both coexist independently.

#### Taxonomy of video comic formats

| Format | MediaType | content_genres | Notes |
|---|---|---|---|
| Motion comic (full production) | TV or MOVIE | `["motion_comic"]` | New Work, ADAPTED_FROM source |
| YouTube "let's read" narration | TV | `["motion_comic"]` | New Work even if amateur |
| Animated adaptation (full art) | TV or MOVIE | `["animation"]` | ADAPTED_FROM source comic |
| Audiobook reading of a comic script | AUDIOBOOK | `["comics"]` | Unusual; treat as AUDIOBOOK |
| Static panel slideshow, no narration | COMIC | — | Release of the comic, source_format="video" |

The last case (slideshow, no new creative work) is a Release of the COMIC Work with
`source_format = "video slideshow"`. The first four all produce new Works.

---

### 8.7 Independent creators, YouTube series, and AI-generated content

#### YouTube and independent creators

An independent creator's YouTube documentary series ("Unbiased History of Rome",
"Kurzgesagt", "CGP Grey") is `MediaType.TV` — episodic video content. The schema is
identical to a network TV series: season/episode structure, credits, runtime. The
distribution channel (YouTube vs Netflix vs broadcast) is a Release concern, not a
Work concern.

```
Work: "Unbiased History of Rome — Republican Era" (MediaType.TV)
  season=1, episode=3
  series_title="Unbiased History of Rome"
  credits:
    - EntityRef("Dovahhatty", EntityKind.PERSON) / CREATOR / PRINCIPAL
  external_ids: {"youtube_video": "..."}

Entity: "Dovahhatty" (EntityKind.PERSON)
  external_ids: {"youtube_channel": "UCW3D0wXUz89D2K1O3ZMZ9hQ"}
```

The YouTube channel is `EntityKind.ORGANISATION` (the distribution entity). The creator
is `EntityKind.PERSON` credited as `RelationRole.CREATOR` on the Work. If the creator
uses a pseudonym, `Entity.aliases` holds it alongside any real name.

For creators who are simultaneously writer, director, editor, and presenter (most
independent YouTube creators), they appear in multiple `Credit` entries with the
appropriate `RelationRole` for each, all in `CreditSection.PRINCIPAL`.

#### AI-generated content

AI-generated content has no human author but it is still a Work: it has a title, a
`MediaType`, a publication date, and in many cases an external database entry. The
credit model accommodates this without new types.

**No human creator:** Leave `credits` empty, or credit the publishing organisation:

```python
Credit(
    entity=EntityRef("Midjourney Inc.", EntityKind.ORGANISATION),
    role="AI system",
    relation_role=RelationRole.CREATOR,
    section=CreditSection.STAFF,
    note="Generated by Midjourney v6",
)
```

**Human-prompted AI content:** The prompter may be credited as `CREATOR` with a note:

```python
Credit(
    entity=EntityRef("Jane Smith", EntityKind.PERSON),
    role="Prompt author",
    relation_role=RelationRole.CREATOR,
    section=CreditSection.PRINCIPAL,
    note="AI-assisted; generated with Suno v4",
)
```

**Genre tag:** `GENRE_AI_GENERATED` in `content_genres` marks AI-primary works for
consumers that filter on it. This is an informational tag, not a type — an AI-generated
film is still `MediaType.MOVIE`.

**What does NOT change:** No new `EntityKind` for "AI system". The AI tool is modelled
as `EntityKind.ORGANISATION` (the organisation that built it) or left unmodelled entirely.
The vocabulary does not need to enumerate AI tools — that belongs in `Credit.note`
or `Work.extra`.

---

### 8.8 Educational content and recorded courses

A recorded university lecture, MOOC course, or tutorial series is episodic video or
audio content. No new MediaType is needed — the distribution format determines the type.

| Format | MediaType | content_genres | Structure |
|---|---|---|---|
| Video lecture series | TV | `["educational"]` | series_title=course, season=module, episode=lecture |
| Audio-only lecture podcast | PODCAST | `["educational"]` | episode per lecture |
| Single standalone lecture (video) | MOVIE | `["educational"]` | no episode structure |
| Textbook | BOOK | `["educational"]` | standard BOOK |
| Course notes / slide deck | BOOK | `["educational"]` | source_format="PDF" Release |

The lecturer/professor is `RelationRole.HOST` (if conversational) or `RelationRole.CREATOR`
(if scripted/produced). The university or platform (Coursera, edX, Khan Academy) is
`EntityKind.ORGANISATION`. The department or channel is also `EntityKind.ORGANISATION` if useful.

```
Work: "The Early Middle Ages, 284–1000" — Lecture 1 (MediaType.TV)
  series_title = "The Early Middle Ages, 284–1000"
  season = 1, episode = 1
  content_genres = ["educational", "history"]
  credits:
    - EntityRef("Paul Freedman", PERSON) / HOST / PRINCIPAL
    - EntityRef("Yale University", ORGANISATION) / DISTRIBUTOR / STAFF
  external_ids: {"youtube_video": "...", "open_yale": "..."}
```

A MOOC with interactive assignments, quizzes, and certificates is still modelled as
TV — the interactive layer is a platform concern, not a vocabulary concern.

---

### 8.9 IoT and device-mediated playback

A voice assistant request may target a *physical device* rather than (or in addition to)
a specific Work. "Turn on the kitchen radio", "play jazz on my Sonos", and "cast this to
the TV" all involve a playback device as the delivery endpoint. By axiom 4 corollary,
the device is an `Entity` (`EntityKind.DEVICE`); the content it plays is still a Work
classified normally.

```
Entity: "Kitchen Radio Plug" (EntityKind.DEVICE)
  external_ids: {"homeassistant": "switch.kitchen_radio_plug"}

Entity: "Living Room Sonos" (EntityKind.DEVICE)
  external_ids: {"sonos": "...", "homeassistant": "media_player.living_room"}
```

#### Pattern table

| Request | Work `MediaType` | Device `EntityKind` |
|---|---|---|
| "Turn on the kitchen radio" | RADIO | DEVICE (smart plug → legacy radio) |
| "Play jazz on Sonos" | MUSIC | DEVICE (smart speaker) |
| "Cast this to the TV" | MOVIE / TV | DEVICE (cast target / smart TV) |
| "Start the PS4" | GAME (TBD) | DEVICE (game console) |
| "Play Netflix" | TV / MOVIE | DEVICE (smart TV) |

#### Rules

- The Work is always classified using normal `MediaType` rules. "Turn on the kitchen
  radio" resolves to a RADIO Work (the station); the smart plug is the delivery channel.
- When no specific Work is implied ("turn on the Sonos"), the Work is resolved from
  context or left as `MediaType.GENERIC` until a title is known.
- Device identity belongs in `Entity.external_ids` using provider-specific keys
  (e.g. `"homeassistant"`, `"sonos"`, `"chromecast"`, `"kodi"`).
- Routing logic — which URI to send to which device — is the consuming player's
  responsibility. `mediavocab` supplies the vocabulary; OCP owns the routing.

---

### 8.10 OCP `media_label` mapping

Canonical mapping from all 33 OCP `media_label` values in `ocp_media_templates_en.csv`
to mediavocab types. The spec is the source of truth; the dataset adapts to it.

| OCP `media_label` | `MediaType` | `content_genres` / notes |
|---|---|---|
| `movie` | MOVIE | — |
| `black_white_movie` | MOVIE | `color = False` on Work |
| `silent_movie` | MOVIE | `audio_present = False` |
| `short_film` | MOVIE | `GENRE_SHORT_FILM` |
| `documentary` | MOVIE or TV | `GENRE_DOCUMENTARY` — distribution determines type |
| `series` | TV | — |
| `tv` | TV | — |
| `anime` | TV or MOVIE | `GENRE_ANIME` |
| `cartoon` | TV or MOVIE | `GENRE_ANIMATION` |
| `trailer` | MOVIE or TV | `GENRE_TRAILER` — supplementary material |
| `behind_the_scenes` | MOVIE or TV | `GENRE_BEHIND_SCENES` — supplementary material |
| `comic_book` | TV or MOVIE | `GENRE_MOTION_COMIC` — dataset treats this as video; see §8.6. Static COMIC works are not a voice-playback target. |
| `video` | MOVIE or TV | — generic video; type resolved from available metadata |
| `hentai` | TV or MOVIE | `GENRE_ANIME + GENRE_ADULT` |
| `porn` | MOVIE | `GENRE_ADULT` |
| `music` | MUSIC | — |
| `podcast` | PODCAST | — |
| `audiobook` | AUDIOBOOK | — |
| `radio` | RADIO | — |
| `radio_theatre` | AUDIO_DRAMA | `GENRE_RADIO_DRAMA` |
| `asmr` | MUSIC or PODCAST | `GENRE_ASMR` — axiom 10: distribution determines type |
| `adult_asmr` | MUSIC or PODCAST | `GENRE_ASMR + GENRE_ADULT` |
| `audio_description` | MOVIE or TV | Not a standalone Work. Accessibility Release variant of the referenced film/programme. Consumer requests an accessible Release of the underlying Work. See §4.1 excluded values. |
| `news` | TV / RADIO / PODCAST | `GENRE_NEWS` — distribution determines type |
| `short_sound` | SOUND_EFFECT | — |
| `ambient_sounds` | AMBIENT_SOUNDS | Procedurally generated or looping environment audio with no recording identity. Ambient albums with ISRCs on music platforms → `MUSIC + GENRE_AMBIENT` instead (axiom 10). |
| `game` | GAME | — |
| `adult_game` | GAME | `GENRE_ADULT` |
| `audio_device` | N/A | `EntityKind.DEVICE` — see §8.9 |
| `video_device` | N/A | `EntityKind.DEVICE` — see §8.9 |
| `game_device` | N/A | `EntityKind.DEVICE` — see §8.9 |
| `not_media` | NOT_MEDIA | Terminal classifier output. No Work exists to resolve. |

---

### 8.11 Interactive fiction and voice games

Interactive fiction is `MediaType.INTERACTIVE_FICTION`. Schema differs from `GAME`
in three ways that matter for cataloguing:

1. **Author, not developer studio.** Most IF works are single-author. `RelationRole.AUTHOR`
   is the principal credit; `DEVELOPER` is rarely used.
2. **Distinct external database.** IFDB.org and ifiction.org are the canonical
   IF databases; `external_ids` keys `ifdb` and `ifiction`. Note: this `IFDB` is
   the **Interactive Fiction Database** — distinct from the fanedit-community
   IFDB (Internet Fanedit Database), which uses key `fanedit_ifdb`.
3. **Source format encodes the engine.** `Z-machine` (`.z3`–`.z8`), `Glulx`
   (`.gblorb`), `TADS`, `Inform 7`, `Twine` (HTML), `ChoiceScript`, `Ink` (JSON).
   Voice-game variants use `Alexa Skill` / `Google Action` / `Mycroft Skill`.

```python
Work(
    title="Counterfeit Monkey",
    media_type=MediaType.INTERACTIVE_FICTION,
    year=2012,
    content_genres=[GENRE_PARSER_IF, GENRE_BRANCHING],
    credits=[Credit(
        entity=EntityRef(name="Emily Short", kind=EntityKind.PERSON),
        role="author",
        relation_role=RelationRole.AUTHOR,
    )],
    external_ids={"ifdb": "lr40jhwqgyx9rzfr"},
)
Release(
    work=...,
    source_format="Glulx",
    uri="https://...",
)
```

**Voice-game IF.** A narrative Alexa Skill is the same `MediaType.INTERACTIVE_FICTION`
with `source_format="Alexa Skill"`, `content_genres=[GENRE_VOICE_GAME, GENRE_BRANCHING]`,
and `external_ids={"alexa_skill": "amzn1.ask.skill.<uuid>"}`. The "Release" is the
skill itself; no file is downloaded.

**Disambiguation from `GAME`:** a graphic adventure with a parser (Sierra-era titles)
is `GAME` — it ships as a platform binary catalogued on IGDB/MobyGames. A text-only
or voice-only branching narrative is `INTERACTIVE_FICTION` — it ships as a story file
catalogued on IFDB. Sessions are user-paced and indeterminate; `runtime=None` (axiom 11).

---

### 8.12 Reader-paced and user-paced content

Books, comics, slideshows, and interactive fiction share an attribute that is
*not* representable as a runtime: the user controls pacing. A novel's page count
is finite but its reading time depends on the reader. A photo slideshow ends
when the viewer dismisses it. An IF session ends when the player saves and quits.

The spec encodes this as `runtime=None`. There is no `Pacing` axis — adding one
would force every consumer to handle a third state for a property they don't use.
The two `runtime=None` interpretations (unknown vs indeterminate) are distinguished
at the consumer:

- `media_type ∈ {BOOK, COMIC, INTERACTIVE_FICTION}` → indeterminate (user-paced)
- `stream_mode == StreamMode.CONTINUOUS` → indeterminate (open-ended stream)
- otherwise → unknown (treat as missing data)

**Slideshows / photo books.** A photo collection with no ordering metadata is a
`Work(media_type=BOOK, content_genres=[GENRE_PHOTO_BOOK])`. When ordered for
sequential viewing it is `[GENRE_SLIDESHOW]` instead. The slideshow timer (if any)
is a Release-level concern: store interval seconds in `Release.extra["slide_interval"]`
or rely on the consumer's default. A motion-comic slideshow with embedded animation
is *not* this — that is `MOVIE`/`TV` with `GENRE_MOTION_COMIC` (see §8.6).

**Branching narratives that are books, not games.** A "choose your own adventure"
print novel is a `BOOK` with `GENRE_BRANCHING`. A digital implementation of the
same text on Twine or as a Kindle interactive title is `INTERACTIVE_FICTION` —
the distribution channel determines the type (axiom 10).

---

### 8.13 Mid-Release navigation

Audiobook chapters, podcast chapter markers, DVD scene breaks, "skip the intro"
points, and music-album track gaps with their own metadata are all `Release.chapters`.

```python
Release(
    work=audiobook_work,
    chapters=[
        Chapter(offset=0.0,    title="Prologue"),
        Chapter(offset=480.5,  title="Chapter 1: The Wardrobe"),
        Chapter(offset=2310.0, title="Chapter 2: What Lucy Found There"),
        # ...
    ],
)
```

Chapters are markers, not Works. A novel's chapter is part of the same canonical
Work as the rest of the book. By contrast, a track on an album IS a Work
(it can appear on multiple Releases independently) — so tracks live in
`Work.tracklist` as `Appearance`, not in `Release.chapters`.

**When in doubt:** if the unit can appear on multiple Releases with stable
identity (a song reissued on a compilation), it is a Work referenced via
`Appearance`. If it is purely a navigational offset within one Release (a
DVD scene break, an audiobook chapter heading), it is a `Chapter`.

---

### 8.14 Accessibility tracks

Subtitles, closed captions, audio description, sign-language inserts, lyric
files, and transcripts are per-Release assets — the underlying Work is unchanged.
They live in `Release.accessibility: List[AccessibilityTrack]`, never in
`VariantKind`.

```python
Release(
    work=film,
    audio_language="en",
    subtitle_languages=["en", "es", "fr"],
    accessibility=[
        AccessibilityTrack(kind="subtitles", language="en", uri="...en.vtt"),
        AccessibilityTrack(kind="subtitles", language="en", uri="...en-sdh.vtt", sdh=True),
        AccessibilityTrack(kind="subtitles", language="es", uri="...es.vtt"),
        AccessibilityTrack(kind="audio_description", language="en", uri="...ad.mp3"),
        AccessibilityTrack(kind="transcript", language="en", uri="...transcript.txt"),
    ],
)
```

**Why per-Release, not per-Work:** the same Work may have one Release with no
subtitles (theatrical print), another with full multi-language captions
(Blu-ray), and a third with audio description added later. The accessibility
profile is a property of the manifestation, not the work.

**Why `kind` is a free string:** accessibility taxonomy is evolving. Closed
captions vs subtitles, sign language as picture-in-picture vs separate stream,
"Easy Read" text editions, descriptive audio for video games — these all
appear and reorganise too quickly to enum-lock. The principal kinds
("subtitles", "captions", "audio_description", "sign_language", "transcript",
"lyrics") are conventions, not validation.

**Dub vs sub.** `Release.audio_language` is the primary audio track language;
`Release.subtitle_languages` lists available subtitle languages. The release
*market* is `Release.region`. These three axes are independent — collapsing them
into `VariantKind.REGIONAL` (which is reserved for editorial regional differences:
censorship cuts, alternate scenes) is wrong. A Blu-ray sold in the US with
Japanese audio and English subtitles is `region="US"`, `audio_language="ja"`,
`subtitle_languages=["en"]` — no `REGIONAL` variant needed.

---

### 8.15 User playlists, live-streamer channels, branching narratives

**User playlists.** A playlist is a `Work` with `media_type=MUSIC` (or whichever
type its members share) and a `tracklist` of `Appearance`s pointing to the
chosen Works. A playlist's *creator* is the curator (`RelationRole.CREATOR`).
The semantic difference from an album — that the user can reorder, add, and
remove members — is a consumer concern, not a vocabulary concern. The model is
identical; the lifecycle is different.

**Live-streamer channels.** A streamer's channel (Twitch, Kick, YouTube Live)
is a `Work` exactly as a radio station is — `series_title` set to the channel
name, `runtime=None`, individual streams modelled as either `Release`s of the
channel Work (when the channel itself is the entity) or as new Works whose
`series_title` matches (when each stream is a discrete catalogued piece). When
a stream is recorded and archived, the same Work transitions from
`stream_mode=LIVE` on its live Release to `stream_mode=ON_DEMAND` on a
new VOD Release.

**Branching narratives.** Print: `BOOK + GENRE_BRANCHING`. Digital text/voice:
`INTERACTIVE_FICTION` (often `+ GENRE_BRANCHING` for emphasis). Game with
branching choices that ships as a binary (Telltale, Detroit: Become Human):
`GAME + GENRE_BRANCHING`. The MediaType follows the distribution channel
(axiom 10), not the narrative structure.

---

### 8.16 Stage productions

`MediaType.STAGE` is a *production* — a specific staging of a script or score
by a specific director and cast in a specific venue. The script ("Hamlet" by
Shakespeare) is a `BOOK` Work; the production ("RSC's 2008 Hamlet with David
Tennant") is a `STAGE` Work linked via `WorkRelation(kind=ADAPTED_FROM)`.

```python
hamlet_script = Work(title="Hamlet", media_type=MediaType.BOOK, year=1603,
                     credits=[author_credit("William Shakespeare")])
rsc_hamlet = Work(
    title="Hamlet",
    media_type=MediaType.STAGE,
    year=2008,
    series_title="Royal Shakespeare Company",
    credits=[
        director_credit("Gregory Doran"),
        Credit(entity=david_tennant_ref, role="Hamlet",
               relation_role=RelationRole.ACTOR),
    ],
    external_ids={"theatricalia": "..."},
)
```

Each performance night is a `Release` of the production:

```python
nightly = Release(
    work=rsc_hamlet,
    release_date="2008-08-12",
    container="Live",
    extra={"venue": "Royal Shakespeare Theatre, Stratford"},
)
```

When a production is filmed (NT Live, Met Opera HD) the filmed version is a
separate `MOVIE` Work with `WorkRelation(kind=ADAPTED_FROM, target=production)`.
When archival footage of a production is later released as video, it follows
the same pattern. The `STAGE` Work always represents the live production
itself, regardless of whether any recording exists.

External-ID keys: `ibdb` (Broadway), `theatricalia`, `operabase`.

---

### 8.17 Box sets and composite Releases

A box set is a packaging decision, not a creative work. `Release.contents`
lets a Release directly aggregate Works without inventing a synthetic
container Work:

```python
trilogy = Release(
    work=fellowship_of_the_ring,            # principal / headline title
    edition="Extended Edition Trilogy Box Set",
    container="Blu-ray",
    contents=[
        Appearance(work=fellowship_of_the_ring, position=1, disc=1),
        Appearance(work=two_towers,             position=2, disc=2),
        Appearance(work=return_of_the_king,     position=3, disc=3),
    ],
)
```

When the box has no headline (a true anthology — three unrelated short films,
a label sampler), create a single Work to act as the headline:

```python
sampler_work = Work(title="Indie Label Sampler 2024",
                    media_type=MediaType.MUSIC, year=2024,
                    variant_kind=VariantKind.COMPILATION)
sampler = Release(work=sampler_work, contents=[...])
```

`tracklist` on `Work` and `contents` on `Release` solve different problems:

| Use case | Where it lives |
|---|---|
| Album tracklist (canonical track order on the work) | `Work.tracklist` |
| DJ mix track ordering with `offset`s (single continuous Release) | `Work.tracklist` with `Appearance.offset` |
| Box set aggregating *separate* Works (films, albums, novels) | `Release.contents` |
| Anthology Release with no canonical "host" Work | `Release.contents` + a synthetic anthology Work |

---

### 8.18 Format, quality, rights, and availability

The Release fields split into four orthogonal blocks:

**Format axes** (`container`, `codec`, `bitrate`, `platform`) — what physically
or digitally ships. Replaces the old overloaded `source_format`. A Blu-ray of
a film is `container="Blu-ray", codec="H.264"`. A FLAC rip is
`container="Digital", codec="FLAC", bitrate="24/96"`. A SNES ROM is
`container="ROM", platform="SNES"`. An Alexa Skill is
`container="Skill", platform="Alexa Skill"`.

**Quality axes** (`resolution`, `hdr`, `audio_channels`, `sample_rate`) —
fidelity. Enables "play me the highest-quality release" without string-parsing
container or bitrate.

**Localisation** (`region`, `audio_language`, `subtitle_languages`) — the
dub/sub/market triple. Distinct from `VariantKind.REGIONAL` (editorial
differences only).

**Rights and availability** (`license`, `region_locked`, `regions_available`,
`available_from`, `available_until`) — typed rather than buried in `extra`.
Covers public-domain editions, Creative-Commons releases, region-locked
streams, and "leaves Netflix on 2026-01-31" workflows.

`license` is a free string with conventional values
(`"all_rights_reserved"`, `"public_domain"`, `"cc_by"`, `"cc_by_sa"`,
`"cc0"`, `"cc_by_nc"`, `"gpl"`, etc.). A typed enum is rejected because the
license catalogue is too large and consumer-specific to lock down.

---

### 8.19 Multiple episode orderings

A single TV season often has several legitimate episode orderings:

- *Production* order — the order episodes were filmed
- *Broadcast* order — the order they aired (often shuffled by the network)
- *Chronological* order — the order events happen in-universe
- *Recommended* viewing order — fan or creator-suggested (Star Wars
  "Machete order")

`Work.episode` is the single default ordering. `Work.episode_orderings: Dict[str, int]`
carries alternatives:

```python
ep = Work(
    title="Firefly: Serenity",
    media_type=MediaType.TV,
    series_title="Firefly",
    season=1,
    episode=11,                            # Fox broadcast order
    episode_orderings={
        "broadcast": 11,
        "production": 1,                   # was actually the pilot
        "chronological": 1,
        "recommended": 1,                  # creator-recommended viewing order
    },
)
```

The keys are free strings. The `episode` field always mirrors one of the
orderings — the consumer's default. Separate Works are not created for
alternative orderings; the Work is the same episode regardless of where it
sits in a viewing list.

---

## 9. Open questions

Questions 1, 3, 5, and 7 are resolved in the spec body. Questions 2, 4, and 6 remain
open for v1.0 decision.

1. ~~**Work→work relations (§6):** Deferred to v1.1. Stored in `Work.extra` for now;
   a `WorkRelation` model will be added once consumers demonstrate divergence.~~ **Resolved.**

2. **Tracklist on Work vs Release:** Currently `tracklist: List[Appearance]` is on
   `Work`. An argument exists for moving it to `Release` only, since track ordering
   can differ between editions (bonus tracks, regional variants). Counter-argument:
   the canonical track order is a property of the work, not the release. **Unresolved.**

3. ~~**Channel/station as Work vs Entity:** A radio station is modelled as a Work with
   `stream_mode = CONTINUOUS`; a broadcaster (BBC, NBC) is an Entity with
   `EntityKind.ORGANISATION`. These are distinct: the station is a broadcast service (something
   you listen to), the network is the organisation that runs it.~~ **Resolved in §5.5.**

4. **`content_genres` as string vs typed enum:** Currently a free `List[str]` with
   well-known constants in `genre.py`. A typed enum would enable validation and schema
   generation but requires ongoing additions. A registry pattern (validated against a
   known set, extensible) may be a middle ground. **Unresolved.**

5. ~~**Multi-language `aka`:**~~ **Resolved.** `Work.aka` remains `List[str]`
   for plain alternative spellings; `Work.localized_titles: List[Tuple[str, str]]`
   carries language-tagged titles for cross-locale matching. Both are excluded
   from the identity hash.

6. **`external_ids` as `Dict[str, str]` vs a typed model:** A typed model provides IDE
   completion and validation but requires mediavocab to enumerate every external database.
   Current decision: `Dict[str, str]` with key constants in `models/external_ids.py`.
   Typed model (like metadatarr's `ExternalIds`) remains a consumer responsibility.
   **Partially resolved; key constants file added to package structure.**

7. ~~**Adult/explicit content modelling:**~~ **Resolved in §8.3.** GENRE_ADULT covers
   the content flag. Scene-level Work, performer Entity, studio/platform patterns, and
   adult database `external_ids` keys are documented in §8.3.

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
