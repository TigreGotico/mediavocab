"""Cross-source resolver contract — abstract base, no runtime registry.

Defines the typed interface a metadata provider implements when
participating in a cross-source resolver pipeline:

- :class:`ProviderMatch` — what a provider returns for a given
  :class:`~mediavocab.models.Signals` query.
- :class:`MetadataProvider` — the abstract base every concrete provider
  inherits from. Subclass and implement :meth:`is_available` and
  :meth:`lookup`; :meth:`matches` ships with a default routing
  implementation that callers can override only when the default
  ``(media, genre_filter)`` gate is insufficient.
- :class:`ResolutionConflict` — a single match dropped by the
  consolidator because it disagreed with what was already accepted.

The actual registry, dispatcher, and consolidation logic live in
downstream packages (e.g. ``metadatarr.resolve``). This module is the
shared contract — every cross-source resolver in the ecosystem speaks
the same shape regardless of who hosts the implementation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field

from mediavocab.models.external_ids import ExternalIds
from mediavocab.models.signals import Signals, SignalConflict
from mediavocab.taxonomy import MediaType, PlaybackModality


class ProviderMatch(BaseModel):
    """One provider's response to a :class:`Signals` query.

    Carries the provider's name, a confidence in ``[0.0, 1.0]``, the
    extracted ``Signals`` (cross-provider comparable), and any
    ``ExternalIds`` that ID-anchor the match.
    """

    model_config = ConfigDict(extra="forbid")

    provider: str
    """Stable name of the provider that produced this match."""

    confidence: float = Field(ge=0.0, le=1.0)
    """``[0.0, 1.0]`` — how confident the provider is in this match."""

    signals: Signals = Field(default_factory=Signals)
    """The extracted signals; consumed by ``compare_signals`` /
    ``merge_signals`` for cross-provider consolidation."""

    external_ids: ExternalIds = Field(default_factory=ExternalIds)
    """Authoritative IDs the provider asserts for the match."""


class ResolutionConflict(BaseModel):
    """One provider match dropped from the consolidated result because
    it disagreed with what was already accepted.
    """

    model_config = ConfigDict(extra="forbid")

    provider: str
    against: str
    fields: List[SignalConflict] = Field(default_factory=list)


class MetadataProvider(ABC):
    """Abstract base every cross-source resolver provider inherits from.

    Routing is **three-axis**, with each axis orthogonal (spec axiom 13):

    - ``media`` — set of ``MediaType`` values this provider handles.
    - ``modality`` — set of ``PlaybackModality`` values (AUDIO / VIDEO /
      INTERACTIVE / TEXT / UNKNOWN). Lets a caller route a
      ``MediaType.GENERIC`` query to audio-only providers by passing
      ``Signals(modality=AUDIO)``.
    - ``genre_filter`` — set of genre tags from
      ``mediavocab.taxonomy.genre``.

    A provider matches when **all three** of the following hold:

        (no ``media`` declared OR signals.medium is None
         OR signals.medium in self.media)
        AND
        (no ``modality`` declared OR signals.modality is None
         OR signals.modality in self.modality)
        AND
        (no ``genre_filter`` declared
         OR self.genre_filter ∩ signals.content_genres)

    Anime / manga-only providers declare e.g.
    ``media = {EPISODIC_SERIES, MOVIE}`` plus
    ``genre_filter = {"anime"}`` rather than a fake
    ``MediaType.ANIME`` value (anime is a *genre*, per axiom 2).
    Audio-only book providers declare ``modality = {AUDIO}`` so a
    GENERIC query with ``modality=VIDEO`` skips them.

    Subclasses must implement :meth:`is_available` and :meth:`lookup`.
    Override :meth:`matches` only if the default three-axis gate is
    wrong for your provider.
    """

    name: ClassVar[str] = ""
    """Stable provider name — used as the registry key and as
    :attr:`ProviderMatch.provider`. Override in subclasses."""

    media: ClassVar[Set[MediaType]] = set()
    """Media-type gate. Empty ⇒ universal."""

    modality: ClassVar[Set[PlaybackModality]] = set()
    """Playback-modality gate. Empty ⇒ universal. When set, at least one
    of the modalities must match ``signals.modality`` for the provider
    to be invoked. ``signals.modality is None`` always passes."""

    genre_filter: ClassVar[Set[str]] = set()
    """Genre-tag gate. Empty ⇒ no gate. When set, at least one tag must
    appear in ``signals.content_genres`` for the provider to be invoked."""

    @abstractmethod
    def is_available(self) -> bool:
        """True if the provider has all the configuration it needs
        (API keys, optional dependencies, network reachability) to
        actually run."""

    @abstractmethod
    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        """Return the single best match for ``signals``, or ``None``."""

    def matches(self, signals: Signals) -> bool:
        """Default three-axis routing test. Override only if your
        provider needs a non-standard gate."""
        if self.media and signals.medium and signals.medium not in self.media:
            return False
        if self.modality and signals.modality and signals.modality not in self.modality:
            return False
        if self.genre_filter:
            tags = set(signals.content_genres or [])
            if not (tags & self.genre_filter):
                return False
        return True


def provider_matches(provider: MetadataProvider, signals: Signals) -> bool:
    """Free-function alias for :meth:`MetadataProvider.matches`.

    Kept for callers that prefer the procedural form. Identical
    semantics — both paths share the same gate.
    """
    return provider.matches(signals)
