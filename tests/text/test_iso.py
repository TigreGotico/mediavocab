import pytest

from mediavocab.text.iso import (
    validate_language, validate_country,
    normalize_language, normalize_country,
)


def test_validate_language_alpha2():
    assert validate_language("en") == "en"
    assert validate_language("EN") == "en"


def test_validate_language_alpha3_collapses():
    assert validate_language("eng") == "en"
    assert validate_language("deu") == "de"


def test_validate_language_invalid():
    with pytest.raises(ValueError):
        validate_language("zzz")


def test_validate_country():
    assert validate_country("us") == "US"
    assert validate_country("GB") == "GB"


def test_validate_country_invalid():
    with pytest.raises(ValueError):
        validate_country("ZZ")


def test_normalize_language_full_name():
    assert normalize_language("English") == "en"
    assert normalize_language("Portuguese") == "pt"


def test_normalize_country_full_name():
    code = normalize_country("United States")
    assert code == "US"
    assert normalize_country("gb") == "GB"


# ---------------------------------------------------------------------------
# Empty / whitespace / case edge cases
# ---------------------------------------------------------------------------

def test_validate_language_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_language("")


def test_validate_country_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        validate_country("")


def test_normalize_language_empty_raises():
    with pytest.raises(ValueError):
        normalize_language("")


def test_normalize_country_empty_raises():
    with pytest.raises(ValueError):
        normalize_country("")


def test_normalize_language_strips_whitespace():
    assert normalize_language("  en  ") == "en"
    assert normalize_language("  English  ") == "en"


def test_normalize_country_strips_whitespace():
    assert normalize_country("  US  ") == "US"
    assert normalize_country("  United States  ") == "US"


def test_normalize_language_case_insensitive_name():
    assert normalize_language("ENGLISH") == "en"
    assert normalize_language("portuguese") == "pt"


def test_normalize_country_case_insensitive_name():
    assert normalize_country("UNITED STATES") == "US"
    assert normalize_country("united kingdom") == "GB"


def test_validate_language_alpha3_variants():
    """Both bibliographic and terminological alpha-3 codes collapse to alpha-2."""
    # German: 'deu' (terminological) and 'ger' (bibliographic) both → 'de'
    assert validate_language("deu") == "de"
    # French: 'fra' / 'fre' both → 'fr'
    assert validate_language("fra") == "fr"


def test_normalize_language_alpha3_passthrough():
    """normalize_language accepts 3-letter codes and resolves to 2-letter."""
    assert normalize_language("eng") == "en"
    assert normalize_language("fra") == "fr"


def test_normalize_country_rejects_3_letter():
    """ISO 3166-1 alpha-3 is not supported — only alpha-2."""
    with pytest.raises(ValueError):
        normalize_country("USA")     # alpha-3 form not recognised by name lookup
