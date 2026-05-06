"""VariantKind — why a Release differs from the canonical Work. Spec §4.2."""
from enum import Enum


class VariantKind(str, Enum):
    """Records why an edition differs from the canonical work.

    A missing variant_kind (None) means the canonical/default edition.
    """

    THEATRICAL = "theatrical"
    DIRECTORS = "directors"
    EXTENDED = "extended"

    FANEDIT = "fanedit"
    TV_TO_MOVIE = "tv_to_movie"
    MOVIE_TO_TV = "movie_to_tv"

    PRESERVATION = "preservation"
    COLORIZED = "colorized"
    REMASTERED = "remastered"
    UPSCALED = "upscaled"

    DELUXE = "deluxe"
    REISSUE = "reissue"
    COMPILATION = "compilation"
    REGIONAL = "regional"
    BOOTLEG = "bootleg"

    OTHER = "other"
