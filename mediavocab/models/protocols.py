"""Cross-source resolver contract — abstract base, no runtime registry.

Defines the typed interface a metadata provider implements when participating
in a cross-source resolver pipeline. Spec §4.11 (PlaybackType routing rule).

The actual registry, dispatcher, and consolidation logic live in downstream
packages (e.g. `metadatarr.resolve`). This module is the shared contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from mediavocab.models.external_ids import ExternalIds
from mediavocab.models.signals import Signals, SignalConflict
from mediavocab.taxonomy import MediaType, PlaybackType


class ProviderMatch(BaseModel):
    """One provider's response to a `Signals` query."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    confidence: float = Field(ge=0.0, le=1.0)
    signals: Signals = Field(default_factory=Signals)
    external_ids: ExternalIds = Field(default_factory=ExternalIds)


class ResolutionConflict(BaseModel):
    """One provider match dropped because it disagreed with the accepted result."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    against: str
    fields: List[SignalConflict] = Field(default_factory=list)


class MetadataProvider(ABC):
    """Abstract base for cross-source resolver providers.

    Routing is three-axis, each axis orthogonal (A6):

    - `media`         — set of `MediaType` values handled.
    - `playback_type` — set of `PlaybackType` values handled.
    - `genre_filter`  — set of genre tags from `mediavocab.taxonomy.genre`.

    A provider matches when ALL three hold:

        (no `media`         declared OR signals.medium       in self.media)
        AND (no `playback_type` declared OR signals.playback_type in self.playback_type)
        AND (no `genre_filter`  declared OR self.genre_filter ∩ signals.content_genres)

    The ``content_form`` axis was removed — no real provider filters on
    ContentForm, and it added complexity with no real-world benefit.
    """

    name: ClassVar[str] = ""
    media: ClassVar[Set[MediaType]] = set()
    playback_type: ClassVar[Set[PlaybackType]] = set()
    genre_filter: ClassVar[Set[str]] = set()

    @abstractmethod
    def is_available(self) -> bool:
        """True iff the provider has its configuration / credentials / dependencies."""

    @abstractmethod
    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        """Return the single best match for `signals`, or `None`."""

    def matches(self, signals: Signals) -> bool:
        """Default three-axis routing test."""
        return _three_axis_gate(
            self.media, self.playback_type, self.genre_filter,
            signals,
        )


def _three_axis_gate(
    media: Set[MediaType],
    playback_type: Set[PlaybackType],
    genre_filter: Set[str],
    signals: Signals,
) -> bool:
    """Single source of truth for the three-axis routing gate (A6)."""
    if media and signals.medium and signals.medium not in media:
        return False
    if playback_type and signals.playback_type and signals.playback_type not in playback_type:
        return False
    if genre_filter:
        tags = set(signals.content_genres or [])
        if not (tags & genre_filter):
            return False
    return True


def provider_matches(provider: MetadataProvider, signals: Signals) -> bool:
    """Standalone gate, callable on any object declaring the three ClassVars."""
    return _three_axis_gate(
        getattr(provider, "media", None) or set(),
        getattr(provider, "playback_type", None) or set(),
        getattr(provider, "genre_filter", None) or set(),
        signals,
    )
