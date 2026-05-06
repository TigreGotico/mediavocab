"""Work, Release, Appearance, WorkRelation. Spec §5.4, §5.5, §5.6, §6."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from mediavocab.taxonomy import (
    MediaType,
    VariantKind,
    ReleaseStatus,
    StreamMode,
    WorkRelationKind,
)
from mediavocab.models.entity import Credit, EntityRef


_CFG = ConfigDict(extra="ignore", populate_by_name=True)


class Appearance(BaseModel):
    """Position of a Work within a Release container."""

    model_config = _CFG

    work: "Work"
    position: int
    disc: int = 1
    title_override: Optional[str] = None
    length_override: Optional[float] = None
    is_bonus: bool = False
    attributed_to: Optional[EntityRef] = None


class Work(BaseModel):
    """The abstract canonical creative work.

    Does not contain playback URIs — those live in Release. Two records
    describing the same song on two different albums share a Work.
    """

    model_config = _CFG

    title: str
    media_type: MediaType = MediaType.GENERIC

    year: Optional[int] = None
    runtime: Optional[float] = None
    language: str = ""
    country: str = ""

    season: Optional[int] = None
    episode: Optional[int] = None
    series_title: Optional[str] = None

    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    source_format: str = ""

    color: Optional[bool] = None
    audio_present: Optional[bool] = None

    content_genres: List[str] = Field(default_factory=list)
    release_status: ReleaseStatus = ReleaseStatus.RELEASED

    aka: List[str] = Field(default_factory=list)

    credits: List[Credit] = Field(default_factory=list)
    tracklist: List[Appearance] = Field(default_factory=list)

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)


class Release(BaseModel):
    """A specific physical or digital manifestation of a Work."""

    model_config = _CFG

    work: Work

    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    region: str = ""
    source_format: str = ""
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    release_status: ReleaseStatus = ReleaseStatus.RELEASED
    release_date: Optional[str] = None

    uri: str = ""
    image: str = ""

    match_confidence: float = 0.0

    label: Optional[EntityRef] = None
    distributor: Optional[EntityRef] = None

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)


class WorkRelation(BaseModel):
    """A relation from one Work to another. Spec §6."""

    model_config = _CFG

    kind: WorkRelationKind
    target: Work
    note: Optional[str] = None


# Resolve forward references in the cycle Work <-> Appearance.
Appearance.model_rebuild()
Work.model_rebuild()
