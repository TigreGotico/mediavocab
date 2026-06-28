"""Work, Release, Appearance, Chapter, AccessibilityTrack, AvailabilityWindow,
WorkRelation, ReleaseRelation (spec: §5, models).

The object graph closes at six models (§1.4 — Work/Release/Entity +
Appearance/Credit/Membership); a scheduled broadcast (§5.5) and a playable
device (§5.6) are *applications* of these, not additional models (A9 forbids
new structure an existing combination already expresses).

`Work` is embedded directly inside `Appearance.work`, `Release.work`,
`WorkRelation.target`, etc. Per §5.1, Work/Release have no dedicated Ref type:
a pointer is a Work / Release populated with identity fields only — what
consumers pass here, wire-format-equivalent.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from mediavocab.models.signals import Signals
    from mediavocab.models.external_ids import ExternalIds

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from mediavocab._iso_date import IsoDate, iso_compare
from mediavocab.models.entity import Credit, EntityRef
from mediavocab.models.license import License
from mediavocab.taxonomy import (
    AccessibilityKind,
    ContentForm,
    MediaType,
    PictureFormat,
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
_LOG = logging.getLogger(__name__)


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
    """Language-tagged title (spec: §5.1). Discovery/description-family (§1.5);
    not a ``work_hash`` input (A6)."""

    model_config = _CFG

    language: str
    title: str
    is_original: bool = False


class Appearance(BaseModel):
    """Position of a Work within a container Release / parent Work — the §1.4
    edge (spec: §1.4, §5.3).

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
    """A timestamped marker within a Release (spec: §5.4). Navigation aid, NOT a
    Work (T2); a per-manifestation asset excluded from ``release_hash`` (A6)."""

    model_config = _CFG

    offset: float
    title: str = ""
    image: str = ""
    end: Optional[float] = None
    # No back-reference to a Work: a chapter is a pure navigation marker
    # (§5.4). A segment that is itself a distinct Work is an `Appearance` in
    # `Release.contents`, not a Chapter — keeping the "Chapter is NOT a Work"
    # invariant clean (T2, A7).


class AccessibilityTrack(BaseModel):
    """Per-Release accessibility asset (spec: §5.4). Acquired over a Release's
    lifetime; excluded from ``release_hash`` (A6)."""

    model_config = _CFG

    kind: AccessibilityKind
    language: str = ""
    uri: str = ""
    forced: bool = False
    sdh: bool = False
    note: Optional[str] = None


class AvailabilityWindow(BaseModel):
    """A single (start, end) availability window — the §5.5 broadcast-slot
    derivation, not a model (spec: §5.4/§5.5). None = open-ended on that side
    (A2 — absence is not a value). `start` / `end` are the `IsoDate` boundary
    type (§6.7): an ISO-8601 date or a datetime with offset; the datetime form
    lets one window carry a broadcast slot (§5.5)."""

    model_config = _CFG

    start: Optional[IsoDate] = None
    end: Optional[IsoDate] = None
    note: str = ""

    @model_validator(mode="after")
    def _check(self) -> "AvailabilityWindow":
        if self.start is not None and self.end is not None:
            if iso_compare(self.end, self.start) < 0:
                raise ValueError("AvailabilityWindow.end precedes start")
        return self


class WorkRelation(BaseModel):
    """Work→Work relation (spec: A9, §4.13/§5.1). Navigation/description, never
    identity (A6) — absent from ``work_hash``."""

    model_config = _CFG

    kind: WorkRelationKind
    target: "Work"
    note: Optional[str] = None


class ReleaseRelation(BaseModel):
    """Release→Release lineage (spec: A9, §4.13/§5.1). Navigation/description,
    never identity (A6). Use sparingly — most distinctions are encoded by
    format/packaging fields plus `release_hash`."""

    model_config = _CFG

    kind: ReleaseRelationKind
    target: "Release"
    note: Optional[str] = None


class Work(BaseModel):
    """The canonical creative artefact — the first identity of §1.3 (spec: T2, §5.3).

    Distinct from Release and Appearance by T2. Its identity fields (§1.5) are
    the ``work_hash`` inputs (§6.3); its routing and description fields are
    excluded by A6. Does not contain playback URIs — those live on Release (A3).
    Two records describing the same song on two different albums share a Work.
    """

    model_config = _CFG

    # --- Identity (work_hash inputs, §6.3; immutable after canonicalisation, §8.1) ---
    title: str                                       # normalise_title → work_hash (§6.3)
    media_type: MediaType                            # schema axis (A1, §3.2); work_hash input
    content_form: ContentForm = ContentForm.PRIMARY  # experiential axis (A8a); enters work_hash by A8b (§6.3)

    # Temporal — identity (year, runtime are work_hash inputs; §6.3)
    year: Optional[int] = None
    runtime: Optional[float] = None                  # quantum-rounded per MediaType in work_hash (§6.2/§6.3)

    # Language — identity (`language` is a work_hash input; original_languages is description)
    language: str = ""
    original_languages: List[str] = Field(default_factory=list)   # description (A6); excluded from hash

    # Geographic provenance — identity (the one non-empty slot is the work_hash
    # country_slot, §6.3). Exactly one non-empty per MediaType; validator
    # enforces exclusivity only, not slot-match (§5.3).
    production_country: str = ""
    publication_country: str = ""
    broadcaster_country: str = ""

    # Episode / series structure — identity (season/episode/series_title are
    # work_hash inputs, §6.3; series_title disambiguates S01E01 collisions).
    # episode_orderings is description (A6).
    season: Optional[int] = None
    episode: Optional[int] = None
    series_title: Optional[str] = None
    episode_orderings: Dict[str, int] = Field(default_factory=dict)   # description (A6)

    # Edition — identity, Work-only (restructurings produce new Works, §3.4);
    # variant_kind / edition / source_format are work_hash inputs (§6.3).
    variant_kind: Optional[VariantKind] = None
    edition: str = ""
    source_format: str = ""

    # Routing — excluded from work_hash (A6)
    content_genres: List[str] = Field(default_factory=list)         # aesthetic axis (T1/A6, §3.6)
    programme_format: Optional[ProgrammeFormat] = None             # routing (A6, §3.7)
    picture_format: Optional[PictureFormat] = None   # presentation attr (T6); routing (A6, §3.11)
    release_status: ReleaseStatus = ReleaseStatus.RELEASED         # lifecycle, description (A6, §4.9)

    # Discovery / description — not part of identity hash (A6)
    aka: List[str] = Field(default_factory=list)
    localized_titles: List[LocalizedTitle] = Field(default_factory=list)

    # Credits and containment — description (A6); accumulate as enrichment
    credits: List[Credit] = Field(default_factory=list)           # §1.4 Entity→Work edges
    tracklist: List[Appearance] = Field(default_factory=list)     # §1.4 canonical member order
    relations: List[WorkRelation] = Field(default_factory=list)   # A9 navigation edges

    # Cross-references — description (A6, §7.1); extra is the §8.3 escape hatch
    external_ids: Dict[str, str] = Field(default_factory=dict)    # canonical persistence form (§7.1)
    extra: Dict[str, Any] = Field(default_factory=dict)           # escape hatch (§8.3); never read by mediavocab

    @property
    def external_ids_model(self) -> ExternalIds:
        """Access `external_ids` as a typed `ExternalIds` model."""
        from mediavocab.models.external_ids import ExternalIds
        return ExternalIds.from_dict(self.external_ids)

    @external_ids_model.setter
    def external_ids_model(self, value: ExternalIds) -> None:
        """Update `external_ids` from a typed `ExternalIds` model."""
        self.external_ids = value.to_dict()

    @field_validator("content_genres", mode="before")
    @classmethod
    def _normalise_genres(cls, v):
        """Lowercase and strip whitespace; warn on unknown genre values."""
        if not v:
            return v
        from mediavocab.taxonomy.genre import KNOWN_GENRES
        result = []
        for g in v:
            if isinstance(g, str):
                g = g.strip().lower()
                if g not in KNOWN_GENRES:
                    _LOG.warning("Unknown genre %r — not in KNOWN_GENRES", g)
            result.append(g)
        return result

    @model_validator(mode="after")
    def _check(self) -> "Work":
        # T8: pipeline sentinels never reach a canonical Work (← A4). A Work
        # constructed with GENERIC / NOT_MEDIA / CONTROL raises at validation.
        if self.media_type in PIPELINE_SENTINELS:
            raise ValueError(
                f"Work.media_type must be a concrete kind; "
                f"{self.media_type.value!r} is a pipeline sentinel (T8)"
            )
        # §5.3: at most one country slot non-empty (the single work_hash
        # country_slot input, §6.3). All-empty is valid (co-productions, etc.).
        slots = [self.production_country, self.publication_country, self.broadcaster_country]
        if sum(1 for s in slots if s) > 1:
            raise ValueError(
                "Work: at most one of production_country / publication_country / "
                "broadcaster_country may be set"
            )
        return self

    @property
    def country(self) -> str:
        """The one non-empty country slot, or `""` (§6.3 country_slot).

        A read-only resolver over the per-MediaType slots
        (`production_country` / `publication_country` / `broadcaster_country`)
        — attribute-style for parity with the other Work fields. Not a stored
        field and not serialised, so it never double-emits the slot value (A7).
        """
        return (
            self.production_country
            or self.publication_country
            or self.broadcaster_country
            or ""
        )

    @classmethod
    def from_signals(cls, signals: "Signals", **overrides) -> "Work":
        """Construct a Work from a resolved Signals bag.

        Maps Signals fields to Work fields. Signals-only routing hints
        (``include_variants``, ``playback_type``, ``role``, ``fanedit_subtype``,
        ``content_form``, ``accessibility``) are silently dropped. (Accessibility
        is a per-Release asset on Work — a ``List[AccessibilityTrack]`` on
        ``Release`` — not a Work-level kind list, so the Signals hint has no
        Work target.)

        ``**overrides`` are applied last — pass ``credits``, ``external_ids``,
        ``tracklist``, etc. to enrich the result beyond what Signals carries.

        Raises ``ValueError`` if ``signals.title`` is absent (required on Work).
        """
        if not signals.title:
            raise ValueError("Work.from_signals() requires signals.title to be set")

        media_type = signals.medium
        if media_type is None:
            raise ValueError("Work.from_signals() requires signals.medium to be set")

        # Map the Signals country hint to the appropriate Work slot.
        country_val = getattr(signals, "country", None) or ""
        country_slot_name = COUNTRY_SLOT_FOR.get(media_type, "production_country")
        country_kwargs: Dict[str, str] = {}
        if country_val:
            country_kwargs[country_slot_name] = country_val

        kwargs: Dict[str, Any] = dict(
            title=signals.title,
            media_type=media_type,
            **country_kwargs,
        )
        for src, dst in (
            ("year",         "year"),
            ("runtime",      "runtime"),
            ("language",     "language"),
            ("season",       "season"),
            ("episode",      "episode"),
            ("variant_kind", "variant_kind"),
            ("edition",      "edition"),
            ("source_format","source_format"),
            ("picture_format","picture_format"),
            ("programme_format","programme_format"),
        ):
            v = getattr(signals, src, None)
            if v is not None and v != "":
                kwargs[dst] = v
        if signals.content_genres:
            kwargs["content_genres"] = list(signals.content_genres)
        if signals.artist:
            # artist is a display-level hint; store it in structured signals_meta
            kwargs.setdefault("extra", {}).setdefault("signals_meta", {})["artist"] = signals.artist
            # Backward compatibility
            kwargs.setdefault("extra", {})["signals_artist"] = signals.artist

        kwargs.update(overrides)
        return cls(**kwargs)


class Release(BaseModel):
    """A specific physical or digital manifestation of a Work — the second
    identity of §1.3 (spec: T2/A3/T6, §5.4).

    Distinct from the Work by T2 and varying independently of it by A3 (delivery
    is not identity). Every technical attribute here is a Release field by T6;
    none back-propagates into the Work. Identity fields are the ``release_hash``
    inputs (§6.4); packaging/quality/availability are description (A6).
    """

    model_config = _CFG

    work: Work                               # the Work this Release manifests (§5.4)

    # Packaging — description-family (A6); excluded from release_hash (§6.4)
    packaging: Optional[ReleasePackaging] = None
    edition: str = ""
    region: str = ""                         # identity: release_hash input (§6.4)

    # Format identity (T6) — release_hash inputs (§6.4)
    container: str = ""
    codec: str = ""
    bitrate: str = ""
    platform: str = ""
    resolution: str = ""

    # Audio / video quality — description (T6 attributes, not identity); excluded from release_hash (§6.4)
    hdr: str = ""
    audio_channels: str = ""
    sample_rate: Optional[int] = None
    frame_rate: Optional[float] = None
    aspect_ratio: str = ""
    color: Optional[bool] = None
    audio_present: Optional[bool] = None
    picture_format: Optional[PictureFormat] = None   # presentation attr (T6); routing (A6)

    # Delivery — routing (A3, §3.9); not identity
    stream_mode: StreamMode = StreamMode.ON_DEMAND

    # Localisation
    audio_language: str = ""                          # identity: release_hash input — the dub defines the version (§6.4)
    subtitle_languages: List[str] = Field(default_factory=list)   # description (A6); added freely

    # Lifecycle
    release_status: ReleaseStatus = ReleaseStatus.RELEASED
    release_date: Optional[IsoDate] = None

    # Rights and availability
    # license is the canonical SPDX-style string (A7 — one source of truth);
    # "" means unknown (A2). The typed view is the read-only `.license_model`
    # overlay (§7.2), mirroring `external_ids` / `.external_ids_model`.
    license: str = ""
    region_locked: Optional[bool] = None
    regions_available: List[str] = Field(default_factory=list)
    # Availability timing lives in one typed home (A7). A single open- or
    # closed-ended window is `availability_windows=[AvailabilityWindow(...)]`;
    # there are no parallel scalar `available_from` / `available_until` fields.
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
    extra: Dict[str, Any] = Field(default_factory=dict)

    @property
    def external_ids_model(self) -> ExternalIds:
        """Access `external_ids` as a typed `ExternalIds` model."""
        from mediavocab.models.external_ids import ExternalIds
        return ExternalIds.from_dict(self.external_ids)

    @external_ids_model.setter
    def external_ids_model(self, value: ExternalIds) -> None:
        """Update `external_ids` from a typed `ExternalIds` model."""
        self.external_ids = value.to_dict()

    @field_validator("license", mode="before")
    @classmethod
    def _coerce_license(cls, v):
        """Canonical license is a string (A7). Accept a typed `License`
        (or None) on intake and reduce it to its SPDX identifier so the
        string stays the single source of truth."""
        if v is None:
            return ""
        if isinstance(v, License):
            return v.identifier
        return v

    @property
    def license_model(self) -> Optional[License]:
        """Read-only typed view of `license` (§7.2). `None` when unknown
        (empty string); otherwise `License.from_spdx(self.license)`. The
        string is canonical — set `release.license`, not this overlay."""
        s = (self.license or "").strip()
        return License.from_spdx(s) if s else None

    @model_validator(mode="after")
    def _check(self) -> "Release":
        # §5.5 closure: availability windows ordered, non-overlapping, at most
        # one open-ended (must be last) — the broadcast-slot invariant that lets
        # AvailabilityWindow subsume a Schedule/Programme model (§1.4 closure).
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
