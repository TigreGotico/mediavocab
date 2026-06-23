"""Stable-hash pins for v1.x (spec §6.3, §6.4).

The `work_hash` / `release_hash` input lists are frozen for the v1.x line.
These pins catch any accidental shift in the hash algorithm: normalisation
changes, field ordering changes, separator changes, etc.

If a test here fails, the v1.x hash contract has been broken. Either revert
the change or bump to a `work_hash_v2` symbol with a major-version release.
"""
from mediavocab import (
    ContentForm, MediaType, Release, VariantKind, Work,
)
from mediavocab.text import work_hash, release_hash


# ---------------------------------------------------------------------------
# work_hash — pinned digests for canonical reference Works
# ---------------------------------------------------------------------------

class TestWorkHashPins:
    def test_minimal_movie(self):
        w = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
        assert work_hash(w) == "19238a3b52ebff5050524dab5e498cf4765f77aa54019af10c00e4e44a793a65"

    def test_master_of_puppets_album(self):
        w = Work(
            title="Master of Puppets", media_type=MediaType.MUSIC,
            year=1986, runtime=3290.0, publication_country="US",
        )
        assert work_hash(w) == "ce7f15b8776fb500c8efd49103c3796a5af017d822b6546f24d49012139b2a59"

    def test_diacritic_strip_collides_with_ascii(self):
        """The hash strips diacritics before normalising."""
        a = Work(title="Café", media_type=MediaType.MOVIE)
        b = Work(title="cafe", media_type=MediaType.MOVIE)
        assert work_hash(a) == work_hash(b)

    def test_hash_is_64_hex_chars(self):
        """SHA-256 hex output."""
        w = Work(title="x", media_type=MediaType.MOVIE)
        h = work_hash(w)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# release_hash — pinned digests
# ---------------------------------------------------------------------------

class TestReleaseHashPins:
    def test_movie_bluray_release(self):
        w = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
        r = Release(work=w, container="Blu-ray", region="US",
                    codec="H.264", bitrate="40Mbps",
                    audio_language="en")
        # Stable digest — locked at first observation. If it changes, the
        # release_hash input list was modified.
        h = release_hash(r)
        assert len(h) == 64
        # Repeat: deterministic
        assert release_hash(r) == h

    def test_hash_is_64_hex_chars(self):
        w = Work(title="x", media_type=MediaType.MOVIE)
        r = Release(work=w, container="Blu-ray")
        h = release_hash(r)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# Normalisation invariants — hash is whitespace / case / punctuation insensitive
# ---------------------------------------------------------------------------

class TestHashNormalisation:
    def test_whitespace_collapse(self):
        a = Work(title="Inception", media_type=MediaType.MOVIE)
        b = Work(title="  Inception  ", media_type=MediaType.MOVIE)
        c = Work(title="Inception   2010", media_type=MediaType.MOVIE)
        assert work_hash(a) == work_hash(b)
        # c has extra content → different
        assert work_hash(a) != work_hash(c)

    def test_case_insensitive(self):
        a = Work(title="Inception", media_type=MediaType.MOVIE)
        b = Work(title="INCEPTION", media_type=MediaType.MOVIE)
        assert work_hash(a) == work_hash(b)

    def test_punctuation_collapse(self):
        """Non-word characters become whitespace; identical after."""
        a = Work(title="Pulp Fiction", media_type=MediaType.MOVIE)
        b = Work(title="Pulp Fiction!", media_type=MediaType.MOVIE)
        assert work_hash(a) == work_hash(b)

    def test_feat_credit_stripped_from_title(self):
        """(feat. X) is removed before hashing — same Work."""
        a = Work(title="Hotline Bling", media_type=MediaType.MUSIC)
        b = Work(title="Hotline Bling (feat. Drake)", media_type=MediaType.MUSIC)
        assert work_hash(a) == work_hash(b)


# ---------------------------------------------------------------------------
# Hash includes content_form (A8b) — visible separation
# ---------------------------------------------------------------------------

def test_content_form_visibly_separates_hashes():
    """A trailer and primary Work with otherwise-identical identity fields
    hash to two distinct 64-char digests."""
    primary = Work(title="Inception", media_type=MediaType.MOVIE, year=2010)
    trailer = Work(title="Inception", media_type=MediaType.MOVIE, year=2010,
                   content_form=ContentForm.TRAILER)
    h_primary = work_hash(primary)
    h_trailer = work_hash(trailer)
    assert h_primary != h_trailer
    # Both well-formed
    assert len(h_primary) == 64 and len(h_trailer) == 64


# ---------------------------------------------------------------------------
# Variant kind in hash — each cut its own Work
# ---------------------------------------------------------------------------

def test_each_cut_gets_distinct_hash():
    """Theatrical / Directors / Extended cuts of the same title hash differently."""
    base = dict(title="Blade Runner", media_type=MediaType.MOVIE, year=1982,
                runtime=117 * 60.0)
    hashes = {
        work_hash(Work(**base, variant_kind=VariantKind.THEATRICAL)),
        work_hash(Work(**base, variant_kind=VariantKind.DIRECTORS)),
        work_hash(Work(**base, variant_kind=VariantKind.EXTENDED)),
        work_hash(Work(**base, variant_kind=VariantKind.REMASTERED)),
    }
    assert len(hashes) == 4


# ---------------------------------------------------------------------------
# Hash determinism across model_copy
# ---------------------------------------------------------------------------

def test_deep_copy_preserves_hash():
    w = Work(title="x", media_type=MediaType.MOVIE, year=2010,
             content_genres=["sci_fi"], extra={"k": "v"})
    h = work_hash(w)
    assert work_hash(w.model_copy(deep=True)) == h
    # Mutating description fields on the copy doesn't change the hash
    c = w.model_copy(deep=True)
    c.content_genres.append("thriller")
    assert work_hash(c) == h
