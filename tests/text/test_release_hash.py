"""Tests for ``release_hash``."""
from mediavocab import (
    AccessibilityTrack, MediaType, Release, StreamMode, VariantKind, Work,
)
from mediavocab.text import release_hash, work_hash


def _movie_work() -> Work:
    return Work(title="Blade Runner", media_type=MediaType.MOVIE,
                year=1982, runtime=117 * 60.0)


def test_same_release_hashes_equal():
    w = _movie_work()
    a = Release(work=w, container="Blu-ray", uri="x://a", region="US")
    b = Release(work=w, container="Blu-ray", uri="x://b", region="US")
    # Different uri / image must not affect identity.
    assert release_hash(a) == release_hash(b)


def test_variant_kind_distinguishes_releases():
    w = _movie_work()
    theatrical = Release(work=w, container="Blu-ray", region="US")
    directors = Release(work=w, container="Blu-ray", region="US",
                        variant_kind=VariantKind.DIRECTORS)
    assert release_hash(theatrical) != release_hash(directors)


def test_container_distinguishes_releases():
    w = _movie_work()
    bd  = Release(work=w, container="Blu-ray", region="US")
    dvd = Release(work=w, container="DVD",     region="US")
    assert release_hash(bd) != release_hash(dvd)


def test_region_distinguishes_releases():
    w = _movie_work()
    us = Release(work=w, container="Blu-ray", region="US")
    jp = Release(work=w, container="Blu-ray", region="JP")
    assert release_hash(us) != release_hash(jp)


def test_audio_language_distinguishes_dubs():
    w = _movie_work()
    en = Release(work=w, container="Blu-ray", audio_language="en")
    fr = Release(work=w, container="Blu-ray", audio_language="fr")
    assert release_hash(en) != release_hash(fr)


def test_accessibility_does_not_affect_hash():
    """AccessibilityTrack list is not identity — the same edition with
    differing subtitle availability is still the same Release."""
    w = _movie_work()
    bare = Release(work=w, container="Blu-ray")
    with_subs = Release(work=w, container="Blu-ray", accessibility=[
        AccessibilityTrack(kind="subtitles", language="en", uri="x"),
    ])
    assert release_hash(bare) == release_hash(with_subs)


def test_stream_mode_does_not_affect_hash():
    """stream_mode is delivery, not identity (spec axiom 4)."""
    w = _movie_work()
    on_demand = Release(work=w, container="Blu-ray",
                        stream_mode=StreamMode.ON_DEMAND)
    live = Release(work=w, container="Blu-ray",
                   stream_mode=StreamMode.LIVE)
    assert release_hash(on_demand) == release_hash(live)


def test_release_hash_changes_with_underlying_work():
    """If the Work changes identity, the Release hash changes too."""
    a = Release(work=Work(title="A", media_type=MediaType.MOVIE), container="Blu-ray")
    b = Release(work=Work(title="B", media_type=MediaType.MOVIE), container="Blu-ray")
    assert release_hash(a) != release_hash(b)


def test_release_hash_includes_work_hash():
    """The release hash must depend on the work hash, not just release fields."""
    w = _movie_work()
    r = Release(work=w, container="Blu-ray", region="US")
    rh = release_hash(r)
    wh = work_hash(w)
    # The work hash is embedded as one of the parts; can't be the same overall.
    assert rh != wh
    # But changing only release fields keeps the work_hash constant.
    r2 = Release(work=w, container="DVD", region="US")
    assert work_hash(r2.work) == wh
    assert release_hash(r2) != rh
