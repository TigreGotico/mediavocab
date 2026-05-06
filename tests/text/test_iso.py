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
