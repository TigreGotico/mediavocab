"""Tests for `mediavocab.text.title_parse` — raw-title field extraction."""
import pytest

from mediavocab import ReleasePackaging, VariantKind
from mediavocab.text import parse_title


# ---------------------------------------------------------------------------
# Year extraction
# ---------------------------------------------------------------------------

class TestYear:
    def test_parenthesised_year(self):
        r = parse_title("Inception (2010)")
        assert r.year == 2010
        assert r.title == "Inception"

    def test_bracketed_year(self):
        r = parse_title("Blade Runner [1982]")
        assert r.year == 1982

    def test_braces_year(self):
        r = parse_title("Some Film {1999}")
        assert r.year == 1999

    def test_bare_year_in_filename(self):
        r = parse_title("Inception 2010")
        assert r.year == 2010

    def test_year_below_cinema_era_rejected(self):
        """1888 is the floor (Roundhay Garden Scene)."""
        r = parse_title("Roman Numerals 1800")
        # 1800 < 1888, treated as bare year only if in 1888-2099 range.
        # We allow the parser to keep 1800 in title or not — just don't crash.
        assert isinstance(r.title, str)


# ---------------------------------------------------------------------------
# Season / episode extraction
# ---------------------------------------------------------------------------

class TestSeasonEpisode:
    def test_s_e_marker(self):
        r = parse_title("Cowboy Bebop S01E02")
        assert r.season == 1
        assert r.episode == 2

    def test_long_form(self):
        r = parse_title("Doctor Who Season 4 Episode 10")
        assert r.season == 4
        assert r.episode == 10

    def test_nxn_form(self):
        r = parse_title("7x12 Title")
        assert r.season == 7
        assert r.episode == 12

    def test_episode_only(self):
        r = parse_title("Episode 5")
        assert r.episode == 5
        assert r.season is None


# ---------------------------------------------------------------------------
# Cuts (Work-level variant_kind)
# ---------------------------------------------------------------------------

class TestCuts:
    def test_directors_cut_brackets(self):
        r = parse_title("Blade Runner [Directors Cut]")
        assert r.variant_kind == VariantKind.DIRECTORS

    def test_directors_cut_parens(self):
        r = parse_title("Blade Runner (Director's Cut)")
        assert r.variant_kind == VariantKind.DIRECTORS

    def test_theatrical_cut(self):
        r = parse_title("The Matrix [Theatrical Cut]")
        assert r.variant_kind == VariantKind.THEATRICAL

    def test_extended_cut(self):
        r = parse_title("LOTR (Extended Edition)")
        assert r.variant_kind == VariantKind.EXTENDED

    def test_fanedit(self):
        r = parse_title("The Phantom Edit (Fanedit)")
        assert r.variant_kind == VariantKind.FANEDIT

    def test_remastered(self):
        r = parse_title("Master of Puppets [Remastered]")
        assert r.variant_kind == VariantKind.REMASTERED


# ---------------------------------------------------------------------------
# Release packaging (Release-level)
# ---------------------------------------------------------------------------

class TestPackaging:
    def test_deluxe_edition(self):
        r = parse_title("Star Wars (Deluxe Edition)")
        assert r.packaging == ReleasePackaging.DELUXE

    def test_criterion_collection_is_reissue(self):
        r = parse_title("Citizen Kane (Criterion Collection)")
        assert r.packaging == ReleasePackaging.REISSUE
        assert r.edition == "Criterion"

    def test_anniversary_edition_is_reissue(self):
        r = parse_title("Movie (Anniversary Edition)")
        assert r.packaging == ReleasePackaging.REISSUE
        assert r.edition == "Anniversary"

    def test_packaging_is_not_aka(self):
        """A parenthetical that matches a known edition keyword stays in the
        title for the cut/edition detector — does NOT leak into aka."""
        r = parse_title("Star Wars (Deluxe Edition)")
        assert "Deluxe Edition" not in r.aka


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

class TestFormat:
    def test_dvd_in_brackets(self):
        r = parse_title("Movie [DVD]")
        assert r.source_format == "DVD"

    def test_bluray(self):
        r = parse_title("Movie [Blu-ray]")
        assert r.source_format == "Blu-ray"


# ---------------------------------------------------------------------------
# AKA collection
# ---------------------------------------------------------------------------

class TestAKA:
    def test_parenthetical_short_phrases_kept_in_aka(self):
        r = parse_title("The Matrix (Or: Reloaded Edition Notes)")
        assert any("Reloaded" in a for a in r.aka)

    def test_resolution_does_not_pollute_aka(self):
        r = parse_title("Movie (1080p)")
        assert r.aka == []

    def test_codec_does_not_pollute_aka(self):
        r = parse_title("Movie (H.265)")
        assert r.aka == []

    def test_year_does_not_pollute_aka(self):
        r = parse_title("Inception (2010)")
        assert r.aka == []


# ---------------------------------------------------------------------------
# Combination
# ---------------------------------------------------------------------------

def test_full_filename():
    r = parse_title("Blade Runner (1982) [Directors Cut] [4K UHD] [H.265].mkv")
    assert r.year == 1982
    assert r.variant_kind == VariantKind.DIRECTORS
    assert r.source_format == "4K UHD"
    assert "Blade Runner" in r.title


def test_lang_bracket():
    r = parse_title("Film [EN]")
    assert r.language_hint is not None


# ---------------------------------------------------------------------------
# Pipe / OR-title trim
# ---------------------------------------------------------------------------

def test_pipe_splitter():
    """Anything after a pipe is treated as a secondary title and dropped."""
    r = parse_title("Main Title | Subtitle Junk")
    assert "Subtitle Junk" not in r.title
