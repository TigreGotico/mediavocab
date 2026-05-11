"""Tests for the identity-input primitives (spec §6.1)."""
import pytest

from mediavocab.text import (
    normalise_country,
    normalise_edition,
    normalise_format,
    normalise_language,
    normalise_title,
)


# ---------------------------------------------------------------------------
# normalise_title / normalise_edition (full normalize pipeline)
# ---------------------------------------------------------------------------

class TestTitleAndEdition:
    @pytest.mark.parametrize("s", ["", None])
    def test_empty_or_none_pass_through(self, s):
        assert normalise_title(s) == ""
        assert normalise_edition(s) == ""

    def test_strips_diacritics(self):
        assert normalise_title("Café") == "cafe"

    def test_lowercases(self):
        assert normalise_title("THE MATRIX") == "the matrix"

    def test_strips_feat(self):
        assert "feat" not in normalise_title("Song (feat. Drake)")

    def test_strips_bracketed(self):
        assert normalise_title("Title [Remastered 2016]") == "title"

    def test_edition_alias_pipeline(self):
        """normalise_edition is identical to normalise_title."""
        for s in ("Director's Cut", "Anniversary Edition", "Criterion Collection"):
            assert normalise_edition(s) == normalise_title(s)


# ---------------------------------------------------------------------------
# normalise_format — lowercase, no punctuation, no whitespace
# ---------------------------------------------------------------------------

class TestFormat:
    @pytest.mark.parametrize("inp,expected", [
        ("Blu-ray",   "bluray"),
        ("4K UHD",    "4kuhd"),
        ("320 kbps",  "320kbps"),
        ("H.265",     "h265"),
        ("PS4",       "ps4"),
        ("DVD",       "dvd"),
        ("Vinyl",     "vinyl"),
        ("",          ""),
        (None,        ""),
    ])
    def test_canonical_format_strings(self, inp, expected):
        assert normalise_format(inp) == expected

    def test_format_strips_all_non_alnum(self):
        assert normalise_format("a.b-c d_e@f") == "abcdef"

    def test_format_preserves_digits(self):
        assert normalise_format("v2.0.1") == "v201"


# ---------------------------------------------------------------------------
# normalise_country
# ---------------------------------------------------------------------------

class TestCountry:
    def test_empty_pass_through(self):
        assert normalise_country("") == ""
        assert normalise_country(None) == ""

    def test_alpha2_uppercase(self):
        assert normalise_country("us") == "US"
        assert normalise_country("GB") == "GB"

    def test_country_name_canonicalises(self):
        assert normalise_country("United States") == "US"
        assert normalise_country("united kingdom") == "GB"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            normalise_country("ZZ")


# ---------------------------------------------------------------------------
# normalise_language
# ---------------------------------------------------------------------------

class TestLanguage:
    def test_empty_pass_through(self):
        assert normalise_language("") == ""
        assert normalise_language(None) == ""

    def test_alpha1_passthrough(self):
        assert normalise_language("en") == "en"
        assert normalise_language("EN") == "en"

    def test_alpha3_collapses(self):
        assert normalise_language("eng") == "en"
        assert normalise_language("deu") == "de"

    def test_language_name(self):
        assert normalise_language("English") == "en"
        assert normalise_language("Portuguese") == "pt"

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            normalise_language("zzz")
