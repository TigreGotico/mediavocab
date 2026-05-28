"""Entity, EntityRef, Membership, Credit. Spec §5.1, §5.2."""
import logging
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mediavocab._iso_date import iso_compare
from mediavocab.taxonomy import (
    EntityKind,
    OrganisationKind,
    MembershipKind,
    TemporalState,
    RelationRole,
    CreditSection,
)


_CFG = ConfigDict(extra="ignore", populate_by_name=True)
_LOG = logging.getLogger(__name__)


class EntityRef(BaseModel):
    """Lightweight reference to an entity (§5.1).

    `localized_names`: list of `(name, ISO 639-1)` tuples for cross-locale
    matching. Not part of the identity hash.
    """

    model_config = _CFG

    name: str
    kind: EntityKind
    external_ids: Dict[str, str] = Field(default_factory=dict)
    localized_names: List[Tuple[str, str]] = Field(default_factory=list)


class Membership(BaseModel):
    """A time-sliced membership of an entity in a group (§5.2).

    Two orthogonal facets (A5):
      - `kind` (MembershipKind): role-shape — MEMBER / TOURING / SESSION.
      - `temporal` (TemporalState): time-state — ACTIVE / ENDED / INACTIVE_GROUP.

    `date_to = None` does NOT mean *current* — check `temporal`.
    """

    model_config = _CFG

    entity: EntityRef
    roles: List[str] = Field(default_factory=list)
    kind: MembershipKind = MembershipKind.MEMBER
    temporal: TemporalState = TemporalState.ACTIVE
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    note: Optional[str] = None

    @model_validator(mode="after")
    def _check(self) -> "Membership":
        if self.temporal == TemporalState.ACTIVE and self.date_to is not None:
            raise ValueError("ACTIVE membership must have date_to=None")
        if (
            self.date_from is not None
            and self.date_to is not None
            and iso_compare(self.date_to, self.date_from) < 0
        ):
            raise ValueError("date_to precedes date_from")
        return self


class Credit(BaseModel):
    """An entity's contribution to a specific Work (§5.2).

    Order in the list is the editorial credit order (poster billing, liner notes).

    `role` is a free-text editorial label (e.g. "Executive Producer", "ADR
    Director"). `relation_role` is the canonical typed role from the taxonomy.
    When both are set they should agree — `role` is the human-readable
    expansion of `relation_role`. A validator logs a WARNING when they visibly
    disagree, but does not reject the record (cross-provider ingestion often
    uses provider-specific labels before normalisation).
    """

    model_config = _CFG

    entity: EntityRef
    role: str
    relation_role: RelationRole
    section: CreditSection = CreditSection.PRINCIPAL
    note: Optional[str] = None

    @model_validator(mode="after")
    def _check_role_consistency(self) -> "Credit":
        if self.role and self.relation_role:
            role_norm = self.role.lower().replace(" ", "_").replace("-", "_")
            rr_val = self.relation_role.value.lower()
            if rr_val not in role_norm and role_norm not in rr_val:
                _LOG.warning(
                    "Credit role mismatch: role=%r does not obviously match "
                    "relation_role=%r — consider aligning them",
                    self.role, self.relation_role.value,
                )
        return self


class Entity(BaseModel):
    """A person, group, organisation, series, or device (§5.2)."""

    model_config = _CFG

    name: str
    kind: EntityKind
    org_kind: Optional[OrganisationKind] = None      # required iff kind == ORGANISATION
    aliases: List[str] = Field(default_factory=list)

    # PERSON-only
    birth_year: Optional[int] = None
    death_year: Optional[int] = None

    # GROUP / SERIES
    memberships: List[Membership] = Field(default_factory=list)

    # Hierarchy
    part_of: Optional[EntityRef] = None

    # Lifecycle
    status: Optional[str] = None
    years_active: List[str] = Field(default_factory=list)
    formed: Optional[str] = None
    disbanded: Optional[str] = None

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> "Entity":
        if self.kind == EntityKind.ORGANISATION and self.org_kind is None:
            raise ValueError("Entity(kind=ORGANISATION) must set org_kind")
        if self.kind != EntityKind.ORGANISATION and self.org_kind is not None:
            raise ValueError("org_kind is only valid for ORGANISATION entities")
        if self.kind != EntityKind.PERSON and (
            self.birth_year is not None or self.death_year is not None
        ):
            raise ValueError("birth_year / death_year are PERSON-only")
        if (
            self.birth_year is not None
            and self.death_year is not None
            and self.death_year < self.birth_year
        ):
            raise ValueError("death_year precedes birth_year")
        return self
