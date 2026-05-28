"""mediavocab — reference vocabulary and pydantic data model for media cataloguing.

See `docs/mediavocab_spec.md` for the full design rationale.
"""
from mediavocab.version import __version__

from mediavocab.taxonomy import (
    MediaType,
    PIPELINE_SENTINELS,
    KNOWN_GENRES,
    VariantKind,
    ReleasePackaging,
    EntityKind,
    OrganisationKind,
    RelationRole,
    CreditSection,
    MembershipKind,
    TemporalState,
    ReleaseStatus,
    StreamMode,
    WorkRelationKind,
    ReleaseRelationKind,
    ContentForm,
    ProgrammeFormat,
    AccessibilityKind,
    PlaybackType,
    MEDIA_TYPE_TO_PLAYBACK_TYPE,
    infer_playback_type,
)
from mediavocab.models import (
    EntityRef,
    Membership,
    Credit,
    Appearance,
    Work,
    Release,
    WorkRelation,
    ReleaseRelation,
    Chapter,
    AccessibilityTrack,
    AvailabilityWindow,
    LocalizedTitle,
    COUNTRY_SLOT_FOR,
    Entity,
    Conflict,
    ExternalIds,
    Stream,
    KNOWN_EXTERNAL_IDS,
    License,
    Signals,
    SignalConflict,
    SignalsRole,
    MetadataProvider,
    ProviderMatch,
    ResolutionConflict,
)
from mediavocab.text import (
    MergeStrategy,
    DEFAULT_STRATEGY,
    IdentityConflict,
)

SPEC_VERSION: str = "1.1"

__all__ = [
    "__version__", "SPEC_VERSION",
    # Taxonomy
    "MediaType", "PIPELINE_SENTINELS", "KNOWN_GENRES",
    "VariantKind", "ReleasePackaging",
    "EntityKind", "OrganisationKind",
    "RelationRole", "CreditSection",
    "MembershipKind", "TemporalState",
    "ReleaseStatus", "StreamMode",
    "WorkRelationKind", "ReleaseRelationKind",
    "ContentForm",
    "ProgrammeFormat", "AccessibilityKind",
    "PlaybackType", "MEDIA_TYPE_TO_PLAYBACK_TYPE", "infer_playback_type",
    # Models
    "EntityRef", "Membership", "Credit",
    "Appearance", "Work", "Release", "WorkRelation", "ReleaseRelation",
    "Chapter", "AccessibilityTrack", "AvailabilityWindow", "LocalizedTitle",
    "COUNTRY_SLOT_FOR",
    "Entity",
    "Conflict",
    "ExternalIds", "Stream", "KNOWN_EXTERNAL_IDS",
    "License",
    "Signals", "SignalConflict", "SignalsRole",
    "MetadataProvider", "ProviderMatch", "ResolutionConflict",
    # Merge / identity-conflict surface
    "MergeStrategy", "DEFAULT_STRATEGY", "IdentityConflict",
]
