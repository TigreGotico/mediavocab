"""Convenience constructors for common patterns. Non-normative."""
from __future__ import annotations

from typing import List, Optional

from mediavocab.taxonomy import (
    MediaType,
    EntityKind,
    RelationRole,
    CreditSection,
    VariantKind,
    StreamMode,
)
from mediavocab.models.entity import Credit, EntityRef
from mediavocab.models.work import Release, Work


def make_movie(
    title: str,
    *,
    year: Optional[int] = None,
    runtime: Optional[float] = None,
    director: Optional[str] = None,
    content_genres: Optional[List[str]] = None,
) -> Work:
    """Construct a MOVIE Work, optionally with a director credit."""
    credits: List[Credit] = []
    if director:
        credits.append(make_credit(director, EntityKind.PERSON, RelationRole.DIRECTOR))
    return Work(
        title=title,
        media_type=MediaType.MOVIE,
        year=year,
        runtime=runtime,
        content_genres=content_genres or [],
        credits=credits,
    )


def make_episode(
    series_title: str,
    season: int,
    episode: int,
    *,
    title: Optional[str] = None,
    year: Optional[int] = None,
    runtime: Optional[float] = None,
) -> Work:
    """Construct a TV episode Work."""
    return Work(
        title=title or f"{series_title} S{season:02d}E{episode:02d}",
        media_type=MediaType.TV,
        series_title=series_title,
        season=season,
        episode=episode,
        year=year,
        runtime=runtime,
    )


def make_release(
    work: Work,
    uri: str,
    *,
    variant_kind: Optional[VariantKind] = None,
    stream_mode: StreamMode = StreamMode.ON_DEMAND,
    region: str = "",
    source_format: str = "",
) -> Release:
    """Wrap a Work in a Release with the given URI."""
    return Release(
        work=work,
        uri=uri,
        variant_kind=variant_kind,
        stream_mode=stream_mode,
        region=region,
        source_format=source_format,
    )


def make_credit(
    name: str,
    kind: EntityKind,
    relation_role: RelationRole,
    *,
    role: Optional[str] = None,
    section: CreditSection = CreditSection.PRINCIPAL,
) -> Credit:
    """Construct a Credit pointing to a fresh EntityRef."""
    return Credit(
        entity=EntityRef(name=name, kind=kind),
        role=role or relation_role.value,
        relation_role=relation_role,
        section=section,
    )
