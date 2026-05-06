"""EntityKind — structural type of an Entity. Spec §4.3."""
from enum import Enum


class EntityKind(str, Enum):
    """Classifies the structural type of an entity — what schema it needs —
    not its professional identity.
    """

    PERSON = "person"
    GROUP = "group"
    ORGANISATION = "organisation"
    SERIES = "series"
    DEVICE = "device"
    EVENT = "event"
    OTHER = "other"
