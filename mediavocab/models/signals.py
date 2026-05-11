"""Signals — the resolver query / observation / consensus model.

``Signals`` exists *only* in the resolver pipeline. The taxonomy and
``Work`` / ``Release`` / ``Entity`` models do not use it; persisted
records are ``Work``s. See spec §1.7 (non-goals) and the
provider-protocol pattern doc for the full scope rules.

The same shape carries three roles, distinguished by *direction of flow*:

1. **Query** (caller → resolver). Filled with what the caller knows;
   passed to ``MetadataProvider.matches(signals)`` to gate dispatch
   and ``MetadataProvider.lookup(signals)`` to fetch.
2. **Observation** (provider → consolidator). The provider re-emits a
   ``Signals`` on its ``ProviderMatch.signals`` describing what *it*
   believes the work is. The consolidator compares observations
   across providers via :func:`compare_signals` and discards
   conflicts.
3. **Result** (consolidator → caller). The merged consensus on
   ``ResolveResult.signals`` produced by :func:`merge_signals` — the
   closest the resolver pipeline gets to a ``Work``, but not a
   ``Work``: no canonical hash, no credits, no tracklist, no
   accessibility profile. A consumer that needs a ``Work`` calls a
   separate constructor (e.g.
   ``metadatarr.canonicalize.work_from_resolve_result``).

Why the field overlap with ``Work`` is intentional: cross-provider
comparison needs identical comparable structure. The duplication is
the reason the comparator can be written once. The orthogonality
axiom (A6) keeps ``Signals``-only fields off ``Work``:
``include_variants``, ``fanedit_subtype``, ``playback_type``,
``content_form`` are all routing hints, not identity claims.

Comparison rules (encoded in :func:`compare_signals`):

- A field absent on either side is **not** a disagreement.
- All overlapping fields must agree → matched.
- Any single overlapping field disagrees → conflict (caller decides
  whether to quarantine, demote confidence, or accept).
- ``playback_type`` is a query hint and is **never** a conflict-eligible
  field; providers don't observe it, the comparator skips it.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from mediavocab.taxonomy import MediaType, VariantKind, ContentForm
from mediavocab.taxonomy.modality import PlaybackType
from mediavocab.text.compare import (
    TITLE_MIN as _TITLE_MIN,
    ARTIST_MIN as _ARTIST_MIN,
    YEAR_WINDOW as _YEAR_WINDOW,
    RUNTIME_TOLERANCE_S as _RUNTIME_TOLERANCE_BY_TYPE,
)
from mediavocab.text.normalize import fuzzy_ratio, normalize as _normalize_text


# Default fallback runtime tolerance when no media_type is set.
RUNTIME_TOLERANCE_S = 5.0


class Signals(BaseModel):
    """Bag of signals extracted from one provider's response, normalised
    for cross-provider comparison.

    Sub-classifications of ``VariantKind`` that the foundation
    deliberately omits (FANFIX, FANMIX, FANEDIT_SHORT, BONUS_TRACKS)
    live in ``edition`` / ``fanedit_subtype`` as free strings.
    """

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    artist: Optional[str] = None       # for music/podcast: artist; for video: director
    year: Optional[int] = None
    country: Optional[str] = None      # ISO 3166-1 alpha-2
    runtime: Optional[float] = None    # seconds
    medium: Optional[MediaType] = None
    language: Optional[str] = None     # ISO 639-1
    season: Optional[int] = None       # episodic media
    episode: Optional[int] = None
    content_genres: List[str] = Field(default_factory=list)

    # Release-variant signals
    variant_kind: Optional[VariantKind] = None
    edition: Optional[str] = None
    region: Optional[str] = None       # release region (distinct from origin country)
    source_format: Optional[str] = None

    # Sub-classifications excluded from the foundation VariantKind enum
    # (e.g. "fanfix", "fanmix", "fanedit_short").
    fanedit_subtype: Optional[str] = None

    # Resolver hint — should the cross-source resolver fan out to
    # variant-aware providers? Defaults to False.
    include_variants: bool = False

    # ContentForm hint (§3.3) — primary vs trailer / supplement / reaction.
    # Routing field; the consolidator filters providers when set.
    content_form: Optional[ContentForm] = None

    # Routing-axis hint, orthogonal to ``medium``. The resolver gate
    # filters providers by ``provider.playback_type`` ∋ ``signals.playback_type``;
    # ``None`` means "no preference". Never participates in identity or
    # in :func:`compare_signals` — it is a query field, never observed.
    playback_type: Optional[PlaybackType] = None


class SignalConflict(BaseModel):
    """One signal field on which two ``Signals`` bags disagree."""

    model_config = ConfigDict(extra="forbid")

    signal: str
    ours: Any
    theirs: Any


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def _agree_year(a: int, b: int, tolerance: int = _YEAR_WINDOW) -> bool:
    return abs(int(a) - int(b)) <= tolerance


def _agree_runtime(a: float, b: float, tolerance: float = RUNTIME_TOLERANCE_S) -> bool:
    return abs(float(a) - float(b)) <= tolerance


def _agree_string(a: str, b: str, threshold: float) -> bool:
    return fuzzy_ratio(a, b) >= threshold


def compare_signals(ours: Signals, theirs: Signals) -> List[SignalConflict]:
    """Return overlapping fields that disagree. Empty list ⇒ matched.

    No-overlap is treated as agreement (a missing value is unknown,
    not contradictory).
    """
    conflicts: List[SignalConflict] = []

    if ours.title and theirs.title and not _agree_string(
        ours.title, theirs.title, _TITLE_MIN
    ):
        conflicts.append(SignalConflict(signal="title", ours=ours.title,
                                        theirs=theirs.title))

    if ours.artist and theirs.artist and not _agree_string(
        ours.artist, theirs.artist, _ARTIST_MIN
    ):
        conflicts.append(SignalConflict(signal="artist", ours=ours.artist,
                                        theirs=theirs.artist))

    if ours.year is not None and theirs.year is not None and not _agree_year(
        ours.year, theirs.year
    ):
        conflicts.append(SignalConflict(signal="year", ours=ours.year,
                                        theirs=theirs.year))

    if ours.country and theirs.country and ours.country.upper() != theirs.country.upper():
        conflicts.append(SignalConflict(signal="country", ours=ours.country,
                                        theirs=theirs.country))

    if ours.runtime is not None and theirs.runtime is not None:
        m = ours.medium or theirs.medium
        tol = _RUNTIME_TOLERANCE_BY_TYPE.get(m, RUNTIME_TOLERANCE_S) if m else RUNTIME_TOLERANCE_S
        if not _agree_runtime(ours.runtime, theirs.runtime, tolerance=tol):
            conflicts.append(SignalConflict(signal="runtime", ours=ours.runtime,
                                            theirs=theirs.runtime))

    if ours.season is not None and theirs.season is not None and ours.season != theirs.season:
        conflicts.append(SignalConflict(signal="season", ours=ours.season,
                                        theirs=theirs.season))

    if ours.episode is not None and theirs.episode is not None and ours.episode != theirs.episode:
        conflicts.append(SignalConflict(signal="episode", ours=ours.episode,
                                        theirs=theirs.episode))

    if ours.medium and theirs.medium and ours.medium != theirs.medium:
        conflicts.append(SignalConflict(signal="medium",
                                        ours=ours.medium.value,
                                        theirs=theirs.medium.value))

    if ours.language and theirs.language and ours.language.lower() != theirs.language.lower():
        conflicts.append(SignalConflict(signal="language", ours=ours.language,
                                        theirs=theirs.language))

    if ours.variant_kind and theirs.variant_kind and ours.variant_kind != theirs.variant_kind:
        conflicts.append(SignalConflict(signal="variant_kind",
                                        ours=ours.variant_kind.value,
                                        theirs=theirs.variant_kind.value))

    if ours.region and theirs.region and ours.region.upper() != theirs.region.upper():
        conflicts.append(SignalConflict(signal="region", ours=ours.region,
                                        theirs=theirs.region))

    if (ours.source_format and theirs.source_format
            and ours.source_format.lower() != theirs.source_format.lower()):
        conflicts.append(SignalConflict(signal="source_format",
                                        ours=ours.source_format,
                                        theirs=theirs.source_format))

    if ours.edition and theirs.edition and ours.edition.lower() != theirs.edition.lower():
        conflicts.append(SignalConflict(signal="edition", ours=ours.edition,
                                        theirs=theirs.edition))

    if (ours.fanedit_subtype and theirs.fanedit_subtype
            and ours.fanedit_subtype.lower() != theirs.fanedit_subtype.lower()):
        conflicts.append(SignalConflict(signal="fanedit_subtype",
                                        ours=ours.fanedit_subtype,
                                        theirs=theirs.fanedit_subtype))

    return conflicts


def merge_signals(*bags: Signals) -> Signals:
    """First non-empty value wins per field. ``content_genres`` is
    unioned (insertion order preserved)."""
    fields = ("title", "artist", "year", "country", "runtime", "medium",
              "language", "season", "episode",
              "variant_kind", "edition", "region", "source_format",
              "fanedit_subtype")
    out: Dict[str, Any] = {}
    for f in fields:
        for b in bags:
            v = getattr(b, f, None)
            if v not in (None, ""):
                out[f] = v
                break
    seen: set = set()
    genres: List[str] = []
    for b in bags:
        for g in getattr(b, "content_genres", None) or []:
            if g not in seen:
                seen.add(g)
                genres.append(g)
    out["content_genres"] = genres
    out["include_variants"] = any(getattr(b, "include_variants", False) for b in bags)
    return Signals(**out)


def match_quality(local: Signals, candidate: Signals) -> float:
    """Score how well ``candidate`` matches ``local`` on ``[0.0, 1.0]``.

    Title fuzzy ratio drives the score; year and medium mismatches
    halve it. Returns 1.0 when one side has no overlapping fields to
    compare against.
    """
    score = 1.0
    if local.title and candidate.title:
        score *= fuzzy_ratio(local.title, candidate.title)
    if local.year is not None and candidate.year is not None:
        if not _agree_year(local.year, candidate.year):
            score *= 0.5
    if local.medium and candidate.medium and local.medium != candidate.medium:
        score *= 0.5
    return max(0.0, min(score, 1.0))


def signal_hash(s: Signals) -> str:
    """A stable hash over the immutable signals — used as a canonical-id
    seed by resolvers."""
    parts = [
        _normalize_text(s.title or ""),
        _normalize_text(s.artist or ""),
        str(s.year) if s.year is not None else "",
        (s.country or "").upper(),
        f"{round(s.runtime):d}" if s.runtime is not None else "",
        s.medium.value if s.medium else "",
        (s.language or "").lower(),
        f"S{s.season}" if s.season is not None else "",
        f"E{s.episode}" if s.episode is not None else "",
        s.variant_kind.value if s.variant_kind else "",
        (s.edition or "").lower(),
        (s.region or "").upper(),
        (s.source_format or "").lower(),
        (s.fanedit_subtype or "").lower(),
    ]
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()
