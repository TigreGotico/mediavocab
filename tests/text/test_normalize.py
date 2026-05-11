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


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_normalize_empty_string():
    assert normalize("") == ""


def test_normalize_handles_unicode_quote_chars():
    """Smart quotes / em-dashes get normalised away as non-word characters."""
    assert normalize("Hello — World") == "hello world"
    assert normalize("It's “fine”") == "it s fine"


def test_strip_diacritics_preserves_non_european_scripts():
    """Japanese, Cyrillic, etc. characters should pass through (no combining marks)."""
    assert strip_diacritics("東京") == "東京"
    assert strip_diacritics("Москва") == "Москва"


def test_fuzzy_ratio_unicode_normalised():
    """NFKD-normalised diacritics fold."""
    assert fuzzy_ratio("Pokémon", "Pokemon") == 1.0
    assert fuzzy_ratio("Beyoncé", "Beyonce") == 1.0


def test_best_match_empty_candidates():
    best, score = best_match("anything", [])
    assert best == ""
    assert score == 0.0


def test_best_match_picks_strongest():
    """When candidates differ in strength, the strongest wins."""
    best, score = best_match("Inception",
                             ["Reception", "Inception", "Inception 2"])
    assert best == "Inception"
    assert score == 1.0


def test_title_words_filters_articles_multiple_languages():
    """Stopword list covers EN, DE, FR, ES, IT, PT articles."""
    assert "the" not in title_words("the cat")
    assert "der" not in title_words("der Mann")
    assert "le" not in title_words("le chat")
    assert "el" not in title_words("el gato")


def test_normalize_strips_feat_at_end():
    """feat. credits stripped wherever they appear."""
    assert "feat" not in normalize("Song feat. Drake")
    assert "ft" not in normalize("Song ft. Drake")
