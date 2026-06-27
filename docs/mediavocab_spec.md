# mediavocab — Formal Specification

**Version:** 1.0
**Status:** Stable. See §8 for versioning policy.
**Scope:** Vocabulary and data-model library for any software that catalogues,
resolves, plays, or recommends media content.

---

## 1. First principles

### 1.1 The problem

Every project that touches media content independently re-defines the same
vocabulary: what kinds of media exist, who participates in them, how editions
relate to canonical works, how band members come and go. The definitions are
subtly incompatible, which makes cross-project data exchange painful and turns
small differences load-bearing in the wrong places — a missing season number
breaks dedup, a stray "Director's Cut" string forks the catalogue.

`mediavocab` defines these concepts once, prescriptively. It provides the
shared data model; consuming packages provide the application logic —
resolving, scraping, playing, recommending.

### 1.2 Two views: human and machine

A media object has two identities at once. To a machine it is a schema row
with an ID — an ISRC, an IMDB number, a file path. To a human it is a memory,
a mood, a category, a thing someone shared. Both are real; neither is the
correct view; a vocabulary that collapses one into the other will be wrong
for half its users.

mediavocab carries both on purpose. The model splits, on every field, what is
machine-stable from what is human-mutable, and forbids mixing.

### 1.3 Three independent things

Creative artefact, physical manifestation, and contributing participant vary
independently. The same film exists across many discs, broadcasts, and
streams; the same band stars on many records; the same recording is reissued
under many editions. A vocabulary that conflates any two of these will
struggle to model splits, compilations, reissues, mirrors, or lineup changes.

The model therefore names three concrete things, each with its own identity:

- **Work** — the canonical creative artefact. The song *Battery*. The film
  *Alien*. An individual episode of *Doctor Who*. A radio station. A book.
  A game.
- **Release** — a specific manifestation of a Work. The original 1986 CD
  pressing of *Master of Puppets*; the 2016 remaster; a Spotify stream; a
  4K Blu-ray. One Work has many Releases.
- **Entity** — anything that *participates in* a Work without being one: a
  person, a band, a record label, a publisher, a series container, a smart
  speaker.

### 1.4 Six models close the graph

Three further models describe how the three identities connect:

- **Appearance** — the position of a Work inside a container Release (track
  5 on the album, episode 12 of the season, issue 4 in a story arc).
- **Credit** — an Entity's contribution to a specific Work (Cliff Burton
  played bass on *Master of Puppets*).
- **Membership** — an Entity's time-sliced presence in a group Entity
  (Cliff Burton was in Metallica from 1982 to 1986).

That is the whole object graph. Everything else in the spec — taxonomy enums
and text utilities — exists to describe, identify, route, or compare instances
of these six models.

### 1.5 Identity, routing, description

Each field on each model belongs to exactly one of three families. Keeping
them apart is what prevents the recurring failure where a genre gets jammed
into MediaType, a routing hint gets hashed as identity, or an enrichment is
treated as a conflict.

- **Identity** — fields whose disagreement means *this is a different
  thing*. Title, year, runtime, type, edition. These feed `work_hash` and
  `release_hash`. After canonicalisation they are immutable; a record that
  differs on an identity field is a different record.
- **Routing** — fields that gate which providers to consult, which pipeline
  to dispatch to, which UI surface to render in. Playback type, content
  genres, programme format. Excluded from hashes. Freely changeable.
- **Description** — fields that accumulate as more sources contribute.
  Credits, tracklist, accessibility tracks, `external_ids`, `extra`. A new
  provider supplying a value is enrichment, not conflict.

The taxonomy of values (§3) follows the same split: identity axes, routing
axes, and description fields on the models.

### 1.6 Intended consumers

- Metadata resolution libraries
- Media scrapers and archivers
- Media players and streaming clients
- Recommendation engines, deduplication pipelines, library managers

### 1.7 Non-goals

- Provider API clients
- Playback routing or intent classification
- Persistence, deduplication, or ID allocation
- NLU or voice-assistant logic
- Any business logic specific to one consumer

---

## 2. Axioms and theorems

§3 (axes) and §4 (labels) appeal to the rules below. Every enum value cited
later carries a reference to the axiom or theorem that admits it.

### 2.1 Axioms

**A1 — Schema-or-database admission for `MediaType`.**
A `MediaType` value earns its place when at least one of the following holds,
and no orthogonal axis would fit:
- (a) the mandatory-field schema differs from every existing type;
- (b) the authoritative external databases (canonical identifier spaces such
  as ISRC, ISBN, IFDB ID, etc.) are disjoint from every existing type's; or
- (c) the comparison tolerances diverge from every existing type's.

Two kinds that share schema, databases, and tolerances are the same type —
genre tags distinguish them.

**A2 — Absence is not a value.**
*Standard edition* means `variant_kind = None`, not `variant_kind = STANDARD`.
*Ongoing membership* means `date_to = None` combined with `temporal = ACTIVE`.
Never add an enum value to mark the absence of a distinction.

**A3 — Delivery is not identity.**
A livestream of a radio station is not a different kind of content from the
station — it is a Release with a streaming URI. `MediaType` describes what a
work IS, not how it is delivered. Physical playback devices, codecs,
containers, resolutions, and bitrates are properties of the Release, never
of the Work.

**A4 — One Work, one `MediaType` for life.**
A Work has a single `MediaType` value, committed at construction. Two
distribution channels of the same artefact produce two `Release`s of one
Work — not two Works. If a single recording has materially different schemas
in two channels (an ASMR ISRC release on a label and the same recording on
an RSS feed), it is two Works linked by `WorkRelation(DERIVED_FROM)`. The
classifier must commit to one type before a Work exists.

**A5 — Membership is temporal and has a status (orthogonal pair).**
`date_to = None` does NOT mean *current member*. A defunct band's last-known
member has `date_to = None` and `temporal = INACTIVE_GROUP`. Temporal state
and membership kind are orthogonal and must both be stored.

**A6 — Routing axes are orthogonal to identity.**
A concern that doesn't change the schema earns a typed field (typically a
ClassVar on the provider and an optional hint on the resolver bag), not a
`MediaType` value. Routing axes are absent from `work_hash` and
`release_hash`. Identity is `(media + identity-fields)`; the resolver gate
is three-axis: `(media × playback_type × genre_filter)`. `content_form` was
removed *from the resolver gate* — no real provider filters on it, and it
added gate complexity with no benefit. It is **not** removed from the model:
`content_form` remains a typed field on `Work` and `Signals` and is an
identity-hash input via A8b (a trailer must not collide with the primary
work). The distinction is deliberate — `content_form` routes nothing at the
gate, yet still separates identity once a `Work` exists.

**A7 — One source of truth per fact.**
If a value has a typed home, the provider populates that. The same value
must not also appear as a relation, an `extra` key, or a free string
elsewhere in the same record. Double-writing produces silent conflicts and
inflates merge scores.

**A8 — Human distinction → typed field, on a threshold.**
When humans systematically treat two records as different things, and no
combination of existing identity fields separates them, the distinction
earns its own typed field. The bar is restrictive: "humans sometimes call
this differently" is not enough (that is `aka`); "humans treat these as
separate things and the catalogue would silently collide them" is.

A8 has two consequences, applied in order:
- **A8a (typed field).** The distinction earns a typed field. The field's
  family (identity / routing / description) is determined by whether
  collision *would* happen without it.
- **A8b (hash inclusion).** The typed field enters the identity hash when —
  and only when — its absence would cause two records with disjoint human
  meaning to share a digest. The field is otherwise routing or description.

`ContentForm` is admitted by A8a; it enters `work_hash` (§6.3) by A8b
because `(title, year, media_type)` cannot separate a trailer from the
primary work.

**A9 — A relation kind earns its place.**
A `RelationRole`, `WorkRelationKind`, or `ReleaseRelationKind` value is
admitted only when both of the following hold:
- (a) the connection it expresses is **not already implied by an identity
  field**. `season` / `episode` / `series_title` already place an episode
  within its series; a relation that restates that double-writes (A7) and
  inflates merge scores. A relation earns its place only when it carries a
  link the fields cannot — typically an edge from one Work/Release/Entity to
  a *different* one.
- (b) it is **not subsumed by an existing relation kind of the same
  family**. A more specific kind is admitted only when consumers
  systematically traverse it as a distinct edge (the A8 threshold):
  "humans sometimes name it differently" is not enough; "consumers navigate
  it differently, and conflating it with the existing kind would merge two
  real links" is.

Relation kinds are navigation and description, never identity — they are
absent from `work_hash` and `release_hash` (A6), so this axiom is about
non-redundancy, not hashing. Two relations pointing the same direction with
the same navigational meaning are the same relation. The same admission
discipline A1 gives `MediaType` and A8 gives typed fields, A9 gives the
relation enums — without it the relation vocabulary sprawls.

`EPISODE_OF` is rejected by A9(a): episode membership is already carried by
the `season` / `episode` / `series_title` identity fields. A *channel* is
rejected as a `RelationRole` for a different reason — it is an Entity (a
Work, per T4), not a way an entity participates — so it never reaches A9.

### 2.2 Theorems

Each theorem is a direct consequence of the axioms; the citation says which.

**T1 — Genre is not type.** (← A1)
*Documentary* is a film with a non-fiction treatment; *anime* is TV with a
cultural origin; *noir* is an aesthetic. None changes the schema, the
authoritative databases, or the comparison tolerances enough to warrant a
separate `MediaType`. `content_genres` carries them.

**T2 — Work ≠ Release ≠ Appearance.** (← §1.3 decomposition)
*Battery* (the song), *Master of Puppets* (the album), and its position as
track 1 are three distinct concepts. Conflating them makes splits,
compilations, reissues, and mirrors impossible to model.

**T3 — Band roster ≠ release lineup.** (← A3, three-thing decomposition)
Who is currently *in* a band is different from who *played on* a specific
album. Producers, session musicians, and guest vocalists contribute to a
Release but are not members of the band Entity.

**T4 — A station is a Work.** (← A3, three-thing decomposition)
A radio station or TV channel has stable cataloguable identity, multiple
stream URLs (mirrors, bitrates, transmitters), and cross-references across
providers exactly like a film. The station is the Work; its stream URLs
are Releases.

**T5 — Credit structure is schema.** (← A1)
A work requiring a cast, a director, and a sound designer has a different
schema from one requiring a single narrator. That difference warrants a
distinct `MediaType` — the test that admits `AUDIO_DRAMA` next to
`AUDIOBOOK`.

**T6 — Technical attributes are Release fields.** (← A3)
Colour, aspect ratio, frame rate, audio-channel count, codec, container,
bitrate, resolution describe the manifestation, not the canonical work.
Two editions of the same Work can differ on every one without changing
identity.

**T7 — `MediaType` follows distribution schema.** (← A1)
A rap track is `MUSIC` because it has an ISRC and appears in music
databases — not because it contains melody. An ASMR recording is `MUSIC`
if distributed through a label, `PODCAST` if distributed via RSS.
`content_genres` handles the aesthetic; `MediaType` handles the schema.

**T8 — Pipeline sentinels never reach a canonical Work.** (← A4)
The classifier may report `MediaType.GENERIC`, `NOT_MEDIA`, or `CONTROL`
during resolution. A `Work` constructed with any of these raises at
validation. By the time a Work exists, the classifier has committed.

**T9 — A channel / feed is an Entity or a Work, never a relation role.** (← T4, A9)
A YouTube channel, podcast feed, or radio/TV station is a *publishing
container*, not a way an entity participates in a work. When it has stable
cataloguable identity with playable streams it is a Work (T4 — a station is a
Work, its stream URLs are Releases); otherwise it is an Entity (an
`OrganisationKind`, e.g. `BROADCASTER` or `NETWORK`). Its link to content is
expressed through an existing `RelationRole` such as `PUBLISHER` or `CREATOR`,
or through a Work/Entity reference — never a bespoke `CHANNEL` role, which A9
would reject as not-a-participation. This is why `RelationRole` has no
`CHANNEL` value.

---

## 3. Axes

A media record is described along axes. Each has a typed home, lives at a
specific layer of the model, and carries one of three families (identity,
routing, description).

### 3.1 The layered axis table

| Layer              | Axes                                                            | Family      |
|--------------------|-----------------------------------------------------------------|-------------|
| Work-identity      | `MediaType`, `ContentForm`, `VariantKind`                       | identity    |
| Work-routing       | `content_genres`, `programme_format`, `picture_format`          | routing     |
| Release-identity   | `region`, `container`, `codec`, `bitrate`, `platform`, `resolution`, `audio_language` | identity |
| Release-routing    | `StreamMode`                                                    | routing     |
| Release-packaging  | `ReleasePackaging`                                              | description |
| Release-rights     | `license` (SPDX string)                                         | description |
| Derived            | `PlaybackType`, `Structure` (functions of `MediaType`)          | routing     |

Identity axes hash; routing axes gate dispatch; description axes accumulate.
No axis appears in two layers.

### 3.2 `MediaType` — schema axis

What schema, what databases, what tolerances. Carried on `Work.media_type`
for the Work's lifetime (A4). Values admitted by A1's three-clause test.
Enumerated in §4.1.

### 3.3 `ContentForm` — experiential axis

Whether a Work is a primary creative artefact or supplementary to one. A
trailer for *Inception* is `MOVIE + ContentForm.TRAILER`; a reaction video
covering an anime episode is `EPISODIC_SERIES + REACTION` with
`WorkRelation(BONUS_FOR=parent)`. Orthogonal to schema and to genre — a
trailer for a podcast is `PODCAST + TRAILER`.

ContentForm is the one human-perception axis admitted to identity, by A8: a
trailer for *Inception* and the film *Inception* have the same title, year,
and `MediaType`. Without form in `work_hash` they would collide.

### 3.4 `VariantKind` — restructuring axis (Work-only)

Why a Work differs from a canonical sibling. Theatrical, director's cut,
extended, fanedit, tv-to-movie, movie-to-tv, remastered, upscaled,
colorized, preservation, compilation. The only difference between official
and fan cuts is the producer; the model treats both uniformly.

Each cut is a distinct `Work` linked to siblings via `WorkRelation`
(`FANEDIT_OF`, `DERIVED_FROM`, `ADAPTED_FROM`). A multi-cut Blu-ray box set
is one `Release` whose `contents` lists every cut. `Release` has no
`variant_kind`.

`None` is the canonical / default form (A2).

### 3.5 `ReleasePackaging` — packaging axis

How a Release is packaged independently of which Works it carries: deluxe,
reissue, regional, bootleg, box-set, single. Lives on `Release.packaging`.
Description-family (§1.5) — packaging does not change which artefact is being
shipped, only how it is shipped.

### 3.6 `content_genres` — aesthetic axis

Free-string list of canonical genre tags. Open vocabulary because genre is
culturally negotiated and inherently extensible. Genre is *what the
experience is like*, never *what kind of thing it is* (T1). Routing-family
(A6) — providers may declare a `genre_filter` ClassVar; identity hashes
exclude genres.

### 3.7 `ProgrammeFormat` — programme-format axis

Programme *format* rather than aesthetic flavour: concert, stand-up
comedy, talk show, reality, news, sports. Lives on
`Work.programme_format: Optional[ProgrammeFormat]`. Routing-family
(A6) — distinct from `content_genres` because real-world databases
treat format as a structural facet, not a flavour.

### 3.8 `PlaybackType` — derived player-surface axis

What player surface a Work needs. Derived from `MediaType` via
`infer_playback_type()`; never persisted on `Work` or `Release` (A6, A7).
A consumer may override by passing `playback_type` on the resolver bag.

### 3.9 `StreamMode` — delivery axis

How the Release is delivered at playback time: on-demand, live, continuous.
A property of the Release, never of the Work (A3). A live concert stream
becomes on-demand when archived without the underlying Work changing.

### 3.10 `license` — rights axis

`Release.license: str` is an SPDX-style identifier (`"CC-BY-SA-4.0"`,
`"all_rights_reserved"`, `""` for unknown). Helper predicates
(`license.is_open()`, `license.is_public_domain()`,
`license.requires_attribution()`) operate on the string. No parallel typed
view (A7).

### 3.11 `PictureFormat` — presentation/picture-attribute axis

The colour, dimensionality, and resolution of a presentation: black-and-white,
silent, colorized, colour, 2d, 3d, sd, hd, 4k, widescreen, imax. A technical
attribute of the manifestation (T6) — two editions of the same Work can differ
on it without changing identity. Routing-family (A6); excluded from `work_hash`,
`release_hash`, and `compare_signals`.

Distinct from the free-text `source_format`, which names the *distribution
container / capture medium* ("Blu-ray", "Vinyl", "35mm"): a Blu-ray can ship a
black-and-white silent film, and a 4K stream can carry a colorized restoration.
`source_format` stays free text (metadatarr populates it for the container);
`PictureFormat` is the typed presentation enum. Carried on
`Work.picture_format` and `Release.picture_format` (both `Optional`, A2 default
`None`), and as the `Signals.picture_format` routing hint.

### 3.12 `Structure` — derived temporal-shape axis

How a Work is shaped in time: a single self-contained unit, a series of discrete
instalments (`episodic`), an unbounded live/looping stream (`continuous`), or an
ordered set of members (`collection`). Derived from `MediaType` via
`infer_structure()`; never persisted on `Work` or `Release` (A6, A7) — the same
derived-axis pattern as `PlaybackType` (§3.8). Routing-family (A6). A trained
classifier MAY override the leaf default per-utterance (e.g. "play the *album*"
→ `COLLECTION`).

---

## 4. Labels

Every enum value cites the axiom or theorem that admits it. Rejected
candidates follow each enum.

### 4.1 `MediaType`

**Inclusion criterion (A1):** the candidate requires a different
mandatory-field set, is catalogued in disjoint authoritative databases, or
has different comparison tolerances from every existing type.

```python
class MediaType(str, Enum):
    MOVIE               = "movie"
    SHORT_FILM          = "short_film"
    EPISODIC_SERIES     = "episodic_series"
    TV                  = "tv"
    MUSIC               = "music"
    MUSIC_VIDEO         = "music_video"
    PODCAST             = "podcast"
    AUDIOBOOK           = "audiobook"
    AUDIO_DRAMA         = "audio_drama"
    RADIO               = "radio"
    BOOK                = "book"
    COMIC               = "comic"
    GAME                = "game"
    INTERACTIVE_FICTION = "interactive_fiction"
    SOUND_EFFECT        = "sound_effect"
    PROCEDURAL_AMBIENT  = "procedural_ambient"
    PLAYLIST            = "playlist"

    # Pipeline sentinels — rejected at Work construction (T8)
    GENERIC             = "generic"
    NOT_MEDIA           = "not_media"
    CONTROL             = "control"
```

**`MOVIE`** *(admitted by A1(a)(b))* — Feature-length narrative film with a
theatrical or theatrical-class release pipeline. Schema: title, director,
cast, runtime (≥40 min by convention), theatrical release date, IMDB/TMDB
IDs, production country. Documentaries, animated films, and adult films
all sit here with an appropriate `content_genres` tag — they share
IMDB/TMDB identity space and theatrical-class economics.

**`SHORT_FILM`** *(A1(b)(c))* — Festival-circuit short film. Disjoint
authoritative databases (Sundance Shorts, Cannes Court Métrage,
Clermont-Ferrand, Vimeo Staff Picks, shortoftheweek), separate award lists,
festival premiere date instead of theatrical release date, runtime ≤ 40 min
by convention, precise comparison tolerance (5 s, vs MOVIE's 120 s).

**`EPISODIC_SERIES`** *(A1(a)(b))* — On-demand episodic video: anime, drama,
sitcoms, web series, streaming originals. Anything with ordered episodes
the viewer can pause, resume, and binge. Schema: series title, season,
episode number, network, first air date, TVmaze/TVDB IDs.

**`TV`** *(A1(b)(c), T4)* — Live linear / IPTV broadcast channels. The
channel is the Work, identified by the broadcaster, not by programmes
airing on it. Cannot skip ahead — schedule is publisher-controlled,
content is continuous. Distinct from `EPISODIC_SERIES` by databases (IPTV
M3U / EPG / DVB identifiers) and tolerance (runtime 0, schedule-driven).

**`MUSIC`** *(A1(a)(b)(c), T7)* — Audio recording distributed through
music pipelines. Schema: artist, album, track number, ISRC, duration,
MusicBrainz recording ID, label. Runtime tolerance ±3 s. Criterion is
distribution schema, not audio content (T7).

**`MUSIC_VIDEO`** *(A1(a)(b)(c))* — Promotional or performance video for a
musical work. Director field (distinct from MUSIC), different providers
(Vevo, YouTube Music), runtime tolerance ±30 s.

**`PODCAST`** *(A1(b))* — Episodic non-music audio distributed via RSS or a
podcast platform. Schema: host, show title, episode GUID, RSS feed URL,
Podcast Index / Apple Podcasts IDs.

**`AUDIOBOOK`** *(A1(a)(b), T5)* — Complete narrated literary work read by
a single narrator. Schema: author, narrator, chapter count, ISBN-derived
IDs, Audible/LibriVox IDs. Distinct from AUDIO_DRAMA by credit structure
(single narrator vs cast).

**`AUDIO_DRAMA`** *(A1(a)(b), T5)* — Fully performed audio production with
a cast, director, and sound design. Schema: cast (multiple actors),
director, sound designer, screenwriter, production-company IDs (Big
Finish, BBC Sounds, Audible Originals).

**`RADIO`** *(A1(b)(c), T4)* — Live linear audio broadcasting: stations and
channels. The audio counterpart to `TV`. Station is a Work with
`episode = None`, `runtime = None`; its stream URLs (mirrors, bitrates,
DAB vs web) are Releases. Distinct databases (radio-station directories,
RDS PI codes) and Release shape (audio codec/bitrate, no video).

**`BOOK`** *(A1(a)(b))* — Text-based written work: prose fiction,
non-fiction, poetry collections, essays, short-story anthologies. Schema:
ISBN, author, publisher, page count, edition, OpenLibrary/Goodreads IDs.
An ebook is a Release with `container = "EPUB"` or `"PDF"`. Comic books
and graphic novels are COMIC.

**`COMIC`** *(A1(a)(b))* — Sequential art: single issues, graphic novels,
manga, manhwa, manhua, webcomics, comic strips. Schema: issue/chapter,
story arc, variant cover flag, publisher series, ComicVine / GCD /
MangaDex IDs. `episode` carries issue/chapter; `season` carries volume;
`series_title` carries the run title.

**`GAME`** *(A1(a)(b))* — Interactive software. Schema: platform,
developer, publisher, IGDB/RAWG IDs. Exists so resolvers can route the
verb *"play"* — the only verb shared across every media type — to the
right pipeline.

**`INTERACTIVE_FICTION`** *(A1(a)(b))* — Text- or voice-driven branching
narrative software: parser-based (Infocom, Inform 7), choice-based
(Twine, ChoiceScript), voice-driven (Alexa Skills, Google Actions).
Distinct from GAME because the database axis splits: GAME records belong
on IGDB/MobyGames/Steam; IF records belong on IFDB.org and ifiction.org.

**`SOUND_EFFECT`** *(A1(a)(b)(c))* — A discrete catalogued audio clip whose
identity is a *category taxonomy*, not an artist or album. Schema:
category hierarchy, precise runtime (0 s tolerance), source-library IDs
(freesound.org, BBC Sound Effects, ZapSplash, Soundsnap). Mandatory schema
diverges from MUSIC (no artist, no ISRC).

**`PROCEDURAL_AMBIENT`** *(A1(a)(b))* — Procedurally generated,
parameterised, or looping-preset ambient audio. Defining test:
**registry membership in a generator platform** (myNoise, Moodist, Noisli,
Endel) AND **no ISRC**. Identity is the *generator preset*, catalogued in
a dedicated platform database (myNoise scene IDs, Moodist preset IDs,
Noisli mix IDs, Endel scene IDs). Runtime is user-controlled.

Looped recordings count: even when the underlying source is a single
recorded loop on repeat, the *playback experience* is parameterised and
there is no ISRC binding the artefact to a music catalogue.
`StreamMode.CONTINUOUS` is a playback choice on a Release, not a MediaType.

**`PLAYLIST`** *(A1(a)(b))* — User-curated cross-media-type collection:
Spotify playlists, YouTube playlists, M3U files, OPML podcast bundles.
Constituent Works keep their own MediaType. Schema: `tracklist` of
`Appearance`s, `Credit` for the curator with `RelationRole.CURATOR`,
distinct external databases (Spotify Playlist API, YouTube Playlist API).

Playlists are the deliberate exception to *Work = canonical artefact*.
Identity is anchored at the **source** — the `external_ids` entry pointing
at the upstream playlist record. The same playlist may be reordered or
have tracks added/removed without becoming a different Work; the
source-side ID is stable. A standalone `.m3u` with no upstream source
inherits identity from the file path; consumers needing content-based
dedup hash `(title, [appearance.work.external_ids for ...])` themselves.

#### Decision tree: MUSIC vs SOUND_EFFECT vs PROCEDURAL_AMBIENT

Apply in order — first match wins:

1. Has an ISRC (or MusicBrainz/Discogs ID) → **`MUSIC`**.
2. Catalogued in a generator-platform database (myNoise, Moodist, Noisli,
   Endel) → **`PROCEDURAL_AMBIENT`**.
3. Discrete finite recording catalogued in a sound-effect library
   (Freesound, BBC Sound Effects, Soundsnap, ZapSplash) → **`SOUND_EFFECT`**.
4. Otherwise short (≤ 60 s) and category-tagged → **`SOUND_EFFECT`**.

#### Pipeline sentinels

`GENERIC`, `NOT_MEDIA`, and `CONTROL` are resolver-side states that share
the `MediaType` namespace so dispatch tables stay exhaustive over a single
enum (T8). A `Work` constructed with any of them raises at validation.

- `GENERIC` — *this is media, but the kind is unresolved*. Transient.
- `NOT_MEDIA` — *this query is positively not a media intent*. Terminal.
  Factual questions (*"when is a director's birthday"*), pure
  device-control on non-media devices (*"turn off the lights"*), calendar
  / reminders, entity-info queries (*"who starred in X"*).
- `CONTROL` — a playback-control verb (*"pause"*, *"skip"*, *"volume up"*,
  *"seek to 3:00"*). Acts on the current session, not on a queryable
  Work. Terminal. Carried separately from `NOT_MEDIA` because downstream
  players route these to a session controller.

#### Rejected `MediaType` values

| Rejected           | Reason                                                                  |
|--------------------|-------------------------------------------------------------------------|
| `DOCUMENTARY`      | Programme format (`ProgrammeFormat.DOCUMENTARY`); same schema as MOVIE/TV. |
| `ANIME`            | Cultural category of animation. Same schema as TV/MOVIE.                |
| `CARTOON`          | Production technique. Same schema as TV/MOVIE.                          |
| `NEWS`             | Programme format. Distributed as TV, RADIO, or PODCAST.                 |
| `AUDIO` / `VIDEO`  | Signal types, not content.                                              |
| `LIVESTREAM`       | Delivery (A3). A livestream is a Release with `StreamMode.LIVE`.        |
| `ADULT`            | Content rating, orthogonal to type. Use `content_genres=["adult"]`.     |
| `HENTAI`           | Anime (genre) + adult (rating). Two tags, not a type.                   |
| `ASMR`             | Genre tag. MUSIC or PODCAST by distribution.                            |
| `TRAILER`          | `ContentForm.TRAILER`.                                                  |
| `BEHIND_THE_SCENES`| `ContentForm.BEHIND_SCENES`.                                            |
| `REACTION`         | `ContentForm.REACTION` with `WorkRelation(BONUS_FOR)`.                  |
| `SOCIAL_CLIP`      | `ContentForm.SOCIAL_CLIP`.                                              |
| `AUDIO_DESCRIPTION`| Accessibility track on existing content (`AccessibilityTrack`).         |
| `SILENT_MOVIE`     | MOVIE + `audio_present = False` on Release (T6).                        |
| `BLACK_WHITE_MOVIE`| MOVIE + `color = False` on Release (T6).                                |
| `RADIO_THEATRE`    | `AUDIO_DRAMA` + `content_genres=["radio_drama"]`.                       |
| `CONCERT`          | Programme format (`ProgrammeFormat.CONCERT`).                           |
| `STAND_UP`         | Programme format (`ProgrammeFormat.STAND_UP`).                          |

### 4.2 `ContentForm`

```python
class ContentForm(str, Enum):
    PRIMARY       = "primary"        # the canonical work itself (default)
    TRAILER       = "trailer"
    TEASER        = "teaser"
    EXCERPT       = "excerpt"
    BEHIND_SCENES = "behind_scenes"
    REACTION      = "reaction"
    SOCIAL_CLIP   = "social_clip"
    SUPPLEMENT    = "supplement"     # commentary tracks, audio descriptions, lyric videos
    OTHER         = "other"
```

A Work is `PRIMARY` unless its very reason for existing is supplementary to
another Work, in which case it carries a non-PRIMARY form *and* a
`WorkRelation(BONUS_FOR=parent)`. ContentForm earns its place when the
experiential relationship to a primary work is fundamentally different —
short vs full is *not* a form (runtime), live vs recorded is *not* a form
(`StreamMode`), kid-friendly is *not* a form (audience).

ContentForm is the one human-perception axis admitted to identity (A8).
It enters `work_hash` (§6.3) and is immutable after canonicalisation (§8.2).

### 4.3 `VariantKind`

**Inclusion criterion:** the variant changes something detectable in the
canonical artefact (runtime, narrative structure, scene order, mix, visual
treatment), is catalogued as a distinct entry in at least one major
database OR is produced by a recognised editorial / restoration process,
and produces a *new Work* per §3.4.

```python
class VariantKind(str, Enum):
    # Cuts — official or fan, the model treats both uniformly
    THEATRICAL   = "theatrical"
    DIRECTORS    = "directors"
    EXTENDED     = "extended"
    FANEDIT      = "fanedit"

    # Cross-MediaType structural transformations
    TV_TO_MOVIE  = "tv_to_movie"
    MOVIE_TO_TV  = "movie_to_tv"

    # Restoration and technical enhancement
    PRESERVATION = "preservation"
    COLORIZED    = "colorized"
    REMASTERED   = "remastered"
    UPSCALED     = "upscaled"

    # Derived aggregations
    COMPILATION  = "compilation"

    OTHER        = "other"
```

**`THEATRICAL`** — Marker for the theatrical cut when a director's cut also
exists. Without a counterpart, `variant_kind = None` is preferred (A2).

**`FANEDIT`** — Foundation-level catch-all for fan-made narrative
restructurings. Downstream packages may sub-classify.

**`TV_TO_MOVIE` / `MOVIE_TO_TV`** — Structural transformations that change
narrative structure and cross the `MediaType` boundary. By A4 the result
is a new Work; the link to source is `WorkRelation(ADAPTED_FROM)` or
`WorkRelation(FANEDIT_OF)`.

**`PRESERVATION`** — Reconstructs content from degraded or partially lost
source material, sometimes resulting in an incomplete work. Distinct from
REMASTERED.

**`REMASTERED`** — New mastering from existing source elements.

**`UPSCALED`** — No new source elements, purely computational. Relevant
for libraries tracking source-quality provenance.

**`COMPILATION`** — A derived Work aggregating content from multiple other
Works (a "best of" album-as-Work, an anthology Work). Not a re-packaging
of a single Release — for that see `ReleasePackaging`.

#### Rejected `VariantKind` values

| Rejected                  | Reason                                                   |
|---------------------------|----------------------------------------------------------|
| `STANDARD` / `ORIGINAL`   | Absence of a variant (A2). `variant_kind = None`.        |
| `DELUXE` / `REISSUE` / `REGIONAL` / `BOOTLEG` | Packaging, not restructuring. See `ReleasePackaging` (§4.4). |
| `FANFIX` / `FANMIX`       | IFDB-specific sub-types. Too narrow for foundation.      |
| `BONUS_TRACKS`            | A property of DELUXE packaging, not a Work-level variant.|

### 4.4 `ReleasePackaging`

```python
class ReleasePackaging(str, Enum):
    DELUXE        = "deluxe"          # bonus material added to a standard edition
    REISSUE       = "reissue"         # later commercial re-pressing
    REGIONAL      = "regional"        # region-specific edition (censorship cuts, alternate artwork)
    BOOTLEG       = "bootleg"         # unofficial pressing of a real performance
    BOX_SET       = "box_set"         # multi-Release container
    PROMO         = "promo"           # promotional / not-for-sale
    OTHER         = "other"
```

Description-family (§1.5); `Release.packaging` is excluded from
`release_hash` because the same SKU may be re-labelled across catalogues
without becoming a different Release. `None` is the unmarked default.

`BOOTLEG` lives here because the performance or recording IS real — the
Work is the performance; the Release is the bootleg pressing or tape.

### 4.5 `EntityKind` and `OrganisationKind`

```python
class EntityKind(str, Enum):
    PERSON       = "person"          # any human being
    GROUP        = "group"           # band, ensemble, theatre company, comedy duo
    ORGANISATION = "organisation"    # see OrganisationKind for sub-type
    SERIES       = "series"          # TV franchise, book series, game series, podcast show
    DEVICE       = "device"          # smart speaker, cast target, set-top box, console-as-endpoint
    OTHER        = "other"


class OrganisationKind(str, Enum):
    LABEL             = "label"
    PUBLISHER         = "publisher"
    STUDIO            = "studio"
    BROADCASTER       = "broadcaster"
    DEVELOPER         = "developer"
    STREAMING_SERVICE = "streaming_service"
    DISTRIBUTOR       = "distributor"
    OTHER             = "other"
```

`EntityKind` classifies the *structural type* of an entity — what schema it
needs. A musician and a documentary director are both `PERSON`; their
contributions are captured by `RelationRole` credits, not by `EntityKind`.

`OrganisationKind` discriminates legal entities that share a schema (name,
country, founding year, external IDs) but differ in role within the media
graph. Set when `kind == ORGANISATION`; `None` otherwise (validator
enforced).

**`SERIES` as Entity** (§1.3 decomposition; A3). A series is a *container*, not a Work.
*The Dark Tower* contains seven Books; *Doctor Who* contains hundreds of
episodes. The series has metadata (title, creator, instalment count) but
is not played, read, or watched directly. Modelling it as an Entity allows
`part_of` relations from individual Works to their containing series.

**`DEVICE` as Entity** (A3). A smart plug, Sonos speaker, Chromecast, Kodi
box, or console-as-endpoint is a delivery channel, not a media work. The
*content* delivered is still a Work. Receiver-class devices additionally
have a `Work` counterpart for invocation (§5.6).

### 4.6 `RelationRole`

```python
class RelationRole(str, Enum):
    CREATOR         = "creator"          # generic fallback

    # Music
    PERFORMER       = "performer"
    COMPOSER        = "composer"
    LYRICIST        = "lyricist"
    PRODUCER        = "producer"         # music producer (shapes the sound)
    FEATURING       = "featuring"
    REMIXER         = "remixer"

    # Film and TV
    DIRECTOR        = "director"
    SCREENWRITER    = "screenwriter"
    ACTOR           = "actor"
    CINEMATOGRAPHER = "cinematographer"
    EDITOR          = "editor"

    # Book and comic
    AUTHOR          = "author"
    ILLUSTRATOR     = "illustrator"
    TRANSLATOR      = "translator"
    NARRATOR        = "narrator"

    # Podcast and radio
    HOST            = "host"
    GUEST           = "guest"
    CURATOR         = "curator"          # playlists, anthologies, compilation editors

    # Game
    DEVELOPER       = "developer"
    PORTER          = "porter"

    # Release infrastructure
    PUBLISHER       = "publisher"
    LABEL           = "label"
    DISTRIBUTOR     = "distributor"

    OTHER           = "other"
```

`PRODUCER` here means *music producer* (shapes the sound of a recording).
Film-producer credits are rarely useful for disambiguation and use
`CREATOR` with a `role` note ("Executive Producer", "Line Producer") until
a dedicated value is added.

### 4.7 `CreditSection`

```python
class CreditSection(str, Enum):
    PRINCIPAL = "principal"   # band members / main cast / core authors / primary creators
    GUEST     = "guest"       # featured artists / session musicians / cameos / guest authors
    STAFF     = "staff"       # producer, engineer, editor, cover artist, publisher, distributor
```

Generalises across media types: a film's cast/crew split, a book's
author/editor/publisher split, and a metal album's members/guests/staff
split all use the same three-way taxonomy.

### 4.8 `MembershipKind` and `TemporalState`

```python
class MembershipKind(str, Enum):
    MEMBER   = "member"     # principal member of the group
    TOURING  = "touring"    # touring/live member only; not on studio recordings
    SESSION  = "session"    # session / guest contributor on specific recordings


class TemporalState(str, Enum):
    ACTIVE          = "active"            # membership ongoing
    ENDED           = "ended"             # membership ended; date_to may be known or unknown
    INACTIVE_GROUP  = "inactive_group"    # group is dormant or disbanded; membership state at inactivity preserved
```

Two orthogonal facets (A5). A *current touring member* is
`(kind=TOURING, temporal=ACTIVE, date_to=None)`. A defunct band's last
guitarist is `(kind=MEMBER, temporal=INACTIVE_GROUP, date_to=None)`. A
musician can have multiple `Membership` records for the same band (left
and rejoined).

`MembershipKind.SESSION` covers both session musicians and one-off guest
contributors at the *roster* level. Guest-status at the *recording* level
is `Credit.section=GUEST` on the specific Work — orthogonal scopes, do not
conflate.

### 4.9 `ReleaseStatus`

```python
class ReleaseStatus(str, Enum):
    RELEASED      = "released"
    ANNOUNCED     = "announced"       # confirmed; release date may be unknown
    IN_PRODUCTION = "in_production"   # filming, recording, or development underway
    CANCELLED     = "cancelled"
    WITHDRAWN     = "withdrawn"       # was released, no longer commercially available
    UNKNOWN       = "unknown"
```

`WITHDRAWN` is distinct from `CANCELLED`: the work shipped, then was
pulled. `RUMOURED` is excluded — a rumoured work has no verifiable record
in any authoritative database; it should not be catalogued as a Work at
all.

### 4.10 `StreamMode`

```python
class StreamMode(str, Enum):
    ON_DEMAND  = "on_demand"   # finite, seekable, available at any time (default)
    LIVE       = "live"        # real-time broadcast; may become ON_DEMAND after broadcast
    CONTINUOUS = "continuous"  # infinite or rolling; no defined end
```

A live concert stream starts as `LIVE` and may become `ON_DEMAND` when
archived. A radio station stream is always `CONTINUOUS`. A downloaded
album track is `ON_DEMAND`. The underlying Work does not change (A3).

### 4.11 `PlaybackType`

```python
class PlaybackType(str, Enum):
    AUDIO       = "audio"          # time-paced audio sink
    VIDEO       = "video"          # time-paced audio+video sink
    PAGED       = "paged"          # user-paced visual: book, comic, photo book, slideshow
    INTERACTIVE = "interactive"    # input-driven: game, interactive fiction
    UNKNOWN     = "unknown"
```

Derived from `MediaType` via `infer_playback_type()`; no persisted field
on `Work` or `Release` (A6, A7).

| Playback type | MediaTypes |
|---|---|
| `AUDIO`       | `MUSIC`, `PODCAST`, `AUDIOBOOK`, `AUDIO_DRAMA`, `RADIO`, `SOUND_EFFECT`, `PROCEDURAL_AMBIENT` |
| `VIDEO`       | `MOVIE`, `SHORT_FILM`, `EPISODIC_SERIES`, `TV`, `MUSIC_VIDEO` |
| `PAGED`       | `BOOK`, `COMIC` |
| `INTERACTIVE` | `GAME`, `INTERACTIVE_FICTION` |
| `UNKNOWN`     | `PLAYLIST` (membership-dependent); pipeline sentinels |

A request verb is an ambiguous hint, not a gate. When the caller asserts
`playback_type` explicitly, providers honour it; when unset, the resolver
falls back to `infer_playback_type(media_type)`.

`PAGED` covers everything that advances on user action with no playback
clock — books, comics, photo books, slideshows, paged ebooks.

### 4.12 `ProgrammeFormat`

```python
class ProgrammeFormat(str, Enum):
    CONCERT     = "concert"
    STAND_UP    = "stand_up"
    TALK_SHOW   = "talk_show"
    REALITY     = "reality"
    NEWS        = "news"
    SPORTS      = "sports"
    QUIZ        = "quiz"
    DOCUMENTARY = "documentary"
    OTHER       = "other"
```

Structural programme *format*, distinct from aesthetic genre (T1). Lives
on `Work.programme_format`. Routing-family (A6); excluded from
`work_hash`.

A concert film released theatrically is `MOVIE` with
`programme_format=CONCERT`. A stand-up special on Netflix is
`EPISODIC_SERIES` or `MOVIE` (depending on series structure) with
`programme_format=STAND_UP`. A feature-length documentary is `MOVIE` with
`programme_format=DOCUMENTARY`; a documentary series is `EPISODIC_SERIES`
with the same.

### 4.13 `WorkRelationKind` and `ReleaseRelationKind`

```python
class WorkRelationKind(str, Enum):
    COVERS         = "covers"
    SAMPLES        = "samples"
    ADAPTED_FROM   = "adapted_from"
    SEQUEL_TO      = "sequel_to"
    PREQUEL_TO     = "prequel_to"
    PART_OF        = "part_of"         # ad-hoc thematic / curatorial grouping that is NOT
                                       # a series (use `series_title` + SERIES Entity for series)
                                       # and NOT an album tracklist (use Appearance for those)
    LIVE_VERSION   = "live_version"
    REMIX_OF       = "remix_of"
    SOUNDTRACK_FOR = "soundtrack_for"
    BONUS_FOR      = "bonus_for"
    FANEDIT_OF     = "fanedit_of"      # combine with Work.variant_kind
    DLC_FOR        = "dlc_for"
    EXPANSION_OF   = "expansion_of"
    DERIVED_FROM   = "derived_from"    # generic catch-all; cross-channel reissues, remasters


class ReleaseRelationKind(str, Enum):
    SUPERSEDES   = "supersedes"        # this Release replaces an earlier one
    PORT_OF      = "port_of"           # platform port of a game / IF
    MIRROR_OF    = "mirror_of"         # alternate stream of the same broadcast
    DERIVED_FROM = "derived_from"
```

Most Release-to-Release distinctions are already encoded by the format /
packaging fields plus `release_hash`. `ReleaseRelation` is for explicit
lineage claims a consumer wants to surface ("this remaster supersedes
that one and you should hide the older record").

### 4.14 `content_genres`

Open-vocabulary string list. The constants in `mediavocab/taxonomy/genre.py`
are canonical spellings; consumers may use any string. The closed list
exists so providers agree on common spellings when the genre is known.

```python
# Aesthetic narrative genres
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
GENRE_MUSICAL        = "musical"
GENRE_FAMILY         = "family"
GENRE_NOIR           = "noir"

# Style / cultural origin (animation, regional)
GENRE_ANIMATION      = "animation"
GENRE_ANIME          = "anime"

# Audio aesthetics
GENRE_RADIO_DRAMA    = "radio_drama"
GENRE_ASMR           = "asmr"
GENRE_AMBIENT        = "ambient"
GENRE_SOUNDSCAPE     = "soundscape"
GENRE_NATURE_SOUNDS  = "nature_sounds"
GENRE_WHITE_NOISE    = "white_noise"

# Sound-effect taxonomy
GENRE_SFX_ANIMAL     = "sfx_animal"
GENRE_SFX_NATURE     = "sfx_nature"
GENRE_SFX_MECHANICAL = "sfx_mechanical"
GENRE_SFX_HUMAN      = "sfx_human"
GENRE_SFX_UI         = "sfx_ui"
GENRE_SFX_FOLEY      = "sfx_foley"

# Comics
GENRE_MANGA          = "manga"
GENRE_MANHWA         = "manhwa"
GENRE_MANHUA         = "manhua"
GENRE_WEBCOMIC       = "webcomic"
GENRE_MOTION_COMIC   = "motion_comic"

# Written / spoken word
GENRE_POETRY         = "poetry"
GENRE_SPOKEN_WORD    = "spoken_word"
GENRE_ESSAY          = "essay"
GENRE_SHORT_STORY    = "short_story"
GENRE_EDUCATIONAL    = "educational"

# Photo / image collections
GENRE_PHOTO_BOOK     = "photo_book"
GENRE_SLIDESHOW      = "slideshow"

# Interactive fiction
GENRE_PARSER_IF      = "parser_if"
GENRE_CHOICE_IF      = "choice_if"
GENRE_VOICE_GAME     = "voice_game"
GENRE_BRANCHING      = "branching"

# Music genres (top-level)
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
GENRE_HIP_HOP        = "hip_hop"
GENRE_RNB            = "rnb"
GENRE_SOUL           = "soul"
GENRE_FUNK           = "funk"
GENRE_DISCO          = "disco"

# Music sub-genres (electronic)
GENRE_HOUSE          = "house"
GENRE_TECHNO         = "techno"
GENRE_TRANCE         = "trance"
GENRE_DUBSTEP        = "dubstep"
GENRE_DRUM_AND_BASS  = "drum_and_bass"

# Cross-type
GENRE_ADULT          = "adult"          # explicit sexual content
GENRE_AI_GENERATED   = "ai_generated"   # primary creative content produced by AI
```

The list is intentionally flat. Sub-genres (house, techno, trance, dubstep,
drum_and_bass) sit beside their parents (electronic); consumers needing a
hierarchy build it on top.

### 4.15 `PictureFormat`

```python
class PictureFormat(str, Enum):
    BLACK_AND_WHITE = "black_and_white"  # monochrome image
    SILENT          = "silent"           # no synchronised audio track
    COLORIZED       = "colorized"        # colour added to an originally B&W work
    COLOR           = "color"            # native colour
    TWO_D           = "2d"               # flat image
    THREE_D         = "3d"               # stereoscopic
    SD              = "sd"               # standard definition
    HD              = "hd"               # high definition
    FOUR_K          = "4k"               # ultra high definition
    WIDESCREEN      = "widescreen"       # wide aspect ratio
    IMAX            = "imax"             # IMAX presentation
    OTHER           = "other"
```

Presentation/picture attributes of a manifestation — a technical Release
attribute (T6), admitted alongside the existing per-Release `color` /
`audio_present` booleans as a typed, multi-valued enum. Routing-family (A6);
**excluded from `work_hash`, `release_hash`, and `compare_signals`** — two
records differing only in `picture_format` are the same Work and do not
conflict. Lives on `Work.picture_format` and `Release.picture_format`
(`Optional`, default `None` per A2) and as the `Signals.picture_format`
routing hint, mapped through by `Work.from_signals`.

Distinct from the free-text `source_format` (§5.3): `source_format` is the
distribution container / capture medium ("Blu-ray", "Vinyl", "35mm");
`PictureFormat` is the typed presentation enum. `silent` /
`black_and_white` are also expressible as the booleans `audio_present=False`
/ `color=False` on a Release (§4.1, T6) — `PictureFormat` is the routing-axis
view that travels on `Signals` and that classifiers emit.

### 4.16 `Structure`

```python
class Structure(str, Enum):
    SINGLE     = "single"      # one self-contained work: a movie, a track, a book
    EPISODIC   = "episodic"    # a series of discrete instalments: tv series, podcast
    CONTINUOUS = "continuous"  # an unbounded live/looping stream: radio, live tv, ambient
    COLLECTION = "collection"  # an ordered set of works: a playlist
    UNKNOWN    = "unknown"
```

Derived from `MediaType` via `infer_structure()`; no persisted field on `Work`
or `Release` (A6, A7) — the same derived-axis pattern as `PlaybackType`
(§4.11). Routing-family (A6).

| Structure    | MediaTypes |
|---|---|
| `SINGLE`     | `MOVIE`, `SHORT_FILM`, `MUSIC`, `MUSIC_VIDEO`, `AUDIOBOOK`, `BOOK`, `COMIC`, `GAME`, `INTERACTIVE_FICTION`, `SOUND_EFFECT` |
| `EPISODIC`   | `EPISODIC_SERIES`, `PODCAST`, `AUDIO_DRAMA` |
| `CONTINUOUS` | `TV` (live channel), `RADIO`, `PROCEDURAL_AMBIENT` |
| `COLLECTION` | `PLAYLIST` |
| `UNKNOWN`    | pipeline sentinels |

The mapping is exhaustive over every concrete `MediaType` (enforced by
`tests/test_taxonomy_completeness.py`). A trained classifier MAY override the
leaf default per-utterance.

---

## 5. Models

The six models in §1.3–§1.4, the references that link them, and the
broadcast-schedule sub-model for live linear channels.

### 5.1 References

`Entity` has a dedicated lightweight pointer (`EntityRef`); `Work` and
`Release` do not — pointers to them are themselves a `Work` / `Release`
populated only with identity fields. The model surface deliberately
accepts the full record; consumers needing a strictly-typed reference
populate `title` / `media_type` / `external_ids` and leave everything
else empty.

Wire-format recursion is bounded by consumer convention: when filling a
`WorkRelation.target`, populate identity fields only — do not recurse
into the target's own `relations`, `tracklist`, or `credits`.

```python
class EntityRef(BaseModel):
    name: str
    kind: EntityKind
    external_ids: Dict[str, str] = {}   # {"musicbrainz_artist": "...", "imdb_person": "..."}


class LocalizedTitle(BaseModel):
    language: str        # ISO 639-1 lowercase; validated via text.iso.normalize_language
    title: str
    is_original: bool = False


class WorkRelation(BaseModel):
    kind: WorkRelationKind
    target: Work
    note: Optional[str] = None


class ReleaseRelation(BaseModel):
    kind: ReleaseRelationKind
    target: Release
    note: Optional[str] = None
```

A `Work` reference is resolvable when `external_ids` contains at least
one well-known key, or when `(title, media_type, year)` is enough for
the consumer's lookup. A `Release` reference is resolvable when
`external_ids` carries a release-level key (e.g. `musicbrainz_release`)
or the parent Work's identity is paired with format/region.

Relations live on `Work.relations: List[WorkRelation]` and
`Release.relations: List[ReleaseRelation]`. The `credits` field handles
entity→work relationships separately. Consumers preferring an external
relation table persist the same data under `(work_hash, kind)` or
`(release_hash, kind)` indices.

### 5.2 People and groups

```python
class Membership(BaseModel):
    entity: EntityRef
    roles: List[str]                        # ["vocals", "guitar"] — lowercase free text
    kind: MembershipKind                    # MEMBER / TOURING / SESSION / GUEST
    temporal: TemporalState                 # ACTIVE / ENDED / INACTIVE_GROUP
    date_from: Optional[str] = None         # year ("1986") or ISO date ("1986-03-01")
    date_to: Optional[str] = None           # None does NOT mean current; check temporal
    note: Optional[str] = None

    @model_validator(mode="after")
    def _check(self) -> "Membership":
        from mediavocab._iso_date import iso_compare
        if self.temporal == TemporalState.ACTIVE and self.date_to is not None:
            raise ValueError("ACTIVE membership must have date_to=None")
        if self.date_from is not None and self.date_to is not None \
                and iso_compare(self.date_to, self.date_from) < 0:
            raise ValueError("date_to precedes date_from")
        return self


class Credit(BaseModel):
    entity: EntityRef
    role: str                               # raw source string: "Electric Guitar", "Mix Engineer"
    relation_role: RelationRole             # typed role for programmatic routing
    section: CreditSection = CreditSection.PRINCIPAL
    note: Optional[str] = None              # "(tracks 1–4 only)", "(R.I.P. 1998)"


class Entity(BaseModel):
    name: str
    kind: EntityKind
    org_kind: Optional[OrganisationKind] = None   # only set when kind == ORGANISATION
    aliases: List[str] = []

    # PERSON-only
    birth_year: Optional[int] = None
    death_year: Optional[int] = None

    # GROUP / SERIES
    memberships: List[Membership] = []      # for GROUP: members over time; for SERIES: constituents

    # Hierarchy
    part_of: Optional[EntityRef] = None     # member of a label group, imprint, franchise

    # Lifecycle
    formed: Optional[str] = None
    disbanded: Optional[str] = None
    years_active: List[str] = []            # ["1986-1991", "1993-present"]

    external_ids: Dict[str, str] = {}
    extra: Dict[str, str] = {}

    @model_validator(mode="after")
    def _check(self) -> "Entity":
        if self.kind == EntityKind.ORGANISATION and self.org_kind is None:
            raise ValueError("ORGANISATION entity must set org_kind")
        if self.kind != EntityKind.ORGANISATION and self.org_kind is not None:
            raise ValueError("org_kind is only valid for ORGANISATION entities")
        if self.kind != EntityKind.PERSON and (self.birth_year or self.death_year):
            raise ValueError("birth_year / death_year are PERSON-only")
        return self
```

Credit list order is the editorial credit order — poster billing, liner
notes, opening titles. `Work.credits[0]` is *billed first*. Consumers
merging credits from multiple providers preserve first-seen order.

`Credit.role` preserves the raw source string for display; `relation_role`
maps it to the closed `RelationRole` enum so consumer code can route
without string-matching. When the raw role is not available, set `role` to
`relation_role.value`. When the typed role cannot be inferred, set
`relation_role = RelationRole.OTHER` and keep the raw string in `role`.

### 5.3 Works

```python
class Appearance(BaseModel):
    work: Work                            # canonical song, chapter, episode, cut
    position: int                            # track / chapter / episode number within container
    disc: int = 1                            # disc number for multi-disc releases
    offset: Optional[float] = None           # seconds into parent Release where this member starts;
                                             # used by continuous mixes (DJ sets, megamixes, live concerts)
    title_override: Optional[str] = None     # if re-titled on this release
    length_override: Optional[float] = None  # seconds; None = use work.runtime
    is_bonus: bool = False
    attributed_to: Optional[EntityRef] = None  # split releases: which band owns this track


class Work(BaseModel):
    title: str
    media_type:   MediaType                  # required; pipeline sentinels rejected (T8)
    content_form: ContentForm = ContentForm.PRIMARY  # identity axis (A8); enters work_hash

    # Temporal
    year: Optional[int] = None               # original release/broadcast year of this Work
    runtime: Optional[float] = None          # seconds; None overloads "unknown" and "indeterminate".
                                             # To disambiguate: indeterminate Works have
                                             # `media_type in {BOOK, COMIC, GAME, INTERACTIVE_FICTION,
                                             # TV, RADIO, PLAYLIST}` OR a Release with
                                             # `stream_mode == CONTINUOUS`. Otherwise None means unknown.

    # Language
    language: str = ""                       # ISO 639-1 / 639-2 primary language; "" = unknown / N/A.
                                             # Always set for a known multi-lingual Work — pick the
                                             # one that best identifies it (production-side primary).
    original_languages: List[str] = []       # full ordered list of originals for multi-lingual Works
                                             # (Quebec FR+EN: language="fr", original_languages=["fr","en"]).
                                             # Empty for single-language Works.

    # Geographic provenance (exactly one is non-empty per MediaType; validator enforced)
    production_country:  str = ""            # MOVIE, SHORT_FILM, EPISODIC_SERIES, MUSIC_VIDEO, GAME, INTERACTIVE_FICTION
    publication_country: str = ""            # BOOK, COMIC, MUSIC, AUDIOBOOK
    broadcaster_country: str = ""            # RADIO, TV, PODCAST, AUDIO_DRAMA

    # Episode / series structure (uniform across all episodic media)
    season: Optional[int] = None
    episode: Optional[int] = None
    series_title: Optional[str] = None       # denormalised; if a SERIES Entity exists, names should match
    episode_orderings: Dict[str, int] = {}   # {"production": 7, "broadcast": 5, "chronological": 12}

    # Edition (Work-only; restructurings produce new Works — see §3.4)
    variant_kind: Optional[VariantKind] = None
    edition: str = ""                        # free text: "Criterion Collection", "Author's Cut"
    source_format: str = ""                  # original capture/broadcast: "35mm", "DAB", "analogue tape"

    # Routing (excluded from work_hash; A6)
    content_genres: List[str] = []           # canonical genre.py constants
    programme_format: Optional[ProgrammeFormat] = None
    picture_format: Optional[PictureFormat] = None   # presentation attr (T6); routing (A6)
    release_status: ReleaseStatus = ReleaseStatus.RELEASED

    # Discovery (not part of identity)
    aka: List[str] = []
    localized_titles: List[LocalizedTitle] = []

    # Credits and containment
    credits: List[Credit] = []
    tracklist: List[Appearance] = []
    relations: List["WorkRelation"] = []

    # Cross-references
    external_ids: Dict[str, str] = {}        # {"imdb": "tt0078748", "musicbrainz_recording": "..."}
    extra: Dict[str, str] = {}

    @model_validator(mode="after")
    def _check(self) -> "Work":
        if self.media_type in {MediaType.GENERIC, MediaType.NOT_MEDIA, MediaType.CONTROL}:
            raise ValueError(
                "Work.media_type must be a concrete kind; "
                "GENERIC, NOT_MEDIA, and CONTROL are pipeline sentinels (T8)"
            )
        # Country-slot exclusivity: at most one of the three non-empty.
        slots = [self.production_country, self.publication_country, self.broadcaster_country]
        if sum(1 for s in slots if s) > 1:
            raise ValueError("at most one country slot may be set")
        return self
```

**Country slots.** Per MediaType:

| MediaType                                                      | Slot                  |
|----------------------------------------------------------------|-----------------------|
| MOVIE, SHORT_FILM, EPISODIC_SERIES, MUSIC_VIDEO, GAME, INTERACTIVE_FICTION | `production_country`  |
| MUSIC, BOOK, COMIC, AUDIOBOOK                                  | `publication_country` |
| RADIO, TV, PODCAST, AUDIO_DRAMA                                | `broadcaster_country` |
| SOUND_EFFECT, PROCEDURAL_AMBIENT, PLAYLIST                     | none (all three `""`) |

International co-productions and Works without a single origin leave all
three empty.

The model validator enforces *at most one slot non-empty* — it is valid for
all three slots to be empty (international productions, PLAYLIST, SOUND_EFFECT).
The validator does NOT enforce which slot matches the MediaType; the table
is editorial guidance for canonical records. Ingestion code may populate
the slot that best fits the source metadata.

**Edition, packaging, and variant disambiguation.**

| Field | Level | In hash? | Use for |
|-------|-------|----------|---------|
| `Work.variant_kind` | Work | ✅ | *Type* of restructuring: DIRECTORS, EXTENDED, THEATRICAL, FANEDIT, REMASTER, etc. |
| `Work.edition` | Work | ✅ | Free-text label that makes this cut unique: `"Unrated"`, `"4K Restoration"`. Changes the Work identity. |
| `Release.packaging` | Release | ❌ | How *this release ships*: DELUXE, BOX_SET, REISSUE, BOOTLEG. Distribution format, not content. |
| `Release.edition` | Release | ❌ | Free-text pressing label: `"Anniversary Edition"`, `"Limited Red Vinyl"`. Description-family. |

Rule of thumb: if two releases differ in *creative content* (different scenes, different runtime, different artistic choices) → they are different Works (`Work.variant_kind` + `Work.edition`). If they differ only in *how they ship* (bonus disc, deluxe packaging, different region) → they are different Releases of the same Work (`Release.packaging` + `Release.edition`).

**Series-vs-episode encoding.** A *series / show / channel / collection*
Work has `episode = None` (and usually `season = None`). An individual
*episode / chapter / issue / programme* Work has `episode` set, optionally
with `season`. `series_title` carries the parent series' name,
denormalised. Applies identically to `EPISODIC_SERIES`, `PODCAST`,
`AUDIO_DRAMA`, and `COMIC` (where `episode` carries issue/chapter and
`season` carries volume).

**Channels as Works.** A `RADIO` station, a `TV` channel, and a `PODCAST`
show all use the same shape: `episode = None`, `runtime = None`,
`external_ids` carrying provider IDs (radio-station directories, IPTV M3U
sources, podcast platform IDs). Stream URLs / RSS feeds (and any mirrors,
bitrates, or transmitters) are `Release`s of that Work. Individual
programmes are separate Works with `episode` set, linked via `series_title`
or a `Credit` to the parent station Entity with `RelationRole.DISTRIBUTOR`.

### 5.4 Releases

```python
class Chapter(BaseModel):
    """A timestamped marker within a Release: audiobook chapter, podcast chapter
    marker, DVD scene break. Chapters are NOT separate Works."""
    offset: float                            # seconds from start of the Release
    title: str = ""
    image: str = ""
    end: Optional[float] = None              # None = until next chapter / end


class AccessibilityKind(str, Enum):
    SUBTITLES         = "subtitles"
    CAPTIONS          = "captions"
    AUDIO_DESCRIPTION = "audio_description"
    SIGN_LANGUAGE     = "sign_language"
    TRANSCRIPT        = "transcript"
    LYRICS            = "lyrics"
    DUBBED            = "dubbed"          # localised replacement audio track


class AccessibilityTrack(BaseModel):
    kind: AccessibilityKind
    language: str = ""                       # ISO 639-1
    uri: str = ""
    forced: bool = False                     # subtitle "forced" flag
    sdh: bool = False                        # subtitles for deaf / hard-of-hearing
    note: Optional[str] = None


class AvailabilityWindow(BaseModel):
    start: Optional[str] = None              # ISO date; None = open-ended start
    end:   Optional[str] = None              # ISO date; None = no scheduled end
    note:  str = ""

    @model_validator(mode="after")
    def _check(self) -> "AvailabilityWindow":
        if self.start is not None and self.end is not None and self.end < self.start:
            raise ValueError("AvailabilityWindow.end precedes start")
        return self


class Release(BaseModel):
    work: Work                            # the canonical work this release manifests

    # Packaging (description-family; A6)
    packaging: Optional[ReleasePackaging] = None
    edition: str = ""                        # free text packaging label
    region: str = ""                         # ISO 3166-1 alpha-2 — release market

    # Format identity (T6)
    container: str = ""                      # "Blu-ray", "4K UHD", "DVD", "Vinyl", "CD", "Cassette",
                                             # "Digital", "Streaming", "Skill", "ROM", "Z-machine",
                                             # "Glulx", "Twine", "EPUB"
    codec: str = ""                          # "FLAC", "MP3", "AAC", "Opus", "H.264", "H.265", "AV1"
    bitrate: str = ""                        # "320kbps", "lossless", "24/96"
    platform: str = ""                       # game / IF runtime target
    resolution: str = ""                     # "480p", "720p", "1080p", "2160p", "4320p"

    # Audio / video quality (description; not identity)
    hdr: str = ""
    audio_channels: str = ""                 # "mono", "stereo", "5.1", "7.1", "Atmos"
    sample_rate: Optional[int] = None
    frame_rate: Optional[float] = None
    aspect_ratio: str = ""
    color: Optional[bool] = None
    audio_present: Optional[bool] = None
    picture_format: Optional[PictureFormat] = None   # presentation attr (T6); routing (A6)

    # Delivery
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    # Localisation (identity)
    audio_language: str = ""                 # ISO 639-1 primary audio — IDENTITY (the dub defines the version)
    subtitle_languages: List[str] = []       # description — added freely; does not change which Release this is

    # Lifecycle
    release_status: ReleaseStatus = ReleaseStatus.RELEASED
    release_date: Optional[str] = None       # ISO date or year string

    # Rights and availability
    license: str = ""                        # SPDX identifier or "all_rights_reserved" or ""
    region_locked: Optional[bool] = None     # True  → restricted; `regions_available` is the allow-list
                                             # False → worldwide; `regions_available` MUST be empty
                                             # None  → unknown
    regions_available: List[str] = []        # ISO 3166-1 alpha-2 codes; gated by `region_locked`
    availability_windows: List[AvailabilityWindow] = []

    # Playback
    uri: str = ""
    image: str = ""

    # Navigation / accessibility
    chapters: List[Chapter] = []
    accessibility: List[AccessibilityTrack] = []

    # Composite Releases (box sets, anthology Blu-rays, multi-cut discs)
    contents: List[Appearance] = []          # constituent Works as Appearances

    # Infrastructure
    label: Optional[EntityRef] = None
    distributor: Optional[EntityRef] = None

    # Release→Release lineage (supersession, ports, mirrors)
    relations: List["ReleaseRelation"] = []

    # Resolver-side scoring
    match_confidence: float = 0.0            # [0.0, 1.0]; set by resolver, not data entry

    # Cross-references
    external_ids: Dict[str, str] = {}
    extra: Dict[str, str] = {}

    @model_validator(mode="after")
    def _check(self) -> "Release":
        # Availability windows: ordered, non-overlapping, at most one open-ended.
        wins = sorted(self.availability_windows,
                      key=lambda w: (w.start is not None, w.start or ""))
        for prev, cur in zip(wins, wins[1:]):
            if prev.end is None or cur.start is None:
                raise ValueError("open-ended availability_window must be the last entry")
            if cur.start < prev.end:
                raise ValueError("availability_windows overlap")
        # region_locked ↔ regions_available invariant.
        if self.region_locked is False and self.regions_available:
            raise ValueError("region_locked=False requires regions_available to be empty")
        return self
```

**Inheritance.** Release has no identity fields of its own beyond format
and packaging. Title, year, runtime, language, country, credits, and
content_genres are always read through `release.work`; the Release model
deliberately does not declare those fields, and Release values never
back-propagate into Work.

**`Work.tracklist` vs `Release.contents`** — both are `List[Appearance]`
but answer different questions:

- `Work.tracklist` is the *canonical* track / chapter / episode order of
  a single Work — the album's intended sequence, the book's chapter list.
  Identity-level.
- `Release.contents` is the *aggregation* of multiple distinct Works in
  one box-set, anthology, or multi-cut disc. Manifestation-level.

### 5.5 Broadcast schedule

Live linear broadcast (`MediaType.TV`, `MediaType.RADIO`) needs a schedule
model: what is airing on this channel at what time. The channel-as-Work
captures stable channel identity; `Schedule` and `Programme` capture the
airing axis.

```python
class Programme(BaseModel):
    """A single airing of a Work on a broadcast channel."""
    work: Work                            # the content Work being aired
    channel: Work                         # the broadcast channel Work (RADIO / TV)
    starts_at: str                           # RFC 3339 / ISO 8601 datetime with offset
    ends_at: Optional[str] = None            # same format; None only on the trailing slot
    runtime: Optional[float] = None
    is_live: bool = False
    is_repeat: bool = False
    extra: Dict[str, str] = {}


class Schedule(BaseModel):
    channel: Work
    programmes: List[Programme] = []
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    source: str = ""                         # "tunein", "tvmaze", "epg.xml", …
    fetched_at: Optional[str] = None
    extra: Dict[str, str] = {}

    @model_validator(mode="after")
    def _check(self) -> "Schedule":
        from mediavocab._iso_date import iso_compare
        progs = self.programmes
        for prev, cur in zip(progs, progs[1:]):
            if iso_compare(prev.starts_at, cur.starts_at) > 0:
                raise ValueError("Schedule.programmes must be sorted by starts_at")
            if prev.ends_at is None:
                raise ValueError("only the last programme may have ends_at=None")
            if iso_compare(prev.ends_at, cur.starts_at) > 0:
                raise ValueError("Schedule.programmes overlap")
        return self
```

`Programme.starts_at` and `Programme.ends_at` must be RFC 3339 / ISO 8601
datetimes with timezone offset. Naive strings raise `ValueError`.

mediavocab does not model *what's on right now* as a function — query the
schedule for the slot whose `[starts_at, ends_at)` contains the consumer's
clock.

Schedules are append-only at the model level. To refresh, replace the
`Schedule` wholesale rather than mutating `programmes` in place — the
ordering and overlap invariants are validated at construction.

### 5.6 Device-as-Work

A *receiver-class* device — radio set, TV set, console, sound-machine
appliance, tunable streaming receiver — can be invoked as an experience
without a content query. *"Turn on the radio"* names the device, not a
station; the user accepts whatever it produces.

The pattern uses `Work` and `Entity(EntityKind.DEVICE)` without a new
MediaType or PlaybackType. The physical thing has two representations:

- An `Entity(kind=EntityKind.DEVICE)` for routing (cast targets, room
  assignment).
- A `Work` for invocation. Its `MediaType` is the medium the device serves
  (`RADIO` / `TV` / `GAME` / `PROCEDURAL_AMBIENT`).

The two records share an `external_ids` key — typically
`home_assistant_entity_id`, `sonos_udn`, `chromecast_device_id`, or
`alexa_device_id`.

```python
Entity(
    name="Kitchen Radio",
    kind=EntityKind.DEVICE,
    external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"},
    extra={"room": "kitchen", "category": "audio"},
)

Work(
    title="Kitchen Radio",
    media_type=MediaType.RADIO,
    content_form=ContentForm.PRIMARY,
    external_ids={"home_assistant_entity_id": "media_player.kitchen_radio"},
)
```

A consumer asked to handle *"turn on the radio"*:

1. Looks up Works whose `external_ids` matches a known
   `EntityKind.DEVICE` of receiver class in the household scope.
2. If exactly one → return that Work; the player invokes its current
   Release (read from the device's tune-state or default Release).
3. If multiple → disambiguate by room or device name.
4. If zero → fall back to a generic `MediaType.RADIO` query.

A device is receiver-class when invoking it without specifying content
produces a coherent media experience. Radios, TVs, consoles, sound
machines, and tunable streaming receivers qualify. Lights, locks,
thermostats, and plugs do not — invoking them produces no media output
(`MediaType.NOT_MEDIA`).

A3 holds: delivery is not identity. The Work IS the experience (not a
delivery channel for some other content), and its identity is rooted in
the device. The `MediaType` and `PlaybackType` of a kitchen radio are
identical to any other `RADIO` Work.

### 5.7 Work vs Release — decision guide

| Question                                                              | Answer                                                                   |
|-----------------------------------------------------------------------|--------------------------------------------------------------------------|
| Is *Alien* the same film as *Alien (Director's Cut)*?                 | Different Works (each cut is its own Work — §3.4); linked by `FANEDIT_OF` |
| Is *Battery* on the original album the same as on a compilation?      | Same Work, two Appearances in two Release containers                     |
| Are the primary stream URL and backup mirror of BBC Radio 4 the same? | Same Work, two Releases with different URIs                              |
| Is the 1986 CD and the 2016 remaster of *Master of Puppets* the same? | Different Works (the remaster restructures the source); linked by `DERIVED_FROM` |
| Is the same 1986 CD pressing in Japan and the US the same?            | Same Work, two Releases (`region`, `packaging` differ)                   |
| Is a cover version of *Hallelujah* the same Work as the original?     | Different Works; a `COVERS` relation may link them                       |

### 5.8 Worked example — *Master of Puppets*

The album, its principal track, two Releases, the band, and one departed
member. Every cross-reference resolves.

```python
metallica = Entity(
    name="Metallica",
    kind=EntityKind.GROUP,
    formed="1981",
    years_active=["1981-present"],
    external_ids={"musicbrainz_artist": "65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab"},
    memberships=[
        Membership(
            entity=EntityRef(name="James Hetfield", kind=EntityKind.PERSON,
                             external_ids={"musicbrainz_artist": "..."}),
            roles=["vocals", "rhythm guitar"],
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ACTIVE,
            date_from="1981",
        ),
        Membership(
            entity=EntityRef(name="Cliff Burton", kind=EntityKind.PERSON,
                             external_ids={"musicbrainz_artist": "..."}),
            roles=["bass"],
            kind=MembershipKind.MEMBER,
            temporal=TemporalState.ENDED,
            date_from="1982",
            date_to="1986-09-27",
            note="died in tour-bus accident",
        ),
    ],
)

cliff = Entity(
    name="Cliff Burton",
    kind=EntityKind.PERSON,
    birth_year=1962,
    death_year=1986,
    external_ids={"musicbrainz_artist": "..."},
)

battery = Work(
    title="Battery",
    media_type=MediaType.MUSIC,
    year=1986,
    runtime=312.0,
    publication_country="US",
    language="en",
    content_genres=["metal", "thrash"],
    credits=[
        Credit(
            entity=EntityRef(name="Metallica", kind=EntityKind.GROUP),
            role="Performer", relation_role=RelationRole.PERFORMER,
            section=CreditSection.PRINCIPAL,
        ),
        Credit(
            entity=EntityRef(name="Cliff Burton", kind=EntityKind.PERSON),
            role="Bass", relation_role=RelationRole.PERFORMER,
            section=CreditSection.PRINCIPAL,
        ),
    ],
    external_ids={"musicbrainz_recording": "...", "isrc": "USEL18600001"},
)

master_of_puppets = Work(
    title="Master of Puppets",
    media_type=MediaType.MUSIC,
    year=1986,
    runtime=3290.0,
    publication_country="US",
    language="en",
    content_genres=["metal", "thrash"],
    credits=[
        Credit(
            entity=EntityRef(name="Metallica", kind=EntityKind.GROUP),
            role="Performer", relation_role=RelationRole.PERFORMER,
        ),
        Credit(
            entity=EntityRef(name="Flemming Rasmussen", kind=EntityKind.PERSON),
            role="Producer", relation_role=RelationRole.PRODUCER,
            section=CreditSection.STAFF,
        ),
        Credit(
            entity=EntityRef(name="Elektra", kind=EntityKind.ORGANISATION),
            role="Label", relation_role=RelationRole.LABEL,
            section=CreditSection.STAFF,
        ),
    ],
    tracklist=[
        Appearance(work=Work(title="Battery", media_type=MediaType.MUSIC,
                                external_ids={"isrc": "USEL18600001"}),
                   position=1),
        # … 7 more tracks
    ],
    external_ids={"musicbrainz_release_group": "..."},
)

original_cd = Release(
    work=Work(title="Master of Puppets", media_type=MediaType.MUSIC, year=1986),
    container="CD",
    codec="PCM",
    region="US",
    audio_language="en",
    release_date="1986-03-03",
    label=EntityRef(name="Elektra", kind=EntityKind.ORGANISATION),
    license="all_rights_reserved",
    external_ids={"musicbrainz_release": "..."},
)

# The 2017 remaster is a NEW Work (§3.4: restructurings produce new Works),
# not a Release variant of the 1986 album.
master_of_puppets_remastered = Work(
    title="Master of Puppets (Remastered)",
    media_type=MediaType.MUSIC,
    year=2017,
    runtime=3290.0,
    publication_country="US",
    language="en",
    variant_kind=VariantKind.REMASTERED,
    content_genres=["metal", "thrash"],
    relations=[
        WorkRelation(
            kind=WorkRelationKind.DERIVED_FROM,
            target=Work(title="Master of Puppets",
                           media_type=MediaType.MUSIC, year=1986,
                           external_ids={"musicbrainz_release_group": "..."}),
            note="2017 remaster from original master tapes",
        ),
    ],
    external_ids={"musicbrainz_release_group": "..."},
)

remaster_cd = Release(
    work=Work(title="Master of Puppets (Remastered)",
                 media_type=MediaType.MUSIC, year=2017,
                 external_ids={"musicbrainz_release_group": "..."}),
    packaging=ReleasePackaging.DELUXE,
    edition="Remastered Deluxe Box Set",
    container="CD",
    codec="PCM",
    region="US",
    audio_language="en",
    release_date="2017-11-10",
    label=EntityRef(name="Blackened Recordings", kind=EntityKind.ORGANISATION),
    license="all_rights_reserved",
    external_ids={"musicbrainz_release": "..."},
)
```

Two Works (1986 album + 2017 remastered album) linked by
`WorkRelation(DERIVED_FROM)`; each has its own Release(s). Packaging
differences (deluxe, regional, format) stay on the Release; structural
changes to the artefact (remastering, recutting) promote to a new Work.

---

## 6. Operations

Hashing, comparison, and merging operate on the models in §5. The order
below is the order needed to read each function: primitives →
quantum table → hashes → compare/score → merge → ISO helpers.

### 6.1 Normalisation primitives

All functions are pure and deterministic — same input, same output, no I/O.

```python
def strip_diacritics(text: str) -> str:
    """NFKD decomposition, drop combining marks. 'café' → 'cafe'."""

def normalize(text: str) -> str:
    """Full pipeline:
       1. strip_diacritics
       2. lowercase
       3. remove featured-artist credits: (feat|ft|featuring) ...
       4. remove parenthetical and bracketed suffixes
       5. collapse non-word characters to spaces
       6. strip and collapse internal whitespace
    Suitable for fuzzy comparison."""

def fuzzy_ratio(a: str, b: str) -> float:
    """SequenceMatcher ratio on normalize(a) vs normalize(b). [0.0, 1.0]."""

def best_match(query: str, candidates: List[str]) -> Tuple[str, float]:
    """Return (best_candidate, score)."""

def title_words(text: str) -> List[str]:
    """Tokenise into meaningful words. Strips common stopwords and articles."""

# Identity-input primitives
def normalise_title(s: str) -> str:
    """Full `normalize` pipeline. Empty input → empty output."""

def normalise_edition(s: str) -> str:
    """Same as normalise_title. Used for `edition`, `source_format`."""

def normalise_format(s: str) -> str:
    """Lowercase, ASCII-stripped, whitespace-collapsed, no punctuation.
       'Blu-ray' → 'bluray'; '320 kbps' → '320kbps'; 'H.265' → 'h265'."""

def normalise_country(s: str) -> str:
    """ISO 3166-1 alpha-2 uppercase via text.iso.normalize_country.
       Empty → empty; unrecognised raises ValueError."""

def normalise_language(s: str) -> str:
    """ISO 639-1 lowercase via text.iso.normalize_language.
       Empty → empty; unrecognised raises ValueError."""
```

### 6.2 Runtime quantum table

`work_hash` rounds `runtime` to a per-MediaType quantum before hashing, so
two providers reporting durations within tolerance produce the same digest.
The quantum equals the identity tolerance.

```python
QUANTUM_SKIP = -1     # sentinel: exclude runtime from the hash for this MediaType

RUNTIME_HASH_QUANTUM_S: Dict[MediaType, int] = {
    MediaType.MOVIE:                120,
    MediaType.SHORT_FILM:             5,
    MediaType.EPISODIC_SERIES:       30,
    MediaType.TV:                     0,
    MediaType.MUSIC:                  3,
    MediaType.MUSIC_VIDEO:           30,
    MediaType.PODCAST:               60,
    MediaType.AUDIOBOOK:             60,
    MediaType.AUDIO_DRAMA:           60,
    MediaType.RADIO:                  0,
    MediaType.BOOK:                   0,
    MediaType.COMIC:                  0,
    MediaType.GAME:                   0,
    MediaType.INTERACTIVE_FICTION:    0,
    MediaType.SOUND_EFFECT:           0,
    MediaType.PROCEDURAL_AMBIENT:     0,
    MediaType.PLAYLIST:              QUANTUM_SKIP,    # runtime is sum-of-members of a mutable tracklist
}
```

Sentinel semantics:

- **`0`** — include runtime at second precision.
- **`N > 0`** — round to the nearest multiple of N seconds.
- **`QUANTUM_SKIP` (`-1`)** — exclude runtime from the hash entirely.

### 6.3 `work_hash`

```python
def work_hash(w: Work) -> str:
    """Stable hash over identity fields. Returns a lowercase hex SHA-256 digest,
    64 characters.

    Inputs, in order, joined by \\x1f (ASCII unit separator):

        normalise_title(title)
        media_type.value                   # raises if GENERIC, NOT_MEDIA, CONTROL
        content_form.value                 # always set; defaults to PRIMARY
        year_or_empty(year)
        country_slot(w)                    # the one non-empty country, normalised
        normalise_language(language)
        round_runtime(runtime, media_type) # per RUNTIME_HASH_QUANTUM_S; "" if QUANTUM_SKIP
        season_or_empty(season)
        episode_or_empty(episode)
        normalise_title(series_title)
        variant_kind.value or ""
        normalise_edition(edition)
        normalise_edition(source_format)

    Excluded:
        content_genres, programme_format, picture_format, credits, aka,
        localized_titles, original_languages, episode_orderings, tracklist,
        relations, external_ids, extra, release_status.

    Notes:
    - `content_form` is included by A8: a trailer and the primary work share
      (title, year, media_type) and would otherwise collide.
    - `country_slot(w)` reads whichever of production_country /
      publication_country / broadcaster_country is non-empty (at most one,
      enforced by the Work validator). Returns `""` when all three are empty
      (international co-productions, SOUND_EFFECT, PROCEDURAL_AMBIENT, PLAYLIST).
    - `series_title` is included because two shows can share season+episode+title
      (S01E01 'Pilot' is a common collision).

    Stability: input list and `normalise_title()` behaviour are frozen for
    the v1.x line. `NORMALISE_TITLE_VERSION` (exported from
    `mediavocab.text.normalize`) pins the normalisation pipeline; any
    semantic change to `normalise_title()` increments this constant and
    constitutes a breaking change requiring a major version bump.
    A major-version change uses a new symbol (`work_hash_v2`)."""
```

### 6.4 `release_hash`

```python
def release_hash(r: Release) -> str:
    """Stable hash over Release identity fields. Returns a lowercase hex
    SHA-256 digest, 64 characters.

    Inputs, in order, joined by \\x1f:

        work_hash(r.work)                  # always computed; the embedded Work
                                           # must have a concrete (non-sentinel)
                                           # media_type — see §6.3
        normalise_country(region)
        normalise_format(container)
        normalise_format(codec)
        normalise_format(bitrate)
        normalise_format(platform)
        normalise_format(resolution)
        normalise_language(audio_language)

    Excluded (description, mutable, or packaging):
        packaging, edition, uri, image, license, region_locked,
        regions_available, availability_windows, release_date, release_status,
        chapters, accessibility, contents, label, distributor, frame_rate,
        aspect_ratio, color, audio_present, picture_format, hdr, audio_channels,
        sample_rate, subtitle_languages, match_confidence, external_ids, extra.

    The exclusions are deliberate: a Release acquires accessibility tracks,
    chapter markers, and availability windows over its lifetime — none should
    change its identity. `packaging` is excluded because deluxe / reissue / box-set
    labels are description-layer (A6).

    Stability: input list is frozen for the v1.x line."""
```

### 6.5 `compare` and `score`

```python
class Conflict(BaseModel):
    field: str
    ours: Any
    theirs: Any


def compare(a: Work, b: Work) -> List[Conflict]:
    """Return overlapping fields that disagree.

    Compared (only when both sides have a value):
        title (fuzzy), year, runtime (within RUNTIME_HASH_QUANTUM_S[media_type]),
        media_type, language, season, episode, series_title,
        production_country, publication_country, broadcaster_country,
        variant_kind, edition, source_format, content_form.

    Out of scope:
        aka, localized_titles, content_genres, programme_format, picture_format,
        credits, tracklist, relations, external_ids, extra, release_status,
        episode_orderings.

    Absence is NOT a conflict — it is unknown.
    Empty list means no contradictions found (may still be a weak match)."""


TITLE_MIN   = 0.92
ARTIST_MIN  = 0.90
YEAR_WINDOW = 1


def score(query: Work, candidate: Work) -> float:
    """[0.0, 1.0] match quality.

    Hard penalties (multiplicative):
    - Title fuzzy ratio is the primary driver; aka and localized_titles are fallbacks.
    - Year mismatch beyond YEAR_WINDOW halves the score.
    - MediaType mismatch halves the score.
    - ContentForm mismatch halves the score (a trailer is not the film).
    - For episodic media: series_title mismatch halves; season/episode halves again.
    - Country slot mismatch halves (when both sides have the same slot non-empty).
    - language mismatch halves (when both sides specify it).

    Bonuses (additive, capped at 1.0):
    - variant_kind agreement: +0.02 (correct cut > correct film).
    - content_genres overlap: +0.01 per overlapping tag.
    - programme_format agreement: +0.02."""
```

The compare tolerance and the hash quantum are the same dict
(`RUNTIME_HASH_QUANTUM_S`, §6.2). The quantum *is* the tolerance: two
durations that round to the same multiple hash identically and compare
as a match.

### 6.6 `merge` and `merge_releases`

```python
class MergeStrategy(BaseModel):
    provider_priority: List[str] = []
    title_strategy:   str = "longest"   # "first" | "longest" | "newest"
    edition_strategy: str = "first"


DEFAULT_STRATEGY = MergeStrategy()


def merge(*works: Work, strategy: MergeStrategy = DEFAULT_STRATEGY) -> Work:
    """Combine partial records. Contract:

    1. Identity fields (work_hash inputs) MUST agree after normalisation across
       all inputs. Disagreement raises `IdentityConflict(field, values)`. Two
       provider records with different `year` are two different Works.

    2. Scalar mutable fields use the strategy's tie-breaker. Empty strings and
       None are treated as "no opinion" and skipped.

    3. List fields union with per-field dedup keys:
         aka:                case-folded normalised title
         localized_titles:   (language, normalised title)
         content_genres:     verbatim string (already canonical)
         credits:            (entity.external_ids first match, relation_role, role)
         tracklist:          (position, disc) — collisions are conflicts, not merges
         relations:          (kind, target.work_hash or first external_id)
         external_ids:       key; first-writer-wins per key
       Order preserves first-seen, then provider_priority order.

    4. `extra` dicts are key-unioned; on key collision, first-writer wins unless
       `provider_priority` overrides.

    5. `release_status` collapses to the highest-confidence state:
       RELEASED > WITHDRAWN > ANNOUNCED > IN_PRODUCTION > CANCELLED > UNKNOWN."""


def merge_releases(*releases: Release, strategy: MergeStrategy = DEFAULT_STRATEGY) -> Release:
    """Same contract scoped to Release. Identity inputs are `release_hash` inputs."""
```

`compare(a, b)` MUST be called before `merge` when callers cannot rule out
identity conflicts; `merge` is the commit step, not the diff step.

### 6.7 ISO helpers

```python
def validate_language(code: str) -> str:
    """Validate ISO 639-1 or ISO 639-2. Return normalised lowercase. Raises ValueError if invalid."""

def validate_country(code: str) -> str:
    """Validate ISO 3166-1 alpha-2. Return normalised uppercase. Raises ValueError if invalid."""

def normalize_language(v: str) -> str:
    """Accept full language name, 2-letter, or 3-letter code; return ISO 639-1.
       'English' → 'en', 'EN' → 'en', 'eng' → 'en'."""

def normalize_country(v: str) -> str:
    """Accept full country name or alpha-2 code; return ISO 3166-1 alpha-2 uppercase.
       'United States' → 'US', 'gb' → 'GB'."""
```

---

## 7. Identifiers and rights

### 7.1 `external_ids`

Every model carries `external_ids: Dict[str, str]` as its canonical
persistence form. Well-known keys are module-level constants in
`mediavocab.models.external_ids`:

```python
IMDB                       = "imdb"
TMDB                       = "tmdb"
MUSICBRAINZ_RECORDING      = "musicbrainz_recording"
MUSICBRAINZ_RELEASE_GROUP  = "musicbrainz_release_group"
MUSICBRAINZ_RELEASE        = "musicbrainz_release"
MUSICBRAINZ_ARTIST         = "musicbrainz_artist"
ISRC                       = "isrc"
ISBN_10                    = "isbn_10"
ISBN_13                    = "isbn_13"
RSS_GUID                   = "rss_guid"
IFDB                       = "ifdb"
IGDB                       = "igdb"
RAWG                       = "rawg"
SHORTOFTHEWEEK             = "shortoftheweek"
VIMEO                      = "vimeo"
SPOTIFY_PLAYLIST           = "spotify_playlist_id"
YOUTUBE_PLAYLIST           = "youtube_playlist_id"
HOME_ASSISTANT_ENTITY_ID   = "home_assistant_entity_id"
SONOS_UDN                  = "sonos_udn"
CHROMECAST_DEVICE_ID       = "chromecast_device_id"
ALEXA_DEVICE_ID            = "alexa_device_id"
```

Provider-namespaced keys (`bandcamp_album_id`) follow the
`<provider>_<entity>_id` pattern. Well-known key spellings are frozen for
the v1.x line — renames are a breaking change.

Per A7, when a fact has a typed field (e.g. `Release.bitrate`), it lives
there and not in `external_ids`. The dict is for *third-party identifiers*,
not for refitting model fields.

**Optional helper.** `mediavocab.models.ExternalIds` is a Pydantic
companion model exposing the well-known keys as typed fields plus an
ISBN-10/-13 auto-pairing rule and a first-writer-wins `merge()`. It is
*not* the canonical persistence form — `Dict[str, str]` is — but
consumers wanting IDE completion and validation can build the dict
through it: `ExternalIds(imdb="tt0083658").to_dict()`.

**Streams.** `mediavocab.models.Stream` is a helper that derives
playable `(platform, url, media_type)` triples from
provider-namespaced keys in an `ExternalIds.extra` map
(`youtube_video_id` → `youtube` Stream; `bandcamp_track_url` → `bandcamp`
Stream). The Stream is a *view*, not a persisted record — the canonical
data is the underlying `external_ids` key.

**Station mirrors and multi-bitrate streams.** A radio station or TV
channel typically publishes several stream URLs — DAB, web high-bitrate,
web low-bitrate, regional transmitter, backup mirror. The station is one
Work (T4); each stream URL is a separate `Release`, distinguished by
`codec` / `bitrate` / `container` / `region`. A
`ReleaseRelation(MIRROR_OF, target=primary_release)` may link mirrors to
a canonical primary stream when consumers want to surface lineage.

There is no `Stream` sub-model — the existing `Release` shape carries
everything a stream needs (`uri`, `codec`, `bitrate`, `container`,
`region`, `stream_mode`).

### 7.2 License helpers

`Release.license: str` is an SPDX-style identifier or empty when unknown.
Predicates operate directly on the string:

```python
def is_open(spdx: str) -> bool:
    """True for SPDX identifiers in the open-licence family
    (CC0, CC-BY*, CC-BY-SA*, GPL family, Apache, MIT, BSD, public_domain, PDM)."""

def is_public_domain(spdx: str) -> bool:
    """True for 'public_domain', 'PDM', 'CC0-1.0'."""

def requires_attribution(spdx: str) -> bool:
    """True for any Creative Commons variant carrying BY."""

def allows_commercial(spdx: str) -> bool:
    """False for NC variants; True otherwise."""

def allows_derivatives(spdx: str) -> bool:
    """False for ND variants; True otherwise."""

def allows_share_alike(spdx: str) -> bool:
    """True for SA variants and copyleft (GPL family)."""
```

For unrecognised identifiers every predicate returns the most-restrictive
answer: `is_open=False`, `is_public_domain=False`, `allows_commercial=False`,
`allows_derivatives=False`, `allows_share_alike=False`,
`requires_attribution=True`.

**Optional helper.** `mediavocab.models.License` is a Pydantic companion
model. Like `ExternalIds`, it is *not* the canonical persisted form —
`Release.license: str` is — but consumers can parse an SPDX string into
typed flags via `License.from_spdx(spdx)`. Per A7, the string is the
single source of truth; the typed view is a read-only overlay.

---

## 8. Versioning and stability

- **`taxonomy/`** — stable from v1.0. Enum values are never removed; new
  values may be added in minor versions. Renaming a value is a breaking
  change.
- **`models/`** — stable from v1.0. Fields are never removed; optional
  fields may be added in minor versions. Changing a field type is a
  breaking change.
- **`text/`** — function signatures are stable from v1.0. Tolerance
  defaults may be tuned in minor versions with changelog notes.
- **`genre.py` constants** — additive only. New constants may be added in
  any version. Changing a constant string value is a breaking change.
- **`external_ids` well-known keys** — additive only. Renaming an existing
  key is a breaking change.

### 8.1 Field mutability after canonicalisation

Once a Work has been canonicalised (assigned a `work_hash`), its fields
fall into two classes:

**Immutable** — changing these produces a *different* Work:

- `media_type`, `content_form`, `year`, `runtime` (except for PLAYLIST),
  `production_country`, `publication_country`, `broadcaster_country`,
  `language`, `season`, `episode`, `series_title`, `variant_kind`,
  `edition`, `source_format`.

(These are the inputs to `work_hash`; §6.3.)

**Mutable** — these accumulate as more sources are merged. A new provider
supplying additional values is *enrichment*, not conflict:

- `content_genres`, `programme_format`, `aka`, `localized_titles`,
  `credits`, `tracklist`, `relations`, `original_languages`,
  `episode_orderings`, `external_ids`, `extra`, `release_status`.

**`tracklist` on a `PLAYLIST` Work** is mutable even though *what tracks
are in the playlist* is the playlist's reason to exist. A reordered or
membership-edited Spotify playlist is the same playlist in source-side
terms (same `spotify_playlist_id`); the hash agrees by design.

### 8.2 Release mutability

Release identity fields (`release_hash` inputs) are likewise immutable.
Packaging, edition, format-quality fields, availability windows,
accessibility tracks, chapters, and `contents` are mutable as providers
refine their data.

A box set's `contents` list (a Trilogy collecting three films, a Deluxe
Edition with extras) is not an identity input. A consumer that discovers
a different `contents` shape is looking at refined metadata, not a
different Release.

### 8.3 The `extra` escape hatch

Every model surfacing external metadata carries an `extra` dict, typed
`Dict[str, str]` throughout the spec. This is an explicit landfill for
provider-specific values that have not yet earned a typed field.

1. **Strings only.** New code writes strings; the validator rejects
   non-string values. Encode lists as comma-joined strings, numbers as
   their decimal representation.
2. **Promotion is the goal.** A key that appears across two or more
   providers, or that downstream consumers branch on, is a candidate for
   promotion to a typed field on the next minor release.
3. **Identity-irrelevant.** No `extra` key participates in `work_hash` or
   `release_hash`.
4. **Provider-namespaced when ambiguous.** Two providers writing the same
   key (`url`, `image`, `source`) collide silently. Prefix with the
   provider when the key is not universally well-defined.
5. **No mediavocab-internal use.** mediavocab never *reads* `extra`
   values. Anything mediavocab ships normative behaviour around is a
   typed field.

---

## 9. Application patterns

`mediavocab` provides vocabulary and structure. Application logic lives
downstream. Patterns resolve to existing `MediaType`, `ContentForm`,
`EntityKind`, and `Work` / `Release` / `Entity` fields — no new schema.

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
- Box sets and composite Releases → `docs/patterns/box-sets.md`
- Format, quality, rights, and availability → `docs/patterns/quality-rights-availability.md`
- Playback-type routing → `docs/patterns/playback-type.md`
- Live broadcast scheduling → `docs/patterns/scheduling.md`
- Writing a metadata provider → `docs/patterns/writing-a-provider.md`
- Multiple episode orderings → see `Work.episode_orderings` field docs in §5.3
