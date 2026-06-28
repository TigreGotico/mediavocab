"""RelationRole, CreditSection, WorkRelationKind, ReleaseRelationKind
(spec: A9, §4.6/§4.7/§4.13).

Every relation value is admitted by A9: a kind earns its place only when (a)
the connection is not already implied by an identity field and (b) it is not
subsumed by an existing kind of the same family. Relation kinds are
navigation/description, never identity (A6) — keep them non-redundant.
"""
from enum import Enum


class RelationRole(str, Enum):
    """How an entity participates in a specific Work or Release (spec: A9, §4.6).

    A role earns a value when consumers route on it as a distinct contribution
    and no existing value subsumes it (A9); CREATOR is the generic fallback (A2,
    not an absence value). The film/music/book/game groupings reflect T5. No
    CHANNEL value: a channel is an Entity or a Work, not a participation (T9).
    """

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
    """Which section of a Work's credits an entity appears in (spec: A8, §4.7).

    Admitted by A8: humans treat billed principals, guests, and back-of-house
    staff as three different kinds of credit, and no combination of RelationRole
    + entity.kind separates them. Description-family (§1.5) — editorial billing,
    never identity.
    """

    PRINCIPAL = "principal"
    GUEST = "guest"
    STAFF = "staff"


class WorkRelationKind(str, Enum):
    """How one Work relates to another (spec: A9, §4.13). Admitted by A9 — each
    kind links to a *different* Work and is not implied by an identity field
    (e.g. no ``EPISODE_OF``: ``season``/``episode``/``series_title`` already
    carry it, A9(a)). Navigation/description, never identity (A6)."""

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
    """How one Release relates to another (spec: A9, §4.13). Admitted by A9(b) —
    a more specific kind (``REMASTER_OF``/``REISSUE_OF`` vs ``SUPERSEDES``) earns
    its place only when consumers traverse it as a distinct edge (e.g. relates
    to source *without* obsoleting it). Navigation/description, never identity
    (A6); deliberately small."""

    SUPERSEDES = "supersedes"
    PORT_OF = "port_of"
    MIRROR_OF = "mirror_of"
    REMASTER_OF = "remaster_of"   # remastered edition of an earlier release (no obsolescence)
    REISSUE_OF = "reissue_of"     # re-release of an earlier edition (no obsolescence)
    DERIVED_FROM = "derived_from"
