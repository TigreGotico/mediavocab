"""Entity, EntityRef, Membership, Credit. Spec §5.1, §5.2, §5.3, §5.7."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from mediavocab.taxonomy import (
    EntityKind,
    MembershipStatus,
    RelationRole,
    CreditSection,
)


_CFG = ConfigDict(extra="ignore", populate_by_name=True)


class EntityRef(BaseModel):
    """Lightweight reference to an entity. Pointer, not a full record."""

    model_config = _CFG

    name: str
    kind: EntityKind
    external_ids: Dict[str, str] = Field(default_factory=dict)


class Membership(BaseModel):
    """A time-sliced membership of an entity in a group.

    `date_to=None` does NOT mean current — check `status` (spec §4.5).
    """

    model_config = _CFG

    entity: EntityRef
    roles: List[str] = Field(default_factory=list)
    status: MembershipStatus
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    note: Optional[str] = None


class Credit(BaseModel):
    """An entity's contribution to a specific Work or Release.

    `position` (1-based) records editorial credit ordering within a
    `(section, relation_role)` group — film opening titles, music liner
    notes, book co-author orderings. List ordering alone is not reliable
    across JSON round-trips and dict-based merges; `position` is.
    """

    model_config = _CFG

    entity: EntityRef
    role: str
    relation_role: RelationRole
    section: CreditSection = CreditSection.PRINCIPAL
    position: Optional[int] = None
    note: Optional[str] = None


class Entity(BaseModel):
    """A person, group, organisation, series, or device that participates in
    or routes Works. Has no `media_type` — entities cannot be played.
    """

    model_config = _CFG

    name: str
    kind: EntityKind
    aliases: List[str] = Field(default_factory=list)

    memberships: List[Membership] = Field(default_factory=list)

    part_of: Optional[EntityRef] = None

    status: Optional[str] = None
    years_active: List[str] = Field(default_factory=list)
    formed: Optional[str] = None
    disbanded: Optional[str] = None

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)
