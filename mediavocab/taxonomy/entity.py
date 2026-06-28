"""EntityKind + OrganisationKind — structural type of an Entity (spec: A1/A5, §4.5)."""
from enum import Enum


class EntityKind(str, Enum):
    """Structural type of the third identity, an Entity (spec: §1.3/§4.5).

    Values earn their place by the A1 test applied to entities: a kind earns a
    value when it needs a different schema (PERSON has birth/death years, GROUP
    has memberships, ORGANISATION has org_kind). SERIES and DEVICE are admitted
    by A3 — a container and a delivery channel are not Works.
    """

    PERSON = "person"
    GROUP = "group"
    ORGANISATION = "organisation"
    SERIES = "series"        # container, not a Work (A3)
    DEVICE = "device"        # delivery channel, not a Work (A3)
    OTHER = "other"


class OrganisationKind(str, Enum):
    """Sub-type of EntityKind.ORGANISATION (spec: A1, §4.5).

    Discriminates legal entities that share a schema but differ in role within
    the media graph. Set when Entity.kind == ORGANISATION; None otherwise — the
    Entity validator rejects org_kind on a non-ORGANISATION and warns (not
    rejects) on an ORGANISATION with no org_kind yet (A9-adjacent: incomplete,
    not wrong).
    """

    LABEL = "label"
    PUBLISHER = "publisher"
    STUDIO = "studio"
    BROADCASTER = "broadcaster"
    NETWORK = "network"          # umbrella grouping multiple broadcasters under shared branding
    DEVELOPER = "developer"
    STREAMING_SERVICE = "streaming_service"
    DISTRIBUTOR = "distributor"
    OTHER = "other"
