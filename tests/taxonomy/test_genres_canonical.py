from mediavocab.taxonomy import (
    GENRE_HORROR, GENRE_COMEDY, GENRE_DRAMA, GENRE_THRILLER, GENRE_SCI_FI,
    GENRE_FANTASY, GENRE_ROMANCE, GENRE_WESTERN, GENRE_MYSTERY, GENRE_ACTION,
    GENRE_ROCK, GENRE_POP, GENRE_JAZZ, GENRE_CLASSICAL, GENRE_ELECTRONIC,
    GENRE_METAL, GENRE_PUNK, GENRE_FOLK, GENRE_BLUES, GENRE_COUNTRY,
    GENRE_INDIE, GENRE_REGGAE, GENRE_HOUSE, GENRE_TECHNO,
    GENRE_VARIETY, GENRE_TALK, GENRE_COMPILATION, GENRE_INSTRUCTIONAL,
    GENRE_NATURE, GENRE_TRAVEL, GENRE_COOKING, GENRE_FITNESS,
    GENRE_TRUE_CRIME, GENRE_SELF_HELP, GENRE_VOCALOID, GENRE_CITY_POP,
    KNOWN_GENRES,
)


def test_canonical_narrative_genres_exist():
    assert GENRE_HORROR == "horror"
    assert GENRE_COMEDY == "comedy"
    assert GENRE_DRAMA == "drama"
    assert GENRE_SCI_FI == "sci_fi"
    assert GENRE_FANTASY == "fantasy"


def test_canonical_music_genres_exist():
    assert GENRE_ROCK == "rock"
    assert GENRE_JAZZ == "jazz"
    assert GENRE_METAL == "metal"
    assert GENRE_HOUSE == "house"


def test_no_uppercase_or_spaces_in_canonical_genres():
    for v in (GENRE_HORROR, GENRE_COMEDY, GENRE_DRAMA, GENRE_THRILLER,
              GENRE_SCI_FI, GENRE_FANTASY, GENRE_ROMANCE, GENRE_WESTERN,
              GENRE_MYSTERY, GENRE_ACTION, GENRE_ROCK, GENRE_POP, GENRE_JAZZ,
              GENRE_CLASSICAL, GENRE_ELECTRONIC, GENRE_METAL, GENRE_PUNK,
              GENRE_FOLK, GENRE_BLUES, GENRE_COUNTRY, GENRE_INDIE,
              GENRE_REGGAE, GENRE_HOUSE, GENRE_TECHNO):
        assert v == v.lower()
        assert " " not in v


def test_new_tv_podcast_genres():
    assert GENRE_VARIETY == "variety"
    assert GENRE_TALK == "talk"
    assert GENRE_COMPILATION == "compilation"
    assert GENRE_INSTRUCTIONAL == "instructional"
    assert GENRE_NATURE == "nature"
    assert GENRE_TRAVEL == "travel"
    assert GENRE_COOKING == "cooking"
    assert GENRE_FITNESS == "fitness"
    assert GENRE_TRUE_CRIME == "true_crime"
    assert GENRE_SELF_HELP == "self_help"


def test_new_jmusic_genres():
    assert GENRE_VOCALOID == "vocaloid"
    assert GENRE_CITY_POP == "city_pop"


def test_known_genres_contains_all_new_constants():
    for g in (GENRE_VARIETY, GENRE_TALK, GENRE_COMPILATION, GENRE_INSTRUCTIONAL,
              GENRE_NATURE, GENRE_TRAVEL, GENRE_COOKING, GENRE_FITNESS,
              GENRE_TRUE_CRIME, GENRE_SELF_HELP, GENRE_VOCALOID, GENRE_CITY_POP):
        assert g in KNOWN_GENRES, f"{g!r} missing from KNOWN_GENRES"


def test_known_genres_is_frozenset_with_all_constants():
    assert isinstance(KNOWN_GENRES, frozenset)
    assert len(KNOWN_GENRES) >= 85
    assert all(g == g.lower() and " " not in g for g in KNOWN_GENRES)
