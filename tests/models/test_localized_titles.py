from mediavocab import MediaType, Work
from mediavocab.text import score


def test_localized_titles_default_empty():
    w = Work(title="x")
    assert w.localized_titles == []


def test_localized_title_used_as_score_fallback():
    query = Work(title="Le Voyage dans la Lune", media_type=MediaType.MOVIE)
    candidate = Work(
        title="A Trip to the Moon",
        media_type=MediaType.MOVIE,
        localized_titles=[("Le Voyage dans la Lune", "fr"),
                          ("A Trip to the Moon", "en")],
    )
    # The English title alone would score poorly; the localized French entry rescues it.
    assert score(query, candidate) >= 0.99


def test_localized_titles_round_trip():
    w = Work(title="x", localized_titles=[("X-Men", "en"), ("X-メン", "ja")])
    again = Work.model_validate_json(w.model_dump_json())
    assert again.localized_titles[1] == ("X-メン", "ja")
