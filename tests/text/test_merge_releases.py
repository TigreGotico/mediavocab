"""Tests for `merge_releases` — combine partial Release records (§6.6)."""
import pytest

from mediavocab import (
    AccessibilityKind, AccessibilityTrack, AvailabilityWindow, Chapter,
    EntityKind, EntityRef, MediaType, Release, ReleasePackaging,
    ReleaseStatus, StreamMode, Work,
)
from mediavocab.text import merge_releases


def _movie():
    return Work(title="Blade Runner", media_type=MediaType.MOVIE,
                year=1982, production_country="US")


def test_merge_releases_zero_args_raises():
    with pytest.raises(ValueError, match="at least one"):
        merge_releases()


def test_merge_releases_single_returns_deep_copy():
    r = Release(work=_movie(), container="Blu-ray", region="US")
    m = merge_releases(r)
    assert m == r
    assert m is not r


def test_merge_releases_first_non_empty_wins_on_scalars():
    """A provider with `license="all_rights_reserved"` wins over an empty
    later provider on the same field."""
    w = _movie()
    a = Release(work=w, container="Blu-ray", region="US",
                license="all_rights_reserved")
    b = Release(work=w, container="Blu-ray", region="US",
                packaging=ReleasePackaging.DELUXE)
    m = merge_releases(a, b)
    assert m.license is not None
    assert m.license.identifier == "all_rights_reserved"
    assert m.packaging is ReleasePackaging.DELUXE


def test_merge_releases_unions_subtitle_languages():
    w = _movie()
    a = Release(work=w, container="Blu-ray", subtitle_languages=["en", "fr"])
    b = Release(work=w, container="Blu-ray", subtitle_languages=["fr", "es", "de"])
    m = merge_releases(a, b)
    # Union preserves order, no duplicates
    assert m.subtitle_languages == ["en", "fr", "es", "de"]


def test_merge_releases_unions_regions_available():
    w = _movie()
    a = Release(work=w, container="Blu-ray", region_locked=True,
                regions_available=["US", "CA"])
    b = Release(work=w, container="Blu-ray", region_locked=True,
                regions_available=["CA", "GB"])
    m = merge_releases(a, b)
    assert set(m.regions_available) == {"US", "CA", "GB"}


def test_merge_releases_takes_chapters_from_incoming_when_base_empty():
    w = _movie()
    a = Release(work=w, container="Blu-ray")
    b = Release(work=w, container="Blu-ray", chapters=[
        Chapter(offset=0.0, title="Prologue"),
        Chapter(offset=300.0, title="Ch 1"),
    ])
    m = merge_releases(a, b)
    assert len(m.chapters) == 2


def test_merge_releases_takes_accessibility_from_incoming():
    w = _movie()
    a = Release(work=w, container="Blu-ray")
    b = Release(work=w, container="Blu-ray", accessibility=[
        AccessibilityTrack(kind=AccessibilityKind.SUBTITLES,
                           language="en", uri="x.vtt"),
    ])
    m = merge_releases(a, b)
    assert len(m.accessibility) == 1


def test_merge_releases_takes_availability_windows_from_incoming():
    w = _movie()
    a = Release(work=w, container="Blu-ray")
    b = Release(work=w, container="Blu-ray", availability_windows=[
        AvailabilityWindow(start="2025-01-01", end="2026-01-01"),
    ])
    m = merge_releases(a, b)
    assert len(m.availability_windows) == 1


def test_merge_releases_preserves_base_chapters_when_non_empty():
    """When base already has chapters, do NOT overwrite with incoming."""
    w = _movie()
    a = Release(work=w, container="Blu-ray", chapters=[
        Chapter(offset=0.0, title="Original"),
    ])
    b = Release(work=w, container="Blu-ray", chapters=[
        Chapter(offset=0.0, title="Different"),
    ])
    m = merge_releases(a, b)
    assert m.chapters[0].title == "Original"


def test_merge_releases_combines_label_and_distributor():
    """Scalar EntityRef fields: first non-None wins."""
    w = _movie()
    label = EntityRef(name="Warner", kind=EntityKind.ORGANISATION)
    distributor = EntityRef(name="Amazon", kind=EntityKind.ORGANISATION)
    a = Release(work=w, container="Blu-ray", label=label)
    b = Release(work=w, container="Blu-ray", distributor=distributor)
    m = merge_releases(a, b)
    assert m.label is not None and m.label.name == "Warner"
    assert m.distributor is not None and m.distributor.name == "Amazon"


def test_merge_releases_extra_dict_first_writer_wins():
    w = _movie()
    a = Release(work=w, container="Blu-ray",
                extra={"src": "imdb", "rating": "R"})
    b = Release(work=w, container="Blu-ray",
                extra={"src": "tmdb", "year": "1982"})
    m = merge_releases(a, b)
    # a is base; on key collision (src), a wins
    assert m.extra["src"] == "imdb"
    assert m.extra["rating"] == "R"
    assert m.extra["year"] == "1982"
