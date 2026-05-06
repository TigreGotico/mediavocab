"""Convenience query helpers for common credit lookups.

Non-normative — every consumer can implement these in two lines, but they
are the most-rewritten loop in the package's surface area.
"""
from __future__ import annotations

from typing import List, Optional

from mediavocab.taxonomy import RelationRole
from mediavocab.models.entity import Credit
from mediavocab.models.work import Release, Work


def credits_with_role(
    work_or_release,
    relation_role: RelationRole,
) -> List[Credit]:
    """All credits on the Work or Release with the given RelationRole,
    sorted by `position` (None goes last, then list order).
    """
    creds = list(getattr(work_or_release, "credits", []) or [])
    matching = [c for c in creds if c.relation_role == relation_role]
    matching.sort(key=lambda c: (c.position is None, c.position or 0))
    return matching


def primary_credit(
    work_or_release,
    relation_role: Optional[RelationRole] = None,
) -> Optional[Credit]:
    """Return the most-significant credit on the Work or Release.

    If `relation_role` is given, return the first credit with that role
    (lowest `position`, falling back to first in list).

    If `relation_role` is None, return the first PRINCIPAL-section credit
    overall, breaking ties by `position`.
    """
    creds = list(getattr(work_or_release, "credits", []) or [])
    if relation_role is not None:
        matching = credits_with_role(work_or_release, relation_role)
        return matching[0] if matching else None

    principal = [c for c in creds if c.section.value == "principal"]
    pool = principal or creds
    if not pool:
        return None
    pool_sorted = sorted(pool, key=lambda c: (c.position is None, c.position or 0))
    return pool_sorted[0]


def director(work: Work) -> Optional[Credit]:
    """Convenience: the first DIRECTOR credit on the Work."""
    return primary_credit(work, RelationRole.DIRECTOR)


def author(work: Work) -> Optional[Credit]:
    """Convenience: the first AUTHOR credit on the Work."""
    return primary_credit(work, RelationRole.AUTHOR)


def performers(work_or_release) -> List[Credit]:
    """All PERFORMER credits, ordered by `position`."""
    return credits_with_role(work_or_release, RelationRole.PERFORMER)


def merged_credits(release: Release) -> List[Credit]:
    """Work credits + Release-level credits, in that order. Release credits
    supplement Work credits (axiom: Release credits apply only to this
    specific manifestation, not to the canonical Work).
    """
    return list(release.work.credits or []) + list(release.credits or [])


__all__ = [
    "credits_with_role",
    "primary_credit",
    "director",
    "author",
    "performers",
    "merged_credits",
]
