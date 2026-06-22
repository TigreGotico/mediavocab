"""RelationRole, CreditSection, WorkRelationKind, ReleaseRelationKind. Spec §4.6, §4.7, §4.13.

Every value in these enums is admitted by A9: a relation kind earns its place
only when (a) the connection is not already implied by an identity field and
(b) it is not subsumed by an existing kind of the same family. Relation kinds
are navigation/description, never identity (A6) — keep them non-redundant.
"""
from enum import Enum


class RelationRole(str, Enum):
    """How an entity participates in a specific Work or Release (A9)."""

    CREATOR = "creator"

    # Music
    PERFORMER = "performer"
    COMPOSER = "composer"
    LYRICIST = "lyricist"
    PRODUCER = "producer"
    FEATURING = "featuring"
    REMIXER = "remixer"
    CONDUCTOR = "conductor"     # leads orchestral performance — not the composer
    ARRANGER = "arranger"       # re-orchestrates an existing composition
    DJ = "dj"                   # selects and mixes a continuous set

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
    """How one Work relates to another (§4.13). Admitted by A9 — each kind links
    to a *different* Work and is not implied by an identity field (e.g. there is
    no ``EPISODE_OF``: ``season``/``episode``/``series_title`` already carry it)."""

    COVERS = "covers"
    SAMPLES = "samples"
    ADAPTED_FROM = "adapted_from"
    SEQUEL_TO = "sequel_to"
    PREQUEL_TO = "prequel_to"
    PART_OF = "part_of"            # ad-hoc thematic / curatorial grouping
    LIVE_VERSION = "live_version"
    REMIX_OF = "remix_of"
    MIX_OF = "mix_of"               # a DJ set / continuous mix sequences this source Work
    SOUNDTRACK_FOR = "soundtrack_for"
    BONUS_FOR = "bonus_for"
    TRAILER_FOR = "trailer_for"     # promo cut (ContentForm.TRAILER) → the work it promotes
    REACTION_TO = "reaction_to"     # commentary (ContentForm.REACTION) → the work it reacts to
    CLIP_OF = "clip_of"             # short excerpt (ContentForm.EXCERPT/SOCIAL_CLIP) → source work
    FANEDIT_OF = "fanedit_of"
    DLC_FOR = "dlc_for"
    EXPANSION_OF = "expansion_of"
    DERIVED_FROM = "derived_from"   # generic catch-all; cross-channel reissues, remasters


class ReleaseRelationKind(str, Enum):
    """How one Release relates to another (§4.13). Admitted by A9 — a more
    specific kind (``REMASTER_OF`` vs ``DERIVED_FROM``) earns its place only when
    consumers traverse it as a distinct edge."""

    SUPERSEDES = "supersedes"
    PORT_OF = "port_of"
    MIRROR_OF = "mirror_of"
    REMASTER_OF = "remaster_of"   # remastered edition of an earlier release (no obsolescence)
    REISSUE_OF = "reissue_of"     # re-release of an earlier edition (no obsolescence)
    DERIVED_FROM = "derived_from"
