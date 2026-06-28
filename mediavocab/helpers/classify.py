"""Predicate helpers for routing decisions in consuming code (non-normative).

Convenience predicates over the spec's routing/sentinel rules — e.g.
``is_not_media`` (T8 sentinels never reach a Work), ``is_device_entity`` (A3 —
a device is an Entity, not a Work), ``is_continuous_release`` (A3 — delivery on
the Release). Each predicate cites the governing clause.
"""
from __future__ import annotations

from mediavocab.taxonomy import EntityKind, MediaType, StreamMode
from mediavocab.models.entity import Entity
from mediavocab.models.work import Release


def is_not_media(media_type: MediaType) -> bool:
    """True if `media_type` is the terminal NOT_MEDIA sentinel.

    Pipeline sentinels never appear on a canonical Work (T8); call this on
    `signals.medium` or `MediaType` directly, not on `work.media_type`.
    """
    return media_type == MediaType.NOT_MEDIA


def is_generic(media_type: MediaType) -> bool:
    """True if `media_type` is the transient GENERIC marker (type unknown)."""
    return media_type == MediaType.GENERIC


def is_control(media_type: MediaType) -> bool:
    """True if `media_type` is the playback-control sentinel."""
    return media_type == MediaType.CONTROL


def is_device_entity(entity: Entity) -> bool:
    """True if the entity is a physical playback endpoint (smart speaker,
    cast target, smart plug, console). Not a Work — a routing destination.
    """
    return entity.kind == EntityKind.DEVICE


def is_continuous_release(release: Release) -> bool:
    """True if the Release streams without a defined end (radio, IPTV)."""
    return release.stream_mode == StreamMode.CONTINUOUS
