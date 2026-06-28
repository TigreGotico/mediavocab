"""Taxonomy completeness invariants.

These catch the failure mode where a new taxonomy value is added but a parallel
table that must cover it is forgotten — e.g. a new MediaType without a hash
quantum (A1), which would make its identity hashing undefined. Adding a value
without wiring its companions fails here instead of shipping a half-defined type.
"""
from mediavocab import (
    MediaType,
    PIPELINE_SENTINELS,
    MEDIA_TYPE_TO_PLAYBACK_TYPE,
    MEDIA_TYPE_TO_STRUCTURE,
)
from mediavocab.text.compare import RUNTIME_HASH_QUANTUM_S


CONCRETE_MEDIA_TYPES = [m for m in MediaType if m not in PIPELINE_SENTINELS]


def test_every_concrete_media_type_has_a_runtime_quantum():
    """A1: every concrete MediaType carries a comparison tolerance (the hash
    quantum). A type without one has undefined identity hashing."""
    missing = [m.value for m in CONCRETE_MEDIA_TYPES if m not in RUNTIME_HASH_QUANTUM_S]
    assert not missing, f"MediaType(s) missing a RUNTIME_HASH_QUANTUM_S entry: {missing}"


def test_quantum_table_has_no_sentinels():
    """Sentinels never reach a Work (T8), so they must not appear in the
    runtime-quantum table."""
    sentinels = [m.value for m in PIPELINE_SENTINELS if m in RUNTIME_HASH_QUANTUM_S]
    assert not sentinels, f"pipeline sentinels leaked into the quantum table: {sentinels}"


def test_every_concrete_media_type_maps_to_a_playback_type():
    """Each concrete MediaType resolves to a PlaybackType (routing)."""
    missing = [m.value for m in CONCRETE_MEDIA_TYPES if m not in MEDIA_TYPE_TO_PLAYBACK_TYPE]
    assert not missing, f"MediaType(s) missing a MEDIA_TYPE_TO_PLAYBACK_TYPE entry: {missing}"


def test_every_concrete_media_type_maps_to_a_structure():
    """Each concrete MediaType resolves to a Structure (derived routing axis)."""
    missing = [m.value for m in CONCRETE_MEDIA_TYPES if m not in MEDIA_TYPE_TO_STRUCTURE]
    assert not missing, f"MediaType(s) missing a MEDIA_TYPE_TO_STRUCTURE entry: {missing}"


def test_structure_table_covers_every_media_type_including_sentinels():
    """The structure table is exhaustive over the whole MediaType enum (the
    map is also consulted for pipeline sentinels, which resolve to UNKNOWN)."""
    missing = [m.value for m in MediaType if m not in MEDIA_TYPE_TO_STRUCTURE]
    assert not missing, f"MediaType(s) missing a MEDIA_TYPE_TO_STRUCTURE entry: {missing}"
