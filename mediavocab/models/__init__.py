"""Pydantic v2 models. Requires pydantic>=2 (spec §3.2)."""
from mediavocab.models.entity import EntityRef, Membership, Credit, Entity
from mediavocab.models.work import (
    Appearance, Work, Release, WorkRelation, Chapter, AccessibilityTrack,
)
from mediavocab.models.conflict import Conflict
from mediavocab.models.external_ids import ExternalIds, Stream
from mediavocab.models.signals import (
    Signals, SignalConflict,
    compare_signals, merge_signals, match_quality, signal_hash,
)
from mediavocab.models.protocols import (
    MetadataProvider, ProviderMatch, ResolutionConflict, provider_matches,
)

__all__ = [
    "EntityRef", "Membership", "Credit", "Entity",
    "Appearance", "Work", "Release", "WorkRelation",
    "Chapter", "AccessibilityTrack",
    "Conflict",
    "ExternalIds", "Stream",
    "Signals", "SignalConflict",
    "compare_signals", "merge_signals", "match_quality", "signal_hash",
    "MetadataProvider", "ProviderMatch", "ResolutionConflict",
    "provider_matches",
]
