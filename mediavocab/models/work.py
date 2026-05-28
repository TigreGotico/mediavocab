"""Work, Release, Appearance, Chapter, AccessibilityTrack, AvailabilityWindow,
WorkRelation, ReleaseRelation, Programme, Schedule.

Spec §5 (models).

`Work` is embedded directly inside `Appearance.work`, `Release.work`,
`WorkRelation.target`, etc. The spec describes `WorkRef` / `ReleaseRef` as
lightweight pointers — in practice, consumers pass a Work with only
identity fields populated, which is wire-format-equivalent.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mediavocab._iso_date import IsoDate, iso_compare
from mediavocab.models.entity import Credit, EntityRef
from mediavocab.models.license import License
from mediavocab.taxonomy import (
    AccessibilityKind,
    ContentForm,
    MediaType,
    PIPELINE_SENTINELS,
    ProgrammeFormat,
    ReleasePackaging,
    ReleaseStatus,
    StreamMode,
    VariantKind,
    WorkRelationKind,
    ReleaseRelationKind,
)

_CFG = ConfigDict(extra="ignore", populate_by_name=True)


# A MediaType-to-country-slot table. Used for editorial validation and as a
# hint to ingestion code; the Work validator enforces exclusivity only (§5.3).
COUNTRY_SLOT_FOR: Dict[MediaType, str] = {
    MediaType.MOVIE: "production_country",
    MediaType.SHORT_FILM: "production_country",
    MediaType.EPISODIC_SERIES: "production_country",
    MediaType.MUSIC_VIDEO: "production_country",
    MediaType.GAME: "production_country",
    MediaType.INTERACTIVE_FICTION: "production_country",

    MediaType.MUSIC: "publication_country",
    MediaType.BOOK: "publication_country",
    MediaType.COMIC: "publication_country",
    MediaType.AUDIOBOOK: "publication_country",

    MediaType.RADIO: "broadcaster_country",
    MediaType.TV: "broadcaster_country",
    MediaType.PODCAST: "broadcaster_country",
    MediaType.AUDIO_DRAMA: "broadcaster_country",
}


class LocalizedTitle(BaseModel):
    """Language-tagged title (§5.1)."""

    model_config = _CFG

    language: str
    title: str
    is_original: bool = False


class Appearance(BaseModel):
    """Position of a Work within a container Release / parent Work (§5.3).

    `offset` carries absolute time-into-the-parent where this member starts —
    used by continuous mixes (DJ sets, megamixes, live concerts). None = the
    parent uses ordering only.
    """

    model_config = _CFG

    work: "Work"
    position: int
    disc: int = 1
    offset: Optional[float] = None
    title_override: Optional[str] = None
    length_override: Optional[float] = None
    is_bonus: bool = False
    attributed_to: Optional[EntityRef] = None


class Chapter(BaseModel):
    """A timestamped marker within a Release (§5.4). Navigation aid, NOT a Work."""

    model_config = _CFG

    offset: float
    title: str = ""
    image: str = ""
    end: Optional[float] = None
    work_ref: Optional[EntityRef] = None   # rare; when chapter delineates a distinct Work segment


class AccessibilityTrack(BaseModel):
    """Per-Release accessibility asset (§5.4)."""

    model_config = _CFG

    kind: AccessibilityKind
    language: str = ""
    uri: str = ""
    forced: bool = False
    sdh: bool = False
    note: Optional[str] = None


class AvailabilityWindow(BaseModel):
    """A single (start, end) availability window. None = open-ended on that side (§5.4)."""

    model_config = _CFG

    start: Optional[str] = None
    end: Optional[str] = None
    note: str = ""

    @model_validator(mode="after")
    def _check(self) -> "AvailabilityWindow":
        if self.start is not None and self.end is not None:
            if iso_compare(self.end, self.start) < 0:
                raise ValueError("AvailabilityWindow.end precedes start")
        return self


class WorkRelation(BaseModel):
    """Work→Work relation (§4.13)."""

    model_config = _CFG

    kind: WorkRelationKind
    target: "Work"
    note: Optional[str] = None


class ReleaseRelation(BaseModel):
    """Release→Release lineage (§4.13). Use sparingly — most distinctions are
    encoded by format/packaging fields plus `release_hash`."""

    model_config = _CFG

    kind: ReleaseRelationKind
    target: "Release"
    note: Optional[str] = None


class Work(BaseModel):
    """The canonical creative artefact (§5.3).

    Does not contain playback URIs — those live on Release. Two records
    describing the same song on two different albums share a Work.
    """

    model_config = _CFG

    title: str
    media_type: MediaType
    content_form: ContentForm = ContentForm.PRIMARY

    # Temporal
    year: Optional[int] = None
    runtime: Optional[float] = None

    # Language
    language: str = ""
    original_languages: List[str] = Field(default_factory=list)

    # Geographic provenance (exactly one of the three is non-empty per MediaType;
    # validator enforces exclusivity only, not slot-match — §5.3)
    production_country: str = ""
    publication_country: str = ""
    broadcaster_country: str = ""

    # Episode / series structure
    season: Optional[int] = None
    episode: Optional[int] = None
    series_title: Optional[str] = None
    episode_orderings: Dict[str, int] = Field(default_factory=dict)

    # Edition (Work-only — restructurings produce new Works)
    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    source_format: str = ""

    # Routing (excluded from work_hash)
    content_genres: List[str] = Field(default_factory=list)
    programme_format: Optional[ProgrammeFormat] = None
    release_status: ReleaseStatus = ReleaseStatus.RELEASED

    # Discovery (not part of identity hash)
    aka: List[str] = Field(default_factory=list)
    localized_titles: List[LocalizedTitle] = Field(default_factory=list)

    # Credits and containment
    credits: List[Credit] = Field(default_factory=list)
    tracklist: List[Appearance] = Field(default_factory=list)
    relations: List[WorkRelation] = Field(default_factory=list)

    # Cross-references
    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, str] = Field(default_factory=dict)

    @field_validator("content_genres", mode="before")
    @classmethod
    def _normalise_genres(cls, v):
        """Lowercase and strip whitespace from each genre tag on intake."""
        if not v:
            return v
        return [g.strip().lower() if isinstance(g, str) else g for g in v]

    @model_validator(mode="after")
    def _check(self) -> "Work":
        if self.media_type in PIPELINE_SENTINELS:
            raise ValueError(
                f"Work.media_type must be a concrete kind; "
                f"{self.media_type.value!r} is a pipeline sentinel (T8)"
            )
        slots = [self.production_country, self.publication_country, self.broadcaster_country]
        if sum(1 for s in slots if s) > 1:
            raise ValueError(
                "Work: at most one of production_country / publication_country / "
                "broadcaster_country may be set"
            )
        return self

    def country(self) -> str:
        """Return the one non-empty country slot, or `""` (§6.3 country_slot)."""
        return (
            self.production_country
            or self.publication_country
            or self.broadcaster_country
            or ""
        )


class Release(BaseModel):
    """A specific physical or digital manifestation of a Work (§5.4)."""

    model_config = _CFG

    work: Work

    # Packaging (description-family)
    packaging: Optional[ReleasePackaging] = None
    edition: str = ""
    region: str = ""

    # Format identity (T6)
    container: str = ""
    codec: str = ""
    bitrate: str = ""
    platform: str = ""
    resolution: str = ""

    # Audio / video quality (description, not identity)
    hdr: str = ""
    audio_channels: str = ""
    sample_rate: Optional[int] = None
    frame_rate: Optional[float] = None
    aspect_ratio: str = ""
    color: Optional[bool] = None
    audio_present: Optional[bool] = None

    # Delivery
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    # Localisation
    audio_language: str = ""                          # identity (defines the dub/version)
    subtitle_languages: List[str] = Field(default_factory=list)   # description

    # Lifecycle
    release_status: ReleaseStatus = ReleaseStatus.RELEASED
    release_date: Optional[IsoDate] = None

    # Rights and availability
    license: Optional[License] = None
    region_locked: Optional[bool] = None
    regions_available: List[str] = Field(default_factory=list)
    available_from: Optional[IsoDate] = None
    available_until: Optional[IsoDate] = None
    availability_windows: List[AvailabilityWindow] = Field(default_factory=list)

    # Playback
    uri: str = ""
    image: str = ""

    # Navigation / accessibility
    chapters: List[Chapter] = Field(default_factory=list)
    accessibility: List[AccessibilityTrack] = Field(default_factory=list)

    # Composite Releases (box sets, anthology Blu-rays, multi-cut discs)
    contents: List[Appearance] = Field(default_factory=list)

    # Infrastructure
    label: Optional[EntityRef] = None
    distributor: Optional[EntityRef] = None

    # Release→Release lineage
    relations: List[ReleaseRelation] = Field(default_factory=list)

    # Resolver-side scoring
    match_confidence: float = 0.0

    # Cross-references
    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, str] = Field(default_factory=dict)

    @field_validator("license", mode="before")
    @classmethod
    def _coerce_license(cls, v):
        """Accept plain SPDX strings; coerce to License on intake."""
        if v is None or isinstance(v, License):
            return v
        if isinstance(v, str):
            return License.from_spdx(v) if v.strip() else None
        return v

    @model_validator(mode="after")
    def _check(self) -> "Release":
        # Availability windows — ordered, non-overlapping, at most one open-ended (must be last)
        wins = sorted(
            self.availability_windows,
            key=lambda w: (w.start is not None, w.start or ""),
        )
        for prev, cur in zip(wins, wins[1:]):
            if prev.end is None or cur.start is None:
                raise ValueError("open-ended availability_window must be the last entry")
            if cur.start < prev.end:
                raise ValueError("availability_windows overlap")

        # region_locked ↔ regions_available invariant
        if self.region_locked is False and self.regions_available:
            raise ValueError("region_locked=False requires regions_available to be empty")

        # Positive numeric quality fields
        if self.sample_rate is not None and self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive (Hz)")
        if self.frame_rate is not None and self.frame_rate <= 0:
            raise ValueError("frame_rate must be positive (fps)")
        if self.match_confidence < 0.0 or self.match_confidence > 1.0:
            raise ValueError("match_confidence must be in [0.0, 1.0]")
        return self





# Resolve forward references in the cycles Work <-> Appearance and
# Release <-> ReleaseRelation, Work <-> WorkRelation.
Appearance.model_rebuild()
Work.model_rebuild()
WorkRelation.model_rebuild()
Release.model_rebuild()
ReleaseRelation.model_rebuild()
