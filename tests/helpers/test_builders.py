from mediavocab import MediaType, RelationRole, StreamMode, VariantKind
from mediavocab.helpers import (
    make_movie, make_episode, make_release, make_credit,
)
from mediavocab.taxonomy import EntityKind


def test_make_movie_with_director():
    m = make_movie("Alien", year=1979, runtime=117 * 60.0, director="Ridley Scott")
    assert m.media_type == MediaType.MOVIE
    assert m.year == 1979
    assert m.credits[0].relation_role == RelationRole.DIRECTOR
    assert m.credits[0].entity.name == "Ridley Scott"


def test_make_episode_synthesises_title():
    e = make_episode("Doctor Who", season=4, episode=10)
    assert e.title.endswith("S04E10")
    assert e.media_type == MediaType.TV
    assert (e.season, e.episode) == (4, 10)


def test_make_release_continuous():
    work = make_movie("x")
    r = make_release(work, "https://stream", stream_mode=StreamMode.CONTINUOUS,
                     variant_kind=VariantKind.REMASTERED)
    assert r.uri == "https://stream"
    assert r.stream_mode == StreamMode.CONTINUOUS
    assert r.variant_kind == VariantKind.REMASTERED


def test_make_credit_default_role_is_relation_value():
    c = make_credit("Nobuo Uematsu", EntityKind.PERSON, RelationRole.COMPOSER)
    assert c.role == "composer"
    assert c.relation_role == RelationRole.COMPOSER
