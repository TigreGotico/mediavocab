"""VariantKind — Work-level restructuring of the canonical artefact. Spec §4.3.

Each cut is its own Work (§3.4); Release-side packaging (deluxe, reissue,
regional, bootleg, box-set) lives on `ReleasePackaging` (§4.4).
"""
from enum import Enum


class VariantKind(str, Enum):
    """Work-level restructuring (§3.4). None = canonical/default (A2)."""

    # Cuts — official or fan, treated uniformly
    THEATRICAL = "theatrical"
    DIRECTORS = "directors"
    EXTENDED = "extended"
    FANEDIT = "fanedit"

    # Cross-MediaType structural transformations
    TV_TO_MOVIE = "tv_to_movie"
    MOVIE_TO_TV = "movie_to_tv"

    # Restoration / technical enhancement
    PRESERVATION = "preservation"
    COLORIZED = "colorized"
    REMASTERED = "remastered"
    UPSCALED = "upscaled"

    # Derived aggregations
    COMPILATION = "compilation"

    OTHER = "other"


class ReleasePackaging(str, Enum):
    """Packaging of a Release independent of which Works it carries (§3.5)."""

    DELUXE = "deluxe"
    REISSUE = "reissue"
    REGIONAL = "regional"
    BOOTLEG = "bootleg"
    BOX_SET = "box_set"
    PROMO = "promo"
    OTHER = "other"
