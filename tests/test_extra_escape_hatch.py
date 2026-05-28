"""Tests for the `extra` escape hatch (spec §8.3)."""
import pytest

from mediavocab import (
    Entity, EntityKind, MediaType, OrganisationKind, Release, Work,
)
from mediavocab.text import work_hash, release_hash


# ---------------------------------------------------------------------------
# Strings-only invariant (§8.3 rule 1)
# ---------------------------------------------------------------------------

class TestStringsOnly:
    def test_work_extra_rejects_int(self):
        with pytest.raises(ValueError):
            Work(title="x", media_type=MediaType.MOVIE, extra={"year": 1999})

    def test_work_extra_rejects_list(self):
        with pytest.raises(ValueError):
            Work(title="x", media_type=MediaType.MOVIE,
                 extra={"tags": ["a", "b"]})

    def test_release_extra_rejects_int(self):
        with pytest.raises(ValueError):
            Release(work=Work(title="x", media_type=MediaType.MOVIE),
                    extra={"runtime_min": 120})

    def test_entity_extra_rejects_dict(self):
        with pytest.raises(ValueError):
            Entity(name="X", kind=EntityKind.ORGANISATION,
                   org_kind=OrganisationKind.LABEL,
                   extra={"nested": {"foo": "bar"}})

    def test_string_values_accepted(self):
        w = Work(title="x", media_type=MediaType.MOVIE,
                 extra={"k1": "v1", "k2": "v2"})
        assert w.extra == {"k1": "v1", "k2": "v2"}

    def test_encode_numbers_as_decimal_strings(self):
        """Spec §8.3 — encode numbers as their decimal representation."""
        w = Work(title="x", media_type=MediaType.MOVIE,
                 extra={"runtime_min": "120", "rating": "8.5"})
        assert w.extra["runtime_min"] == "120"
        assert w.extra["rating"] == "8.5"

    def test_encode_lists_as_comma_joined_strings(self):
        """Spec §8.3 — encode lists as comma-joined strings."""
        w = Work(title="x", media_type=MediaType.MOVIE,
                 extra={"tags": "a,b,c"})
        assert w.extra["tags"].split(",") == ["a", "b", "c"]


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
