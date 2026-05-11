"""External identifiers — known keys + typed model.

The string constants below are the canonical key names for the free-form
``external_ids`` dicts on :class:`Work` / :class:`Release` / :class:`Entity`
/ :class:`EntityRef`. Using the constants improves cross-package
interoperability without forcing a closed enum.

The :class:`ExternalIds` Pydantic model is a typed alternative for
consumers who want validation, IDE completion, automatic ISBN pairing,
and a first-writer-wins :meth:`merge`. Either representation is
acceptable; the model serialises to and from the same dict shape.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mediavocab.text.isbn import isbn10_to_13, isbn13_to_10, normalize_isbn


# ---------------------------------------------------------------------------
# Well-known key constants
# ---------------------------------------------------------------------------

# Film and TV
IMDB = "imdb"
TMDB = "tmdb"
TVMAZE = "tvmaze"
TVDB = "tvdb"

# Music
MUSICBRAINZ_ARTIST = "musicbrainz_artist"
MUSICBRAINZ_RECORDING = "musicbrainz_recording"
MUSICBRAINZ_RELEASE = "musicbrainz_release"
MUSICBRAINZ_RELEASE_GROUP = "musicbrainz_release_group"
DISCOGS_ARTIST = "discogs_artist"
DISCOGS_RELEASE = "discogs_release"
SPOTIFY = "spotify"
ISRC = "isrc"
LASTFM = "lastfm"

# Books
ISBN = "isbn"
OPENLIBRARY = "openlibrary"
GOODREADS = "goodreads"

# Audio long-form
AUDIBLE = "audible"
LIBRIVOX = "librivox"
PODCAST_INDEX = "podcast_index"
APPLE_PODCASTS = "apple_podcasts"

# Radio
TUNEIN = "tunein"
RADIO_BROWSER = "radio_browser"
RDS_PI = "rds_pi"

# Audio drama
BIG_FINISH = "big_finish"

# Games
IGDB = "igdb"
MOBYGAMES = "mobygames"
STEAM = "steam"
GOG = "gog"

# Variants / fan edits
# Note: there are two databases historically called "IFDB":
#   - IFDB.org: the Interactive Fiction Database (Infocom, Inform, Twine)
#   - Internet Fanedit Database (the fanedit.org community DB)
# We reserve `ifdb` for interactive fiction (more widely cited externally)
# and use `fanedit_ifdb` for the fanedit one.
IFDB = "ifdb"                # Interactive Fiction Database — see also IF block below
FANEDIT_IFDB = "fanedit_ifdb"
FANEDIT_ORG = "fanedit_org"

# Interactive fiction
IFICTION = "ifiction"        # ifiction.org IFiction archive
ALEXA_SKILL = "alexa_skill"
GOOGLE_ACTION = "google_action"
MYCROFT_SKILL = "mycroft_skill"

# Adult
IAFD = "iafd"
ADULTFILMDATABASE = "adultfilmdatabase"

# Comics / anime / manga
COMIXOLOGY = "comixology"
ANILIST = "anilist"
MYANIMELIST = "myanimelist"

# Devices and routing
HOME_ASSISTANT = "home_assistant"
MQTT_TOPIC = "mqtt_topic"

# Anything else: free-form
WIKIDATA = "wikidata"
YOUTUBE = "youtube"

ALL_KNOWN_KEYS = (
    IMDB, TMDB, TVMAZE, TVDB,
    MUSICBRAINZ_ARTIST, MUSICBRAINZ_RECORDING, MUSICBRAINZ_RELEASE,
    MUSICBRAINZ_RELEASE_GROUP, DISCOGS_ARTIST, DISCOGS_RELEASE, SPOTIFY,
    ISRC, LASTFM,
    ISBN, OPENLIBRARY, GOODREADS,
    AUDIBLE, LIBRIVOX, PODCAST_INDEX, APPLE_PODCASTS,
    TUNEIN, RADIO_BROWSER, RDS_PI,
    BIG_FINISH,
    IGDB, MOBYGAMES, STEAM, GOG,
    IFDB, FANEDIT_IFDB, FANEDIT_ORG,
    IFICTION, ALEXA_SKILL, GOOGLE_ACTION, MYCROFT_SKILL,
    IAFD, ADULTFILMDATABASE,
    COMIXOLOGY, ANILIST, MYANIMELIST,
    HOME_ASSISTANT, MQTT_TOPIC,
    WIKIDATA, YOUTUBE,
)


# ---------------------------------------------------------------------------
# Stream extraction — IDs in `extra` that resolve to playable URLs
# ---------------------------------------------------------------------------

# (extra_key, platform, media_type, url_template_or_None)
# url_template uses {id} as the placeholder; None means the value IS the URL.
_STREAM_MAP = (
    ("soundcloud_track_url",      "soundcloud",    "track",    None),
    ("bandcamp_track_url",        "bandcamp",      "track",    None),
    ("bandcamp_album_url",        "bandcamp",      "album",    None),
    ("music_video_url",           "youtube",       "video",    None),
    ("youtube_video_id",          "youtube",       "video",    "https://www.youtube.com/watch?v={id}"),
    ("youtube_music_video_id",    "youtube_music", "video",    "https://music.youtube.com/watch?v={id}"),
    ("youtube_music_playlist_id", "youtube_music", "playlist", "https://music.youtube.com/playlist?list={id}"),
    ("stream_url",                "radio",         "stream",   None),
)


class Stream(BaseModel):
    """A playable media stream from a known platform.

    Constructed from :meth:`ExternalIds.streams` — aggregates playable
    URLs and IDs stored in ``ExternalIds.extra`` into a typed, uniform
    list. Consumers building players should iterate
    ``ids.streams`` rather than reaching into the raw dict.

    `kind` is the platform's *asset category* ("track", "album",
    "video", "playlist", "stream") — distinct from `MediaType` (the
    canonical mediavocab schema-axis enum). Two different concepts;
    a YouTube "video" Stream may carry a Work of `MediaType.MOVIE`,
    `MUSIC_VIDEO`, or `EPISODIC_SERIES`.
    """

    model_config = ConfigDict(extra="ignore")

    platform: str         # "bandcamp", "soundcloud", "youtube", "youtube_music", "radio", …
    url: str              # fully-formed playable URL
    kind: str             # "track", "album", "video", "playlist", "stream"
    id: Optional[str] = None  # raw ID when the URL was constructed from one


# ---------------------------------------------------------------------------
# Typed external-id model
# ---------------------------------------------------------------------------

class ExternalIds(BaseModel):
    """Typed, validated companion to the ``Dict[str, str]`` ``external_ids``
    field.

    Use this when you want IDE completion, ISBN auto-pairing, typed
    merging, or stream extraction. The model can serialise to and from a
    plain dict via :meth:`to_dict` / :meth:`from_dict` so consumers that
    prefer the dict representation stay compatible.

    Known fields are first-class so the schema is explicit; unknown keys
    land in :attr:`extra` (string → string), so a new provider can ship
    without breaking validation.
    """

    model_config = ConfigDict(extra="forbid")

    # MusicBrainz
    musicbrainz_recording: Optional[str] = None
    musicbrainz_release: Optional[str] = None
    musicbrainz_release_group: Optional[str] = None
    musicbrainz_work: Optional[str] = None
    musicbrainz_artist: Optional[str] = None

    # Video
    imdb: Optional[str] = None             # tt-id
    tmdb_movie: Optional[int] = None
    tmdb_tv: Optional[int] = None
    tvdb: Optional[int] = None
    trakt_id: Optional[int] = None

    # Books
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    olid: Optional[str] = None
    goodreads: Optional[str] = None
    google_books_id: Optional[str] = None

    # Linked-data hub
    wikidata: Optional[str] = None         # Q-id

    # People
    tmdb_person: Optional[int] = None
    imdb_person: Optional[str] = None      # nm-id

    # Encyclopaedia Metallum (metal-archives.com) ids
    metal_archives_band: Optional[int] = None
    metal_archives_release: Optional[int] = None
    metal_archives_song: Optional[int] = None
    metal_archives_label: Optional[int] = None
    metal_archives_artist: Optional[int] = None

    # Release variants
    fanedit_id: Optional[int] = None             # IFDB WordPress post ID
    derived_from_imdb: Optional[str] = None      # parent IMDb tt-id when this record IS a variant

    # Physical-disc catalogues
    discogs_release: Optional[int] = None
    bluray_com_id: Optional[int] = None
    dvdcompare_id: Optional[str] = None

    # Audiobook / podcast
    podcast_index_id: Optional[int] = None
    audible_asin: Optional[str] = None
    librivox_id: Optional[int] = None
    apple_podcast_id: Optional[int] = None
    listen_notes_id: Optional[str] = None

    # Anime / manga — work-level
    anilist_id: Optional[int] = None
    mal_id: Optional[int] = None
    anidb_id: Optional[int] = None

    # Anime / manga — entity-level
    anilist_staff_id: Optional[int] = None
    anilist_studio_id: Optional[int] = None
    anilist_character_id: Optional[int] = None
    mal_person_id: Optional[int] = None
    mal_studio_id: Optional[int] = None
    mal_character_id: Optional[int] = None

    # Games
    opencritic_id: Optional[int] = None
    rawg_id: Optional[int] = None
    igdb_id: Optional[int] = None

    # Anything else a provider produced that we don't have a slot for.
    extra: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _normalize_and_pair_isbn(self) -> "ExternalIds":
        """Canonicalise ISBN forms and back-fill the sibling representation.

        ``ISBN-10`` and ``ISBN-13`` (for 978-prefixed editions) describe
        the same edition; without normalisation the catalogue would
        treat ``"0-261-10328-8"`` and ``"9780261103283"`` as different
        identifiers and fail to merge records that came from providers
        using different conventions.
        """
        if self.isbn_10:
            self.isbn_10 = normalize_isbn(self.isbn_10) or self.isbn_10
        if self.isbn_13:
            self.isbn_13 = normalize_isbn(self.isbn_13) or self.isbn_13
        if self.isbn_10 and not self.isbn_13:
            self.isbn_13 = isbn10_to_13(self.isbn_10) or None
        elif self.isbn_13 and not self.isbn_10:
            self.isbn_10 = isbn13_to_10(self.isbn_13) or None
        return self

    def merge(self, other: "ExternalIds") -> "ExternalIds":
        """Field-wise merge — first-writer-wins semantics.

        ``self`` is treated as the higher-precedence source: any value
        it already holds is preserved, and ``other`` only fills in
        fields that ``self`` left empty. The same rule applies to
        ``extra``, so an ``extra`` key set by the higher-precedence
        source is never silently overwritten by a later (weaker)
        provider.
        """
        out = self.model_copy(deep=True)
        for name in type(self).model_fields:
            if name == "extra":
                continue
            cur = getattr(out, name)
            new = getattr(other, name)
            if cur in (None, "") and new not in (None, ""):
                setattr(out, name, new)
        merged_extra = dict(other.extra)   # weak source as the base...
        merged_extra.update(out.extra)     # ...overridden by the strong source
        out.extra = merged_extra
        return out

    def is_empty(self) -> bool:
        """True iff no known field is set and ``extra`` is empty."""
        return self == ExternalIds()

    @property
    def streams(self) -> List[Stream]:
        """Return all playable stream URLs as typed :class:`Stream` objects.

        Aggregates known streaming keys from ``extra``, constructing
        full URLs from raw IDs where needed (e.g.
        ``youtube_video_id`` → ``https://www.youtube.com/watch?v=<id>``).
        Artist / album *page* URLs are intentionally excluded — only
        directly playable content is listed.
        """
        results: List[Stream] = []
        for key, platform, kind, tmpl in _STREAM_MAP:
            val = self.extra.get(key)
            if not val:
                continue
            url = tmpl.format(id=val) if tmpl else val
            results.append(Stream(
                platform=platform,
                url=url,
                kind=kind,
                id=val if tmpl else None,
            ))
        return results

    def to_dict(self) -> Dict[str, str]:
        """Serialise to a plain ``Dict[str, str]`` suitable for the
        free-form ``external_ids`` field on Work / Release / Entity.

        Keys with a typed integer value are stringified. Empty / ``None``
        fields are omitted.
        """
        out: Dict[str, str] = {}
        for name in type(self).model_fields:
            if name == "extra":
                continue
            val = getattr(self, name)
            if val in (None, ""):
                continue
            out[name] = str(val)
        out.update(self.extra)
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ExternalIds":
        """Build an ``ExternalIds`` from a plain dict, routing unknown
        keys into ``extra``."""
        known = set(cls.model_fields) - {"extra"}
        kwargs: dict = {}
        extras: Dict[str, str] = {}
        for k, v in (data or {}).items():
            if k in known:
                kwargs[k] = v
            else:
                extras[k] = str(v)
        kwargs["extra"] = extras
        return cls(**kwargs)
