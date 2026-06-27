"""PictureFormat — presentation/picture-attribute axis (spec §4.15).

Technical Release attribute (T6); routing-family (A6) — exempt from
identity hashing (``signal_hash`` / ``work_hash``) and from
``compare_signals``.
"""
from mediavocab import (
    MediaType, PictureFormat, Signals, Work, compare_signals, signal_hash,
)
from mediavocab.text import work_hash


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

def test_picture_format_values():
    expected = {
        "black_and_white", "silent", "colorized", "color", "2d", "3d",
        "sd", "hd", "4k", "widescreen", "imax", "other",
    }
    assert {pf.value for pf in PictureFormat} == expected


def test_picture_format_is_str_enum():
    assert PictureFormat.BLACK_AND_WHITE == "black_and_white"
    assert PictureFormat.FOUR_K == "4k"


# ---------------------------------------------------------------------------
# Signals — round-trip + identity exemption (A6)
# ---------------------------------------------------------------------------

def test_signals_default_none():
    assert Signals(title="x").picture_format is None


def test_signals_round_trip():
    s = Signals(title="Metropolis", medium=MediaType.MOVIE,
                picture_format=PictureFormat.SILENT)
    again = Signals.model_validate_json(s.model_dump_json())
    assert again.picture_format is PictureFormat.SILENT


def test_picture_format_excluded_from_compare_signals():
    """Two Signals differing only in picture_format do NOT conflict (A6)."""
    a = Signals(title="Inception", medium=MediaType.MOVIE,
                picture_format=PictureFormat.HD)
    b = Signals(title="Inception", medium=MediaType.MOVIE,
                picture_format=PictureFormat.FOUR_K)
    assert compare_signals(a, b) == []


def test_picture_format_excluded_from_signal_hash():
    a = Signals(title="Inception", medium=MediaType.MOVIE,
                picture_format=PictureFormat.HD)
    b = Signals(title="Inception", medium=MediaType.MOVIE,
                picture_format=PictureFormat.FOUR_K)
    assert signal_hash(a) == signal_hash(b)


# ---------------------------------------------------------------------------
# Work — round-trip + work_hash exemption (T6/A6)
# ---------------------------------------------------------------------------

def test_work_default_none():
    assert Work(title="x", media_type=MediaType.MOVIE).picture_format is None


def test_work_round_trip():
    w = Work(title="Nosferatu", media_type=MediaType.MOVIE,
             picture_format=PictureFormat.BLACK_AND_WHITE)
    again = Work.model_validate_json(w.model_dump_json())
    assert again.picture_format is PictureFormat.BLACK_AND_WHITE


def test_picture_format_excluded_from_work_hash():
    a = Work(title="Inception", media_type=MediaType.MOVIE,
             picture_format=PictureFormat.HD)
    b = Work(title="Inception", media_type=MediaType.MOVIE,
             picture_format=PictureFormat.FOUR_K)
    assert work_hash(a) == work_hash(b)


def test_from_signals_maps_picture_format():
    s = Signals(title="Inception", medium=MediaType.MOVIE,
                picture_format=PictureFormat.IMAX)
    assert Work.from_signals(s).picture_format is PictureFormat.IMAX
