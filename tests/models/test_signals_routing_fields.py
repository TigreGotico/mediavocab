"""Signals routing-hint fields: ``programme_format`` and ``accessibility``.

Both are routing-family (A6) — round-trip serialisable, but exempt from
identity hashing (``signal_hash``) and from ``compare_signals``. Mirrors the
``picture_format`` exemption tests (``tests/taxonomy/test_picture_format.py``).
"""
from mediavocab import (
    MediaType, ProgrammeFormat, AccessibilityKind,
    Signals, Work, compare_signals, signal_hash,
)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

def test_signals_defaults():
    s = Signals(title="x")
    assert s.programme_format is None
    assert s.accessibility == []


# ---------------------------------------------------------------------------
# programme_format — round-trip + identity exemption (A6)
# ---------------------------------------------------------------------------

def test_programme_format_round_trip():
    s = Signals(title="Cosmos", medium=MediaType.EPISODIC_SERIES,
                programme_format=ProgrammeFormat.DOCUMENTARY)
    again = Signals.model_validate_json(s.model_dump_json())
    assert again.programme_format is ProgrammeFormat.DOCUMENTARY


def test_programme_format_excluded_from_compare_signals():
    a = Signals(title="Cosmos", medium=MediaType.EPISODIC_SERIES,
                programme_format=ProgrammeFormat.DOCUMENTARY)
    b = Signals(title="Cosmos", medium=MediaType.EPISODIC_SERIES,
                programme_format=ProgrammeFormat.NEWS)
    assert compare_signals(a, b) == []


def test_programme_format_excluded_from_signal_hash():
    a = Signals(title="Cosmos", programme_format=ProgrammeFormat.DOCUMENTARY)
    b = Signals(title="Cosmos", programme_format=ProgrammeFormat.NEWS)
    assert signal_hash(a) == signal_hash(b)


def test_from_signals_maps_programme_format():
    s = Signals(title="Cosmos", medium=MediaType.EPISODIC_SERIES,
                programme_format=ProgrammeFormat.DOCUMENTARY)
    assert Work.from_signals(s).programme_format is ProgrammeFormat.DOCUMENTARY


# ---------------------------------------------------------------------------
# accessibility — round-trip + identity exemption (A6); no Work target
# ---------------------------------------------------------------------------

def test_accessibility_round_trip():
    s = Signals(title="Nosferatu", medium=MediaType.MOVIE,
                accessibility=[AccessibilityKind.SUBTITLES,
                               AccessibilityKind.DUBBED])
    again = Signals.model_validate_json(s.model_dump_json())
    assert again.accessibility == [AccessibilityKind.SUBTITLES,
                                   AccessibilityKind.DUBBED]


def test_accessibility_excluded_from_compare_signals():
    a = Signals(title="Nosferatu", medium=MediaType.MOVIE,
                accessibility=[AccessibilityKind.SUBTITLES])
    b = Signals(title="Nosferatu", medium=MediaType.MOVIE,
                accessibility=[AccessibilityKind.SIGN_LANGUAGE])
    assert compare_signals(a, b) == []


def test_accessibility_excluded_from_signal_hash():
    a = Signals(title="Nosferatu", accessibility=[AccessibilityKind.SUBTITLES])
    b = Signals(title="Nosferatu", accessibility=[AccessibilityKind.DUBBED])
    assert signal_hash(a) == signal_hash(b)


def test_from_signals_drops_accessibility():
    """Accessibility lives on Release as rich tracks — the Work has no
    kind-list field, so the Signals hint is dropped (no crash)."""
    s = Signals(title="Nosferatu", medium=MediaType.MOVIE,
                accessibility=[AccessibilityKind.SUBTITLES])
    w = Work.from_signals(s)
    assert not hasattr(w, "accessibility") or getattr(w, "accessibility", None) in (None, [])
