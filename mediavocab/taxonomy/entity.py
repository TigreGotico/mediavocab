"""EntityKind + OrganisationKind — structural type of an Entity. Spec §4.5."""
from enum import Enum


class EntityKind(str, Enum):
    """Classifies the structural type of an entity — what schema it needs."""

    PERSON = "person"
    GROUP = "group"
    ORGANISATION = "organisation"
    SERIES = "series"
    DEVICE = "device"
    OTHER = "other"


class OrganisationKind(str, Enum):
    """Sub-type of EntityKind.ORGANISATION.

    Set when Entity.kind == ORGANISATION; None otherwise.
    """

    LABEL = "label"
    PUBLISHER = "publisher"
    STUDIO = "studio"
    BROADCASTER = "broadcaster"
    DEVELOPER = "developer"
    STREAMING_SERVICE = "streaming_service"
    DISTRIBUTOR = "distributor"
    OTHER = "other"
