import pytest

from mediavocab import ExternalIds, Stream
from mediavocab.models import external_ids as eid


# ---------------------------------------------------------------------------
# Well-known string constants
# ---------------------------------------------------------------------------

def test_known_keys_are_lowercase_strings():
    for k in eid.ALL_KNOWN_KEYS:
        assert isinstance(k, str)
        assert k == k.lower()
        assert " " not in k


def test_known_keys_unique():
    assert len(eid.ALL_KNOWN_KEYS) == len(set(eid.ALL_KNOWN_KEYS))


def test_a_few_well_known():
    assert eid.IMDB == "imdb"
    assert eid.MUSICBRAINZ_RECORDING == "musicbrainz_recording"
    assert eid.HOME_ASSISTANT == "home_assistant"


# ---------------------------------------------------------------------------
# ISBN auto-pairing on construction
# ---------------------------------------------------------------------------

def test_isbn10_backfills_isbn13():
    ids = ExternalIds(isbn_10="0261103288")
    assert ids.isbn_13 == "9780261103283"


def test_isbn13_backfills_isbn10():
    ids = ExternalIds(isbn_13="9780261103283")
    assert ids.isbn_10 == "0261103288"


def test_isbn_normalization_strips_formatting():
    ids = ExternalIds(isbn_10="0-261-10328-8", isbn_13="978-0-261-10328-3")
    assert ids.isbn_10 == "0261103288"
    assert ids.isbn_13 == "9780261103283"


def test_isbn13_no_pair_for_979():
    # 979 ISBNs cannot map to ISBN-10
    ids = ExternalIds(isbn_13="9791234567896")
    assert ids.isbn_10 is None


# ---------------------------------------------------------------------------
# is_empty
# ---------------------------------------------------------------------------

def test_is_empty_default_instance():
    assert ExternalIds().is_empty() is True


def test_is_empty_false_when_field_set():
    assert ExternalIds(imdb="tt0078748").is_empty() is False


def test_is_empty_false_when_extra_set():
    assert ExternalIds(extra={"custom": "x"}).is_empty() is False


# ---------------------------------------------------------------------------
# merge — first-writer-wins
# ---------------------------------------------------------------------------

def test_merge_fills_only_empty_fields():
    a = ExternalIds(imdb="tt0078748", tmdb_movie=348)
    b = ExternalIds(imdb="tt0000000", wikidata="Q103937")
    merged = a.merge(b)
    assert merged.imdb == "tt0078748"           # a wins
    assert merged.tmdb_movie == 348             # only on a
    assert merged.wikidata == "Q103937"         # only on b → filled


def test_merge_extra_first_writer_wins():
    a = ExternalIds(extra={"k": "from-a"})
    b = ExternalIds(extra={"k": "from-b", "other": "from-b"})
    merged = a.merge(b)
    assert merged.extra["k"] == "from-a"        # a wins
    assert merged.extra["other"] == "from-b"    # only on b


def test_merge_does_not_mutate_inputs():
    a = ExternalIds(imdb="tt1")
    b = ExternalIds(imdb="tt2")
    a.merge(b)
    assert a.imdb == "tt1"
    assert b.imdb == "tt2"


# ---------------------------------------------------------------------------
# to_dict / from_dict round-trip
# ---------------------------------------------------------------------------

def test_to_dict_omits_none():
    ids = ExternalIds(imdb="tt0078748", tmdb_movie=348)
    d = ids.to_dict()
    assert d == {"imdb": "tt0078748", "tmdb_movie": "348"}


def test_to_dict_includes_extra():
    ids = ExternalIds(imdb="tt1", extra={"custom": "x"})
    d = ids.to_dict()
    assert d == {"imdb": "tt1", "custom": "x"}


def test_from_dict_routes_unknown_to_extra():
    ids = ExternalIds.from_dict({
        "imdb": "tt1",
        "tmdb_movie": "348",
        "custom": "x",
    })
    assert ids.imdb == "tt1"
    assert ids.tmdb_movie == 348
    assert ids.extra == {"custom": "x"}


# ---------------------------------------------------------------------------
# streams extraction
# ---------------------------------------------------------------------------

def test_streams_youtube_video_id_expands_to_url():
    ids = ExternalIds(extra={"youtube_video_id": "dQw4w9WgXcQ"})
    streams = ids.streams
    assert len(streams) == 1
    s = streams[0]
    assert isinstance(s, Stream)
    assert s.platform == "youtube"
    assert s.kind == "video"
    assert s.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert s.id == "dQw4w9WgXcQ"


def test_streams_passthrough_url_keys():
    ids = ExternalIds(extra={"bandcamp_track_url": "https://x.bandcamp.com/track/y"})
    streams = ids.streams
    assert len(streams) == 1
    assert streams[0].platform == "bandcamp"
    assert streams[0].url == "https://x.bandcamp.com/track/y"
    assert streams[0].id is None  # value WAS the URL, no template applied


def test_streams_empty_when_no_known_keys():
    ids = ExternalIds(imdb="tt1", extra={"unrelated": "value"})
    assert ids.streams == []


def test_streams_aggregates_multiple_platforms():
    ids = ExternalIds(extra={
        "youtube_video_id": "abc",
        "bandcamp_track_url": "https://x.bandcamp.com/track/y",
        "soundcloud_track_url": "https://soundcloud.com/x/y",
    })
    platforms = {s.platform for s in ids.streams}
    assert platforms == {"youtube", "bandcamp", "soundcloud"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_extra_forbid_on_unknown_top_level_key():
    """Unknown keys at the top level must be rejected — they belong in extra."""
    with pytest.raises(Exception):
        ExternalIds(unknown_provider_id="x")


# ---------------------------------------------------------------------------
# Work / Release `external_ids_model` typed accessor
# ---------------------------------------------------------------------------

def test_work_external_ids_model_roundtrip():
    from mediavocab import Work, MediaType
    w = Work(title="X", media_type=MediaType.MUSIC,
             external_ids={"tmdb": "1", "soundcloud_track_id": "7"})
    m = w.external_ids_model
    assert isinstance(m, ExternalIds)
    assert m.extra["soundcloud_track_id"] == "7"
    w.external_ids_model = ExternalIds(igdb_id=5)
    assert w.external_ids == {"igdb_id": "5"}


def test_release_external_ids_model_roundtrip():
    from mediavocab import Work, Release, MediaType
    r = Release(work=Work(title="X", media_type=MediaType.MUSIC))
    r.external_ids_model = ExternalIds(trakt_id=9)
    assert r.external_ids == {"trakt_id": "9"}
    assert isinstance(r.external_ids_model, ExternalIds)
