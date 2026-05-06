from mediavocab.taxonomy import (
    GENRE_ANIME, GENRE_ASMR, GENRE_ADULT, GENRE_MOTION_COMIC,
    GENRE_SFX_NATURE, GENRE_AMBIENT, GENRE_AI_GENERATED,
)
from mediavocab.taxonomy import genre as genre_module


def test_canonical_spellings_lowercase_underscored():
    assert GENRE_ANIME == "anime"
    assert GENRE_ASMR == "asmr"
    assert GENRE_ADULT == "adult"
    assert GENRE_MOTION_COMIC == "motion_comic"
    assert GENRE_SFX_NATURE == "sfx_nature"
    assert GENRE_AMBIENT == "ambient"
    assert GENRE_AI_GENERATED == "ai_generated"


def test_no_uppercase_or_spaces_in_any_genre_constant():
    for name in dir(genre_module):
        if not name.startswith("GENRE_"):
            continue
        v = getattr(genre_module, name)
        assert v == v.lower(), f"{name} not lowercase: {v}"
        assert " " not in v, f"{name} contains space: {v}"
