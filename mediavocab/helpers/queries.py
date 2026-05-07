"""Convenience query helpers for common credit lookups.

Non-normative — every consumer can implement these in two lines, but they
are the most-rewritten loop in the package's surface area.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

from mediavocab.taxonomy import RelationRole
from mediavocab.models.entity import Credit, EntityRef
from mediavocab.models.work import Release, Work


def credits_with_role(work: Work, relation_role: RelationRole) -> List[Credit]:
    """All credits on the Work with the given RelationRole, in list order
    (which is the editorial credit order).
    """
    return [c for c in (work.credits or []) if c.relation_role == relation_role]


def primary_credit(
    work: Work,
    relation_role: Optional[RelationRole] = None,
) -> Optional[Credit]:
    """The first matching credit on the Work.

    If `relation_role` is given, return the first credit with that role.
    Otherwise return the first PRINCIPAL-section credit, falling back to
    the first credit overall.
    """
    creds = list(work.credits or [])
    if relation_role is not None:
        for c in creds:
            if c.relation_role == relation_role:
                return c
        return None

    for c in creds:
        if c.section.value == "principal":
            return c
    return creds[0] if creds else None


def director(work: Work) -> Optional[Credit]:
    """Convenience: the first DIRECTOR credit on the Work."""
    return primary_credit(work, RelationRole.DIRECTOR)


def author(work: Work) -> Optional[Credit]:
    """Convenience: the first AUTHOR credit on the Work."""
    return primary_credit(work, RelationRole.AUTHOR)


def performers(work: Work) -> List[Credit]:
    """All PERFORMER credits in editorial order."""
    return credits_with_role(work, RelationRole.PERFORMER)


def episodes_of(series: Work, all_works: Iterable[Work]) -> List[Work]:
    """Return episodes belonging to a series, in `(season, episode)` order.

    A "series" Work is one with ``series_title`` set (or the series's
    own title) and ``episode == None``. Episode Works carry the same
    ``series_title`` plus an ``episode`` value.

    The match is by ``series_title`` (canonical name) — consumers
    that promote ``Entity(kind=SERIES)`` should pre-resolve to the
    canonical name before calling.
    """
    name = series.series_title or series.title
    eps = [
        w for w in all_works
        if w.episode is not None and (w.series_title or "") == name
    ]
    eps.sort(key=lambda w: (w.season or 0, w.episode or 0))
    return eps


def filmography_of(entity: EntityRef, all_works: Iterable[Work],
                   relation_role: Optional[RelationRole] = None
                   ) -> List[Work]:
    """Return Works on which the given Entity is credited.

    Match by ``EntityRef.external_ids`` overlap (any shared, non-empty
    key/value pair anchors the match) or, as a last resort, by name
    equality. Optionally restrict to a specific role.
    """
    target_ids = {k: v for k, v in (entity.external_ids or {}).items() if v}
    out: List[Work] = []
    for w in all_works:
        for c in (w.credits or []):
            if relation_role is not None and c.relation_role != relation_role:
                continue
            cand_ids = c.entity.external_ids or {}
            if any(target_ids.get(k) == v and v for k, v in cand_ids.items()):
                out.append(w)
                break
            if cand_ids and target_ids:
                continue  # had IDs that didn't overlap → not a match
            if c.entity.name and c.entity.name == entity.name:
                out.append(w)
                break
    return out


# ---------------------------------------------------------------------------
# Release ranking — "play me the best version available" preference rules.
# ---------------------------------------------------------------------------

# Ordered worst→best for ranking; missing values rank at -1.
_RESOLUTION_ORDER = ("", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p")
_HDR_ORDER = ("", "HDR10", "HDR10+", "HLG", "Dolby Vision")
_AUDIO_CHANNELS_ORDER = ("", "mono", "stereo", "5.1", "7.1", "Atmos")
_VARIANT_PREF = {
    # Higher = preferred. Director's / Extended cuts preferred over theatrical
    # when a consumer asks for "the best version available". Theatrical is the
    # baseline; remasters / colorizations are improvements; bootlegs lose.
    "directors":     8,
    "extended":      7,
    "preservation":  6,
    "remastered":    5,
    "upscaled":      4,
    "deluxe":        4,
    "colorized":     3,
    "theatrical":    2,
    "reissue":       2,
    "regional":      1,
    "bootleg":      -1,
}


def _index(value: str, order: tuple) -> int:
    """Return the index of ``value`` in ``order``, or -1 if not listed."""
    try:
        return order.index(value or "")
    except ValueError:
        return -1


def quality_score(release: Release) -> tuple:
    """Sortable tuple — higher tuples are better releases.

    Order of precedence (highest first): variant preference,
    resolution, HDR, audio channels, sample rate.
    """
    return (
        _VARIANT_PREF.get(release.variant_kind.value if release.variant_kind else "", 0),
        _index(release.resolution, _RESOLUTION_ORDER),
        _index(release.hdr,         _HDR_ORDER),
        _index(release.audio_channels, _AUDIO_CHANNELS_ORDER),
        release.sample_rate or 0,
    )


def best_release(*releases: Release) -> Optional[Release]:
    """Return the highest-quality Release of those given, or ``None``
    when called with no arguments.

    Releases tied on every comparison axis return the first one
    given — list order breaks ties so callers can pre-order by
    preference (e.g. "prefer my local file over a stream").
    """
    if not releases:
        return None
    return max(releases, key=quality_score)


__all__ = [
    "credits_with_role",
    "primary_credit",
    "director",
    "author",
    "performers",
    "episodes_of",
    "filmography_of",
    "quality_score",
    "best_release",
]
