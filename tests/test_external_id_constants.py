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
