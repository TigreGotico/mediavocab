from mediavocab import LocalizedTitle, MediaType, Work
from mediavocab.text import score


def test_localized_titles_default_empty():
    w = Work(title="x", media_type=MediaType.MOVIE)
    assert w.localized_titles == []


def test_localized_title_used_as_score_fallback():
    query = Work(title="Le Voyage dans la Lune", media_type=MediaType.MOVIE)
    candidate = Work(
        title="A Trip to the Moon",
        media_type=MediaType.MOVIE,
        localized_titles=[
            LocalizedTitle(title="Le Voyage dans la Lune", language="fr", is_original=True),
            LocalizedTitle(title="A Trip to the Moon", language="en"),
        ],
    )
    # The English title alone would score poorly; the localized French entry rescues it.
    assert score(query, candidate) >= 0.99


def test_localized_titles_round_trip():
    w = Work(
        title="x",
        media_type=MediaType.COMIC,
        localized_titles=[
            LocalizedTitle(title="X-Men", language="en"),
            LocalizedTitle(title="X-メン", language="ja"),
        ],
    )
    again = Work.model_validate_json(w.model_dump_json())
    assert again.localized_titles[1].title == "X-メン"
    assert again.localized_titles[1].language == "ja"
