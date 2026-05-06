from mediavocab.taxonomy import (
    GENRE_HORROR, GENRE_COMEDY, GENRE_DRAMA, GENRE_THRILLER, GENRE_SCI_FI,
    GENRE_FANTASY, GENRE_ROMANCE, GENRE_WESTERN, GENRE_MYSTERY, GENRE_ACTION,
    GENRE_ROCK, GENRE_POP, GENRE_JAZZ, GENRE_CLASSICAL, GENRE_ELECTRONIC,
    GENRE_METAL, GENRE_PUNK, GENRE_FOLK, GENRE_BLUES, GENRE_COUNTRY,
    GENRE_INDIE, GENRE_REGGAE, GENRE_HOUSE, GENRE_TECHNO,
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
