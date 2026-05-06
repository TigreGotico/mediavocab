"""Well-known string keys for the `external_ids: Dict[str, str]` field.

These are conventions, not validation rules. mediavocab does not enforce that
keys be one of these — but using them improves cross-package interoperability.
The canonical type stays `Dict[str, str]` (spec §9.6).
"""

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

# Comics
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
