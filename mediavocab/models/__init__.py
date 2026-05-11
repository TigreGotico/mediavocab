"""Pydantic v2 models. Requires pydantic>=2."""
from mediavocab.models.entity import EntityRef, Membership, Credit, Entity
from mediavocab.models.work import (
    Appearance, Work, Release, WorkRelation, ReleaseRelation,
    Chapter, AccessibilityTrack, AvailabilityWindow, LocalizedTitle,
    Programme, Schedule, COUNTRY_SLOT_FOR,
)
from mediavocab.models.conflict import Conflict
from mediavocab.models.external_ids import ExternalIds, Stream
from mediavocab.models.license import (
    License,
    is_open as license_is_open,
    is_public_domain as license_is_public_domain,
    requires_attribution as license_requires_attribution,
    allows_commercial as license_allows_commercial,
    allows_derivatives as license_allows_derivatives,
    allows_share_alike as license_allows_share_alike,
)
from mediavocab.models.signals import (
    Signals, SignalConflict,
    compare_signals, merge_signals, match_quality, signal_hash,
)
from mediavocab.models.protocols import (
    MetadataProvider, ProviderMatch, ResolutionConflict, provider_matches,
)

__all__ = [
    "EntityRef", "Membership", "Credit", "Entity",
    "Appearance", "Work", "Release", "WorkRelation", "ReleaseRelation",
    "Chapter", "AccessibilityTrack", "AvailabilityWindow", "LocalizedTitle",
    "Programme", "Schedule", "COUNTRY_SLOT_FOR",
    "Conflict",
    "ExternalIds", "Stream",
    "License",
    "license_is_open", "license_is_public_domain", "license_requires_attribution",
    "license_allows_commercial", "license_allows_derivatives",
    "license_allows_share_alike",
    "Signals", "SignalConflict",
    "compare_signals", "merge_signals", "match_quality", "signal_hash",
    "MetadataProvider", "ProviderMatch", "ResolutionConflict",
    "provider_matches",
]
