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
    CURATOR = "curator"   # selected/ordered other people's works (playlists, anthologies)

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
    BONUS_FOR = "bonus_for"
    FANEDIT_OF = "fanedit_of"
    DLC_FOR = "dlc_for"             # game DLC tied to a base game
    EXPANSION_OF = "expansion_of"    # standalone expansion (still a separate Work)


class ReleaseRelationKind(str, Enum):
    """How one Release relates to another. Spec §6.

    Parallel to ``WorkRelationKind`` but for Release-level lineage:
    remasters supersede prior remasters, ports / DLC / re-issues
    chain through release time.
    """

    SUPERSEDES = "supersedes"        # this Release replaces an earlier one (e.g. newer remaster)
    REMASTER_OF = "remaster_of"      # explicit remaster lineage
    REISSUE_OF = "reissue_of"        # later commercial release of the same edition
    PORT_OF = "port_of"              # platform port of the same base game / IF
    DERIVED_FROM = "derived_from"    # generic "this Release is derived from that one"
