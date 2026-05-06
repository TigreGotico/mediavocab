from mediavocab.text import (
    strip_diacritics, normalize, fuzzy_ratio, best_match, title_words,
)


def test_strip_diacritics():
    assert strip_diacritics("café") == "cafe"
    assert strip_diacritics("naïve") == "naive"
    assert strip_diacritics("") == ""


def test_normalize_strips_feat():
    assert normalize("Hotline Bling (feat. Drake)") == "hotline bling"
    assert normalize("Song ft. Someone") == "song"


def test_normalize_strips_brackets():
    assert normalize("Title [Remastered 2016]") == "title"


def test_normalize_lowercases_and_collapses_punctuation():
    assert normalize("Hello, World!!!") == "hello world"


def test_fuzzy_ratio_identical():
    assert fuzzy_ratio("Café Society", "cafe society") == 1.0


def test_fuzzy_ratio_empty_pair():
    assert fuzzy_ratio("", "") == 1.0
    assert fuzzy_ratio("x", "") == 0.0


def test_best_match():
    cands = ["The Matrix", "Matrix Reloaded", "Matrix Revolutions"]
    best, score = best_match("The Matrix (1999)", cands)
    assert best == "The Matrix"
    assert score > 0.9


def test_title_words_strips_articles():
    assert title_words("The Lord of the Rings") == ["lord", "of", "rings"]
    # Note: "of" is not in the article list — only definite/indefinite articles are stripped.
