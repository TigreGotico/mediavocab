"""mediavocab — reference vocabulary and pydantic data model for media cataloguing.

See `mediavocab_spec.md` for the full design rationale.
"""
from mediavocab.version import __version__

from mediavocab.taxonomy import (
    MediaType,
    VariantKind,
    EntityKind,
    RelationRole,
    CreditSection,
    MembershipStatus,
    ReleaseStatus,
    StreamMode,
    WorkRelationKind,
)
from mediavocab.models import (
    EntityRef,
    Membership,
    Credit,
    Appearance,
    Work,
    Release,
    WorkRelation,
    Entity,
    Conflict,
)

__all__ = [
    "__version__",
    "MediaType",
    "VariantKind",
    "EntityKind",
    "RelationRole",
    "CreditSection",
    "MembershipStatus",
    "ReleaseStatus",
    "StreamMode",
    "WorkRelationKind",
    "EntityRef",
    "Membership",
    "Credit",
    "Appearance",
    "Work",
    "Release",
    "WorkRelation",
    "Entity",
    "Conflict",
]
