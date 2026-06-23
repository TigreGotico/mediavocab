"""Tests for mediavocab.io.schema_org."""
import json

from mediavocab import MediaType, Work, Release
from mediavocab.io import work_to_schema_org, release_to_schema_org


def _movie():
    return Work(title="Blade Runner", media_type=MediaType.MOVIE, year=1982,
                runtime=7020.0, language="en", production_country="US",
                content_genres=["sci_fi", "noir"],
                external_ids={"imdb": "tt0083658", "wikidata": "Q104878"})


def test_work_has_context_and_type():
    d = work_to_schema_org(_movie())
    assert d["@context"] == "https://schema.org"
    assert d["@type"] == "Movie"


def test_work_name():
    assert work_to_schema_org(_movie())["name"] == "Blade Runner"


def test_work_date_published():
    assert work_to_schema_org(_movie())["datePublished"] == "1982"


def test_work_duration_format():
    d = work_to_schema_org(_movie())
    assert d["duration"] == "PT1H57M"


def test_work_in_language():
    assert work_to_schema_org(_movie())["inLanguage"] == "en"


def test_work_genre():
    d = work_to_schema_org(_movie())
    assert "sci_fi" in d["genre"]
    assert "noir" in d["genre"]


def test_work_country_of_origin():
    d = work_to_schema_org(_movie())
    assert d["countryOfOrigin"]["@type"] == "Country"
    assert d["countryOfOrigin"]["name"] == "US"


def test_work_same_as_imdb():
    d = work_to_schema_org(_movie())
    same_as = d.get("sameAs", [])
    if isinstance(same_as, str):
        same_as = [same_as]
    assert any("imdb.com/title/tt0083658" in s for s in same_as)


def test_work_same_as_wikidata():
    d = work_to_schema_org(_movie())
    same_as = d.get("sameAs", [])
    if isinstance(same_as, str):
        same_as = [same_as]
    assert any("wikidata.org/wiki/Q104878" in s for s in same_as)


def test_work_is_json_serialisable():
    d = work_to_schema_org(_movie())
    json.dumps(d)  # must not raise


def test_music_type_mapping():
    w = Work(title="Stairway to Heaven", media_type=MediaType.MUSIC)
    d = work_to_schema_org(w)
    assert d["@type"] == "MusicRecording"


def test_tv_series_type():
    w = Work(title="Doctor Who", media_type=MediaType.EPISODIC_SERIES,
             series_title="Doctor Who", season=1, episode=1)
    d = work_to_schema_org(w)
    assert d["@type"] == "TVSeries"
    assert d["partOfSeries"]["name"] == "Doctor Who"
    assert d["seasonNumber"] == 1
    assert d["episodeNumber"] == 1


def test_release_url():
    r = Release(work=_movie(), uri="https://example.org/blade_runner.mkv",
                container="MKV", audio_language="en")
    d = release_to_schema_org(r)
    assert d["url"] == "https://example.org/blade_runner.mkv"
    assert d["encodingFormat"] == "MKV"


def test_release_license():
    r = Release(work=_movie(), license="CC-BY-4.0")
    d = release_to_schema_org(r)
    assert "license" in d


def test_release_regions():
    r = Release(work=_movie(), region_locked=True,
                regions_available=["US", "CA"])
    d = release_to_schema_org(r)
    assert len(d["availableInCountry"]) == 2


def test_extra_props_passthrough():
    d = work_to_schema_org(_movie(), audience={"@type": "Audience", "audienceType": "adult"})
    assert d["audience"]["audienceType"] == "adult"
