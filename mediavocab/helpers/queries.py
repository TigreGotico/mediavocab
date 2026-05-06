"""Convenience query helpers for common credit lookups.

Non-normative — every consumer can implement these in two lines, but they
are the most-rewritten loop in the package's surface area.
"""
from __future__ import annotations

from typing import List, Optional

from mediavocab.taxonomy import RelationRole
from mediavocab.models.entity import Credit
from mediavocab.models.work import Work


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


__all__ = [
    "credits_with_role",
    "primary_credit",
    "director",
    "author",
    "performers",
]
