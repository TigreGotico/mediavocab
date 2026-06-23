"""Tests for the `extra` escape hatch (spec §8.3).

Work.extra and Release.extra are Dict[str, Any] — they accept any
JSON-serialisable type. String values remain the most portable choice
for cross-package interop, but typed values (int, bool, list) are
accepted to avoid the stringify/parse round-trip tax.
"""
from mediavocab import (
    Entity, EntityKind, MediaType, OrganisationKind, Release, Work,
)
from mediavocab.text import work_hash, release_hash


# ---------------------------------------------------------------------------
# Type acceptance (§8.3 — Dict[str, Any])
# ---------------------------------------------------------------------------

class TestExtraTypes:
    def test_work_extra_accepts_int(self):
        w = Work(title="x", media_type=MediaType.MOVIE, extra={"year": 1999})
        assert w.extra["year"] == 1999

    def test_work_extra_accepts_list(self):
        w = Work(title="x", media_type=MediaType.MOVIE,
                 extra={"tags": ["a", "b"]})
        assert w.extra["tags"] == ["a", "b"]

    def test_release_extra_accepts_int(self):
        r = Release(work=Work(title="x", media_type=MediaType.MOVIE),
                    extra={"runtime_min": 120})
        assert r.extra["runtime_min"] == 120

    def test_entity_extra_accepts_nested_dict(self):
        e = Entity(name="X", kind=EntityKind.ORGANISATION,
                   org_kind=OrganisationKind.LABEL,
                   extra={"nested": {"foo": "bar"}})
        assert e.extra["nested"]["foo"] == "bar"

    def test_string_values_still_work(self):
        w = Work(title="x", media_type=MediaType.MOVIE,
                 extra={"k1": "v1", "k2": "v2"})
        assert w.extra == {"k1": "v1", "k2": "v2"}


# ---------------------------------------------------------------------------
# Identity-irrelevant (§8.3 rule 3)
# ---------------------------------------------------------------------------

def test_extra_excluded_from_work_hash():
    """No `extra` key participates in `work_hash`."""
    a = Work(title="x", media_type=MediaType.MOVIE)
    b = Work(title="x", media_type=MediaType.MOVIE,
             extra={"provider_thing": "value"})
    assert work_hash(a) == work_hash(b)


def test_extra_excluded_from_release_hash():
    w = Work(title="x", media_type=MediaType.MOVIE)
    a = Release(work=w, container="Blu-ray")
    b = Release(work=w, container="Blu-ray",
                extra={"provider_thing": "value"})
    assert release_hash(a) == release_hash(b)


# ---------------------------------------------------------------------------
# Provider-namespaced keys (§8.3 rule 4)
# ---------------------------------------------------------------------------

def test_provider_namespaced_keys_dont_collide():
    """Two providers writing the same key would collide; the convention is
    to namespace by provider. This is editorial — not enforced by code."""
    w = Work(title="x", media_type=MediaType.MOVIE,
             extra={"bandcamp_band_id": "1234",
                    "audiodb_artist_id": "5678"})
    assert "bandcamp_band_id" in w.extra
    assert "audiodb_artist_id" in w.extra
