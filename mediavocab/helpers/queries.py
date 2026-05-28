"""Convenience query helpers for common credit lookups.

Non-normative — every consumer can implement these in two lines, but they
are the most-rewritten loop in the package's surface area.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

from mediavocab.taxonomy import RelationRole, WorkRelationKind, ReleaseRelationKind
from mediavocab.models.entity import Credit, EntityRef
from mediavocab.models.work import Release, Work, WorkRelation, ReleaseRelation


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
# WorkRelation / ReleaseRelation traversal helpers
# ---------------------------------------------------------------------------

def relations_of_kind(work: Work, kind: WorkRelationKind) -> List[WorkRelation]:
    """All WorkRelations on the Work with the given kind."""
    return [r for r in (work.relations or []) if r.kind == kind]


def is_sequel_of(work: Work) -> bool:
    """True if the Work has at least one SEQUEL_TO relation."""
    return any(r.kind == WorkRelationKind.SEQUEL_TO for r in (work.relations or []))


def is_part_of_series(work: Work) -> bool:
    """True if the Work has at least one PART_OF relation."""
    return any(r.kind == WorkRelationKind.PART_OF for r in (work.relations or []))


def all_cuts(work: Work) -> List[WorkRelation]:
    """All DERIVED_FROM relations on the Work (used for alternative cuts)."""
    return relations_of_kind(work, WorkRelationKind.DERIVED_FROM)


def release_variants(release: Release) -> List[ReleaseRelation]:
    """All SUPERSEDES ReleaseRelations on the Release."""
    return [r for r in (release.relations or []) if r.kind == ReleaseRelationKind.SUPERSEDES]


__all__ = [
    "credits_with_role",
    "primary_credit",
    "director",
    "author",
    "performers",
    "episodes_of",
    "filmography_of",
    "relations_of_kind",
    "is_sequel_of",
    "is_part_of_series",
    "all_cuts",
    "release_variants",
]
