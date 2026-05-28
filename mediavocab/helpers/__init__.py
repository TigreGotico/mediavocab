"""Convenience helpers — non-normative."""
from mediavocab.helpers.classify import (
    is_not_media, is_generic, is_control, is_device_entity, is_continuous_release,
)
from mediavocab.helpers.queries import (
    credits_with_role, primary_credit, director, author, performers,
    episodes_of, filmography_of,
    relations_of_kind, is_sequel_of, is_part_of_series, all_cuts,
    release_variants,
)

__all__ = [
    "is_not_media", "is_generic", "is_control",
    "is_device_entity", "is_continuous_release",
    "credits_with_role", "primary_credit", "director", "author", "performers",
    "episodes_of", "filmography_of",
    "relations_of_kind", "is_sequel_of", "is_part_of_series", "all_cuts",
    "release_variants",
]
