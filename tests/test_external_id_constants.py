"""Well-known external_id key constants (spec §7.1).

The well-known keys are frozen for the v1.x line — renames are a breaking
change. Spelling is lowercase; conform to a `<provider>_<entity>_id`-ish
pattern.
"""
from mediavocab.models import external_ids as eid


# ---------------------------------------------------------------------------
# Constants exist and have stable string values (frozen for v1.x)
# ---------------------------------------------------------------------------

class TestStableKeySpellings:
    """Renaming any of these strings is a breaking change. The point of these
    constants is so consumers don't string-match the same provider's keys
    differently across packages."""

    def test_film_and_tv_keys(self):
        assert eid.IMDB == "imdb"
        assert eid.TMDB == "tmdb"
        assert eid.TVMAZE == "tvmaze"
        assert eid.TVDB == "tvdb"

    def test_musicbrainz_keys(self):
        assert eid.MUSICBRAINZ_ARTIST == "musicbrainz_artist"
        assert eid.MUSICBRAINZ_RECORDING == "musicbrainz_recording"
        assert eid.MUSICBRAINZ_RELEASE == "musicbrainz_release"
        assert eid.MUSICBRAINZ_RELEASE_GROUP == "musicbrainz_release_group"

    def test_music_distribution_keys(self):
        assert eid.DISCOGS_ARTIST == "discogs_artist"
        assert eid.DISCOGS_RELEASE == "discogs_release"
        assert eid.SPOTIFY == "spotify"
        assert eid.ISRC == "isrc"

    def test_book_keys(self):
        assert eid.ISBN == "isbn"
        assert eid.OPENLIBRARY == "openlibrary"
        assert eid.GOODREADS == "goodreads"

    def test_audiobook_podcast_keys(self):
        assert eid.AUDIBLE == "audible"
        assert eid.LIBRIVOX == "librivox"
        assert eid.PODCAST_INDEX == "podcast_index"
        assert eid.APPLE_PODCASTS == "apple_podcasts"

    def test_radio_keys(self):
        assert eid.TUNEIN == "tunein"
        assert eid.RADIO_BROWSER == "radio_browser"
        assert eid.RDS_PI == "rds_pi"

    def test_game_keys(self):
        assert eid.IGDB == "igdb"
        assert eid.MOBYGAMES == "mobygames"
        assert eid.STEAM == "steam"
        assert eid.GOG == "gog"

    def test_interactive_fiction_keys(self):
        assert eid.IFDB == "ifdb"

    def test_new_anime_and_film_keys(self):
        assert eid.ANIDB == "anidb"
        assert eid.LETTERBOXD == "letterboxd"

    def test_new_music_streaming_keys(self):
        assert eid.BANDCAMP == "bandcamp"
        assert eid.SOUNDCLOUD == "soundcloud"
        assert eid.YOUTUBE_CHANNEL == "youtube_channel"
        assert eid.YOUTUBE_VIDEO == "youtube_video"
        assert eid.YOUTUBE_MUSIC_ARTIST == "youtube_music_artist"

    def test_new_book_keys(self):
        assert eid.HARDCOVER == "hardcover"
        assert eid.READING_GLASSES == "reading_glasses"

    def test_new_podcast_radio_keys(self):
        assert eid.PODCAST_INDEX_FEED == "podcast_index_feed"
        assert eid.RADIO_BROWSER_UUID == "radio_browser_uuid"

    def test_music_platform_artist_keys(self):
        assert eid.AUDIODB_ARTIST == "audiodb_artist_id"
        assert eid.AUDIODB_ALBUM == "audiodb_album_id"
        assert eid.AUDIODB_TRACK == "audiodb_track_id"
        assert eid.BANDCAMP_ARTIST == "bandcamp_band_id"
        assert eid.SOUNDCLOUD_USER == "soundcloud_user_id"
        assert eid.YOUTUBE_MUSIC_ARTIST_BROWSE == "youtube_music_artist_browse_id"
        assert eid.YOUTUBE_CHANNEL_ID == "youtube_channel_id"
        assert eid.MUSICBRAINZ_LABEL == "musicbrainz_label"

    def test_iheart_keys(self):
        assert eid.IHEART_STATION == "iheart_station_id"
        assert eid.IHEART_PODCAST == "iheart_podcast_id"
        assert eid.IHEART_EPISODE == "iheart_episode_id"
        assert eid.IHEART_ARTIST == "iheart_artist_id"
        assert eid.IHEART_TRACK == "iheart_track_id"
        assert eid.IHEART_PLAYLIST == "iheart_playlist_id"


def test_known_external_ids_frozenset():
    from mediavocab import KNOWN_EXTERNAL_IDS
    assert isinstance(KNOWN_EXTERNAL_IDS, frozenset)
    assert len(KNOWN_EXTERNAL_IDS) >= 50
    for key in ("imdb", "bandcamp", "letterboxd", "anidb", "hardcover",
                "youtube_channel", "podcast_index_feed", "radio_browser_uuid"):
        assert key in KNOWN_EXTERNAL_IDS, f"{key!r} missing from KNOWN_EXTERNAL_IDS"


# ---------------------------------------------------------------------------
# Keys follow the lowercase / underscore convention
# ---------------------------------------------------------------------------

def test_all_known_keys_are_lowercase():
    """Every well-known constant value is lowercase with underscores
    (no spaces, no mixed-case, no hyphens)."""
    import re
    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    public_names = [
        n for n in dir(eid)
        if n.isupper() and not n.startswith("_")
        and isinstance(getattr(eid, n), str)
    ]
    assert public_names, "should have well-known constants"
    for name in public_names:
        value = getattr(eid, name)
        assert pattern.match(value), f"{name}={value!r} violates lowercase pattern"


# ---------------------------------------------------------------------------
# ExternalIds.from_dict / to_dict round-trips
# ---------------------------------------------------------------------------

def test_external_ids_round_trips_via_constants():
    from mediavocab import ExternalIds
    src = {eid.IMDB: "tt0083658", eid.MUSICBRAINZ_RELEASE: "abc-123"}
    obj = ExternalIds.from_dict(src)
    assert obj.imdb == "tt0083658"
    out = obj.to_dict()
    assert out[eid.IMDB] == "tt0083658"
    assert out[eid.MUSICBRAINZ_RELEASE] == "abc-123"


def test_unknown_keys_land_in_extra():
    from mediavocab import ExternalIds
    obj = ExternalIds.from_dict({"some_obscure_provider_id": "x"})
    assert obj.extra["some_obscure_provider_id"] == "x"
    # Round-trip
    assert obj.to_dict()["some_obscure_provider_id"] == "x"


# ---------------------------------------------------------------------------
# New first-class fields — tvmaze, music platform IDs, iHeart
# ---------------------------------------------------------------------------

def test_tvmaze_is_first_class_field():
    from mediavocab import ExternalIds
    ids = ExternalIds(tvmaze=1234)
    d = ids.to_dict()
    assert d["tvmaze"] == "1234"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.tvmaze == 1234


def test_discogs_artist_is_first_class_field():
    from mediavocab import ExternalIds
    ids = ExternalIds(discogs_artist=999)
    d = ids.to_dict()
    assert d["discogs_artist"] == "999"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.discogs_artist == 999


def test_musicbrainz_label_is_first_class_field():
    from mediavocab import ExternalIds
    ids = ExternalIds(musicbrainz_label="mb-label-uuid")
    d = ids.to_dict()
    assert d["musicbrainz_label"] == "mb-label-uuid"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.musicbrainz_label == "mb-label-uuid"


def test_audiodb_fields_are_first_class():
    from mediavocab import ExternalIds
    ids = ExternalIds(audiodb_artist_id=10, audiodb_album_id=20, audiodb_track_id=30)
    d = ids.to_dict()
    assert d["audiodb_artist_id"] == "10"
    assert d["audiodb_album_id"] == "20"
    assert d["audiodb_track_id"] == "30"


def test_bandcamp_band_id_is_first_class():
    from mediavocab import ExternalIds
    ids = ExternalIds(bandcamp_band_id=555)
    d = ids.to_dict()
    assert d["bandcamp_band_id"] == "555"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.bandcamp_band_id == 555


def test_soundcloud_user_id_is_first_class():
    from mediavocab import ExternalIds
    ids = ExternalIds(soundcloud_user_id="my-band")
    d = ids.to_dict()
    assert d["soundcloud_user_id"] == "my-band"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.soundcloud_user_id == "my-band"


def test_youtube_channel_id_is_first_class():
    from mediavocab import ExternalIds
    ids = ExternalIds(youtube_channel_id="UCxyz123")
    d = ids.to_dict()
    assert d["youtube_channel_id"] == "UCxyz123"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.youtube_channel_id == "UCxyz123"


def test_iheart_station_round_trips():
    from mediavocab import ExternalIds
    ids = ExternalIds(iheart_station_id="7556")
    d = ids.to_dict()
    assert d["iheart_station_id"] == "7556"
    ids2 = ExternalIds.from_dict(d)
    assert ids2.iheart_station_id == "7556"


def test_iheart_episode_carries_podcast_link():
    from mediavocab import ExternalIds
    ids = ExternalIds(iheart_episode_id="9999", iheart_podcast_id="1234")
    d = ids.to_dict()
    ids2 = ExternalIds.from_dict(d)
    assert ids2.iheart_episode_id == "9999"
    assert ids2.iheart_podcast_id == "1234"
