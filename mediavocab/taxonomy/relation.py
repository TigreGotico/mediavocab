"""RelationRole, CreditSection, WorkRelationKind. Spec §4.4, §4.6, §6."""
from enum import Enum


class RelationRole(str, Enum):
    """How an entity participates in a specific Work or Release."""

    CREATOR = "creator"

    PERFORMER = "performer"
    COMPOSER = "composer"
    LYRICIST = "lyricist"
    PRODUCER = "producer"
    FEATURING = "featuring"
    REMIXER = "remixer"

    DIRECTOR = "director"
    SCREENWRITER = "screenwriter"
    ACTOR = "actor"
    CINEMATOGRAPHER = "cinematographer"
    EDITOR = "editor"

    AUTHOR = "author"
    ILLUSTRATOR = "illustrator"
    TRANSLATOR = "translator"
    NARRATOR = "narrator"

    HOST = "host"
    GUEST = "guest"

    DEVELOPER = "developer"
    PORTER = "porter"

    PUBLISHER = "publisher"
    LABEL = "label"
    DISTRIBUTOR = "distributor"

    OTHER = "other"


class CreditSection(str, Enum):
    """Which section of a release's credits an entity appears in."""

    PRINCIPAL = "principal"
    GUEST = "guest"
    STAFF = "staff"


class WorkRelationKind(str, Enum):
    """How one Work relates to another. Spec §6."""

    COVERS = "covers"
    SAMPLES = "samples"
    ADAPTED_FROM = "adapted_from"
    SEQUEL_TO = "sequel_to"
    PREQUEL_TO = "prequel_to"
    PART_OF = "part_of"
    LIVE_VERSION = "live_version"
    REMIX_OF = "remix_of"
    SOUNDTRACK_FOR = "soundtrack_for"
