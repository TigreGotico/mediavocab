"""VariantKind — the restructuring axis, Work-only (spec: §3.4/§4.3).

Identity axis: ``variant_kind`` is a ``work_hash`` input (§6.3). Each cut is its
own Work (§3.4) linked to siblings via ``WorkRelation``; Release-side packaging
(deluxe, reissue, regional, bootleg, box-set) lives on ``ReleasePackaging``
(§4.4), which is description-family.
"""
from enum import Enum


class VariantKind(str, Enum):
    """Work-level restructuring axis (spec: §3.4/§4.3). None = canonical/default (A2)."""

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
    """Packaging axis of a Release, independent of which Works it carries
    (spec: §3.5/§4.4). Description-family (§1.5): excluded from ``release_hash``
    (A6) — re-labelling an SKU across catalogues does not make a new Release.
    None is the unmarked default (A2)."""

    DELUXE = "deluxe"
    REISSUE = "reissue"
    REGIONAL = "regional"
    BOOTLEG = "bootleg"
    BOX_SET = "box_set"
    PROMO = "promo"
    OTHER = "other"
