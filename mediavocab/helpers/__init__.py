"""Convenience helpers — non-normative."""
from mediavocab.helpers.builders import (
    make_movie, make_episode, make_release, make_credit,
)
from mediavocab.helpers.classify import (
    is_not_media, is_generic, is_device_entity, is_continuous_release,
)

__all__ = [
    "make_movie", "make_episode", "make_release", "make_credit",
    "is_not_media", "is_generic", "is_device_entity", "is_continuous_release",
]
