"""Predicate helpers for routing decisions in consuming code."""
from __future__ import annotations

from mediavocab.taxonomy import MediaType, EntityKind, StreamMode
from mediavocab.models.entity import Entity
from mediavocab.models.work import Release, Work


def is_not_media(work: Work) -> bool:
    """True if the Work is the terminal NOT_MEDIA sentinel — not a playback
    candidate. Routers should send these to non-media handlers.
    """
    return work.media_type == MediaType.NOT_MEDIA


def is_generic(work: Work) -> bool:
    """True if media_type is the transient GENERIC marker — type unknown,
    further resolution may clarify.
    """
    return work.media_type == MediaType.GENERIC


def is_device_entity(entity: Entity) -> bool:
    """True if the entity is a physical playback endpoint (smart speaker,
    cast target, smart plug, console). Not a Work — a routing destination.
    """
    return entity.kind == EntityKind.DEVICE


def is_continuous_release(release: Release) -> bool:
    """True if the Release streams without a defined end (radio, IPTV)."""
    return release.stream_mode == StreamMode.CONTINUOUS
