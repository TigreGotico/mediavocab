"""Work, Release, Appearance, Chapter, AccessibilityTrack, WorkRelation.

Spec §5.4, §5.5, §5.6, §6.
"""
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from mediavocab.taxonomy import (
    MediaType,
    VariantKind,
    ReleaseStatus,
    StreamMode,
    WorkRelationKind,
)
from mediavocab.taxonomy.relation import ReleaseRelationKind
from mediavocab.models.entity import Credit, EntityRef
from mediavocab._iso_date import IsoDate


_CFG = ConfigDict(extra="ignore", populate_by_name=True)


class Appearance(BaseModel):
    """Position of a Work within a Release container.

    `offset` carries the absolute time-into-the-Release where this member
    starts. Used by continuous mixes (DJ sets, megamixes, live concerts)
    where `position` alone is insufficient. None = the parent uses simple
    ordering and members do not occupy a fixed offset.
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
    """A timestamped marker within a Release: audiobook chapter, podcast
    chapter marker, DVD scene break, "skip the intro" point.

    Chapters are NOT separate Works in their own right. ``work_ref``
    is an optional pointer for the case where one Release contains
    *segments* of distinct Works (a podcast episode whose chapters
    delineate an interview Work + a monologue Work). When set, the
    chapter is read as "this region of the Release contains *that*
    Work." When ``None`` the chapter is purely a navigation aid for
    the parent Release.
    """

    model_config = _CFG

    offset: float
    title: str = ""
    image: str = ""
    end: Optional[float] = None
    work_ref: Optional[EntityRef] = None   # see docstring; usually None


class AccessibilityTrack(BaseModel):
    """A per-Release accessibility asset: subtitle/caption file, audio
    description, sign-language insert, lyric, transcript.

    Distinct from `VariantKind` — the underlying Work is unchanged; the
    Release simply ships an additional asset.
    """

    model_config = _CFG

    kind: str
    language: str = ""
    uri: str = ""
    forced: bool = False
    sdh: bool = False
    note: Optional[str] = None


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
    original_languages: List[str] = Field(default_factory=list)  # multi-language original (Quebec films, simulcast anime)
    country: str = ""

    season: Optional[int] = None
    episode: Optional[int] = None
    series_title: Optional[str] = None
    episode_orderings: Dict[str, int] = Field(default_factory=dict)

    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    source_format: str = ""

    color: Optional[bool] = None
    audio_present: Optional[bool] = None

    content_genres: List[str] = Field(default_factory=list)
    release_status: ReleaseStatus = ReleaseStatus.RELEASED

    aka: List[str] = Field(default_factory=list)
    localized_titles: List[Tuple[str, str]] = Field(default_factory=list)

    credits: List[Credit] = Field(default_factory=list)
    tracklist: List[Appearance] = Field(default_factory=list)

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)


class Release(BaseModel):
    """A specific physical or digital manifestation of a Work."""

    model_config = _CFG

    work: Work

    # Edition
    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    region: str = ""

    # Format — three orthogonal axes (replaces overloaded source_format)
    container: str = ""
    codec: str = ""
    bitrate: str = ""
    platform: str = ""
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    # Quality / fidelity
    resolution: str = ""
    hdr: str = ""
    audio_channels: str = ""
    sample_rate: Optional[int] = None

    # Localisation — dub/sub/market triple; not VariantKind.REGIONAL
    audio_language: str = ""
    subtitle_languages: List[str] = Field(default_factory=list)

    # Lifecycle
    release_status: ReleaseStatus = ReleaseStatus.RELEASED
    release_date: Optional[IsoDate] = None

    # Rights and availability — license carries the SPDX-style string for
    # persistence; use ``parsed_license`` for the typed view.
    license: str = ""
    region_locked: Optional[bool] = None
    regions_available: List[str] = Field(default_factory=list)
    available_from: Optional[IsoDate] = None
    available_until: Optional[IsoDate] = None
    # Cycled availability ("Disney vault" pattern) — list of (from, until)
    # ISO-date pairs. Either side may be None for open-ended windows.
    # ``available_from`` / ``available_until`` cover the simple single-window
    # case; populate ``availability_windows`` only when there are multiple.
    availability_windows: List[Tuple[Optional[IsoDate], Optional[IsoDate]]] = Field(default_factory=list)

    # Playback
    uri: str = ""
    image: str = ""

    # Mid-Release navigation and accessibility
    chapters: List[Chapter] = Field(default_factory=list)
    accessibility: List[AccessibilityTrack] = Field(default_factory=list)

    # Composite Releases (box sets, anthology Blu-rays). A box set aggregates
    # several Works in one Release without a synthetic container Work. `work`
    # is the principal / headline Work; `contents` lists the member Works.
    contents: List[Appearance] = Field(default_factory=list)

    # Scoring
    match_confidence: float = 0.0

    # Infrastructure
    label: Optional[EntityRef] = None
    distributor: Optional[EntityRef] = None

    external_ids: Dict[str, str] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)

    @property
    def parsed_license(self) -> "License":
        """Typed view of :attr:`license`.

        ``license`` is the canonical persisted form (SPDX identifier or
        free string); ``parsed_license`` is the typed overlay parsed
        via :meth:`License.from_spdx`. Use it to filter on rights
        (open / commercial / share-alike) without string-matching every
        SPDX variant.

        Round-trips: ``Release.parsed_license.identifier == Release.license``
        for any string the parser recognises; unknown strings round-trip
        too but :meth:`License.is_open` returns ``False``.
        """
        # Local import: avoid circular dep on License (which imports nothing
        # from this module) at module-load time, and avoid forcing every
        # Release consumer to import License.
        from mediavocab.models.license import License
        return License.from_spdx(self.license)


class WorkRelation(BaseModel):
    """A relation from one Work to another. Spec §6."""

    model_config = _CFG

    kind: WorkRelationKind
    target: Work
    note: Optional[str] = None


class ReleaseRelation(BaseModel):
    """A relation from one Release to another. Spec §6.

    Use for per-edition lineage that ``WorkRelation`` cannot express:
    a 2025 Atmos remaster ``SUPERSEDES`` the 2017 stereo remaster
    (same Work; the Release graph chains).
    """

    model_config = _CFG

    kind: ReleaseRelationKind
    target: "Release"
    note: Optional[str] = None


class Programme(BaseModel):
    """A single airing of a Work on a broadcast channel.

    A ``Programme`` is the show-as-aired-at-time anchor for live
    broadcast (``MediaType.TV``, ``MediaType.RADIO``). It points at
    the *content* Work being aired (typically an
    ``EPISODIC_SERIES`` episode, a ``MOVIE``, an ``AUDIO_DRAMA``
    instalment, …) and locates it in time on a specific channel.

    Distinct from the channel-as-Work itself: a ``Programme`` is a
    *slot*, not an identity. Two channels broadcasting the same
    episode at different times yield two ``Programme`` records, one
    Work.
    """

    model_config = _CFG

    work: EntityRef                          # the content Work being aired (resolve via external_ids / title+year)
    channel: EntityRef                       # the broadcast channel Work / Entity
    starts_at: IsoDate                       # aired-at start
    ends_at: Optional[IsoDate] = None        # aired-at end (omit when only duration is known)
    runtime: Optional[float] = None          # seconds; programme length on the schedule
    is_live: bool = False                    # True for live broadcasts (sport, news, talk)
    is_repeat: bool = False                  # True when this airing is a re-broadcast
    extra: Dict[str, str] = Field(default_factory=dict)
    """Provider-specific tags that don't yet warrant a typed field.
    String values only — see §10.2 escape-hatch contract."""


class Schedule(BaseModel):
    """An ordered list of ``Programme`` slots for a single broadcast
    channel over a window of time.

    Use for EPG / TV-listings / radio-schedule data. mediavocab
    deliberately does not model "what's on right now" — query the
    schedule for the slot whose ``[starts_at, ends_at)`` contains the
    consumer's clock. Schedules are append-only at the model level;
    consumers can replace a stale ``Schedule`` wholesale to refresh.
    """

    model_config = _CFG

    channel: EntityRef                       # the broadcast channel
    programmes: List[Programme] = Field(default_factory=list)
    valid_from: Optional[IsoDate] = None     # start of the schedule window
    valid_until: Optional[IsoDate] = None    # end of the schedule window
    source: str = ""                         # provider hint: "tunein", "tvmaze", "epg.xml", …
    fetched_at: Optional[IsoDate] = None     # when the schedule was retrieved (for staleness)
    extra: Dict[str, str] = Field(default_factory=dict)
    """Provider-specific tags that don't yet warrant a typed field.
    String values only — see §10.2 escape-hatch contract."""


# Resolve forward references in the cycle Work <-> Appearance and
# ReleaseRelation -> Release.
Appearance.model_rebuild()
Work.model_rebuild()
ReleaseRelation.model_rebuild()
