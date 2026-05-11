"""RelationRole, CreditSection, WorkRelationKind, ReleaseRelationKind. Spec §4.6, §4.7, §4.13."""
from enum import Enum


class RelationRole(str, Enum):
    """How an entity participates in a specific Work or Release."""

    CREATOR = "creator"

    # Music
    PERFORMER = "performer"
    COMPOSER = "composer"
    LYRICIST = "lyricist"
    PRODUCER = "producer"
    FEATURING = "featuring"
    REMIXER = "remixer"

    # Film and TV
    DIRECTOR = "director"
    SCREENWRITER = "screenwriter"
    ACTOR = "actor"
    CINEMATOGRAPHER = "cinematographer"
    EDITOR = "editor"

    # Book and comic
    AUTHOR = "author"
    ILLUSTRATOR = "illustrator"
    TRANSLATOR = "translator"
    NARRATOR = "narrator"

    # Podcast and radio
    HOST = "host"
    GUEST = "guest"
    CURATOR = "curator"

    # Game
    DEVELOPER = "developer"
    PORTER = "porter"

    # Release infrastructure
    PUBLISHER = "publisher"
    LABEL = "label"
    DISTRIBUTOR = "distributor"

    OTHER = "other"


class CreditSection(str, Enum):
    """Which section of a Work's credits an entity appears in."""

    PRINCIPAL = "principal"
    GUEST = "guest"
    STAFF = "staff"


class WorkRelationKind(str, Enum):
    """How one Work relates to another (§4.13)."""

    COVERS = "covers"
    SAMPLES = "samples"
    ADAPTED_FROM = "adapted_from"
    SEQUEL_TO = "sequel_to"
    PREQUEL_TO = "prequel_to"
    PART_OF = "part_of"            # ad-hoc thematic / curatorial grouping
    LIVE_VERSION = "live_version"
    REMIX_OF = "remix_of"
    SOUNDTRACK_FOR = "soundtrack_for"
    BONUS_FOR = "bonus_for"
    FANEDIT_OF = "fanedit_of"
    DLC_FOR = "dlc_for"
    EXPANSION_OF = "expansion_of"
    DERIVED_FROM = "derived_from"   # generic catch-all; cross-channel reissues, remasters


class ReleaseRelationKind(str, Enum):
    """How one Release relates to another (§4.13)."""

    SUPERSEDES = "supersedes"
    PORT_OF = "port_of"
    MIRROR_OF = "mirror_of"
    DERIVED_FROM = "derived_from"
