"""Taxonomy enums and genre constants. Zero dependencies — safe everywhere."""
from mediavocab.taxonomy.media_type import MediaType
from mediavocab.taxonomy.variant import VariantKind
from mediavocab.taxonomy.status import ReleaseStatus, StreamMode
from mediavocab.taxonomy.entity import EntityKind
from mediavocab.taxonomy.relation import (
    RelationRole,
    CreditSection,
    WorkRelationKind,
)
from mediavocab.taxonomy.membership import MembershipStatus
from mediavocab.taxonomy.genre import (  # noqa: F401  (re-exported)
    GENRE_DOCUMENTARY, GENRE_ANIMATION, GENRE_ANIME, GENRE_SHORT_FILM,
    GENRE_NOIR, GENRE_CONCERT, GENRE_STAND_UP, GENRE_TALK_SHOW, GENRE_REALITY,
    GENRE_NEWS, GENRE_SPORTS, GENRE_BEHIND_SCENES, GENRE_TRAILER,
    GENRE_RADIO_DRAMA, GENRE_ASMR, GENRE_AMBIENT, GENRE_SOUNDSCAPE,
    GENRE_NATURE_SOUNDS, GENRE_WHITE_NOISE,
    GENRE_SFX_ANIMAL, GENRE_SFX_NATURE, GENRE_SFX_MECHANICAL,
    GENRE_SFX_HUMAN, GENRE_SFX_UI, GENRE_SFX_FOLEY,
    GENRE_MANGA, GENRE_MANHWA, GENRE_MANHUA, GENRE_WEBCOMIC,
    GENRE_MOTION_COMIC,
    GENRE_POETRY, GENRE_SPOKEN_WORD, GENRE_ESSAY, GENRE_SHORT_STORY,
    GENRE_HIP_HOP, GENRE_EDUCATIONAL,
    GENRE_ADULT, GENRE_AI_GENERATED,
)

__all__ = [
    "MediaType", "VariantKind", "ReleaseStatus", "StreamMode", "EntityKind",
    "RelationRole", "CreditSection", "WorkRelationKind", "MembershipStatus",
    # genres
    "GENRE_DOCUMENTARY", "GENRE_ANIMATION", "GENRE_ANIME", "GENRE_SHORT_FILM",
    "GENRE_NOIR", "GENRE_CONCERT", "GENRE_STAND_UP", "GENRE_TALK_SHOW",
    "GENRE_REALITY", "GENRE_NEWS", "GENRE_SPORTS", "GENRE_BEHIND_SCENES",
    "GENRE_TRAILER", "GENRE_RADIO_DRAMA", "GENRE_ASMR", "GENRE_AMBIENT",
    "GENRE_SOUNDSCAPE", "GENRE_NATURE_SOUNDS", "GENRE_WHITE_NOISE",
    "GENRE_SFX_ANIMAL", "GENRE_SFX_NATURE", "GENRE_SFX_MECHANICAL",
    "GENRE_SFX_HUMAN", "GENRE_SFX_UI", "GENRE_SFX_FOLEY",
    "GENRE_MANGA", "GENRE_MANHWA", "GENRE_MANHUA", "GENRE_WEBCOMIC",
    "GENRE_MOTION_COMIC", "GENRE_POETRY", "GENRE_SPOKEN_WORD", "GENRE_ESSAY",
    "GENRE_SHORT_STORY", "GENRE_HIP_HOP", "GENRE_EDUCATIONAL",
    "GENRE_ADULT", "GENRE_AI_GENERATED",
]
