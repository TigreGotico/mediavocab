"""Cross-source resolver protocol — typed shape only, no runtime registry.

Defines the typed interface a metadata provider implements when
participating in a cross-source resolver pipeline:

- :class:`ProviderMatch` — what a provider returns for a given
  :class:`~mediavocab.models.Signals` query.
- :class:`MetadataProvider` — the runtime ``Protocol`` every concrete
  provider implements.
- :class:`ResolutionConflict` — a single match dropped by the
  consolidator because it disagreed with what was already accepted.

The actual registry, dispatcher, and consolidation logic live in
downstream packages (e.g. ``metadatarr.resolve``). This module is the
shared contract — every cross-source resolver in the ecosystem speaks
the same shape regardless of who hosts the implementation.
"""
from __future__ import annotations

from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Set,
    runtime_checkable,
)

from pydantic import BaseModel, ConfigDict, Field

from mediavocab.models.external_ids import ExternalIds
from mediavocab.models.signals import Signals, SignalConflict
from mediavocab.taxonomy import MediaType


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

    Surfacing these is how a resolver explains "we ignored provider X
    on these fields" without silently throwing the data away.
    """

    model_config = ConfigDict(extra="forbid")

    provider: str
    """The provider whose match was dropped."""

    against: str
    """Either ``"local"`` (disagreed with the input query) or the name
    of the already-accepted provider that anchored the result."""

    fields: List[SignalConflict] = Field(default_factory=list)
    """The specific :class:`SignalConflict` entries that triggered the
    drop."""


@runtime_checkable
class MetadataProvider(Protocol):
    """Typed interface every resolver-participating provider implements.

    A provider is anything that, given a :class:`Signals` query,
    returns zero or more :class:`ProviderMatch` results. The optional
    :attr:`media` and :attr:`genre_filter` class-level attributes let
    a dispatcher gate calls without invoking the provider:

    - ``media`` — the set of ``MediaType`` values this provider
      handles. Empty set ⇒ universal w.r.t. media type.
    - ``genre_filter`` — the set of genre tags (typically
      ``mediavocab.taxonomy.genre`` constants) that must overlap with
      ``signals.content_genres`` for this provider to be eligible.
      Empty set ⇒ no genre gate.

    Anime / manga-only providers therefore declare e.g.
    ``media = {EPISODIC_SERIES, MOVIE}`` plus
    ``genre_filter = {"anime"}`` rather than a fake
    ``MediaType.ANIME`` value (anime is a *genre*, per spec axiom 2).
    """

    name: ClassVar[str]
    """Stable provider name — used as the registry key and as
    ``ProviderMatch.provider``."""

    media: ClassVar[Set[MediaType]]
    """Media-type gate. Empty ⇒ universal."""

    genre_filter: ClassVar[Set[str]]
    """Genre-tag gate. Empty ⇒ no gate. When set, at least one tag
    must appear in ``signals.content_genres`` for the provider to be
    invoked."""

    def is_available(self) -> bool:
        """True if the provider has all the configuration it needs
        (API keys, optional dependencies, …) to actually run."""

    def lookup(self, signals: Signals) -> Optional[ProviderMatch]:
        """Return the single best match for ``signals``, or ``None``."""

    def matches(self, signals: Signals) -> bool:
        """Default routing test used by dispatchers:

        - ``media`` empty OR ``signals.medium`` is ``None`` OR
          ``signals.medium in self.media``
        - AND
        - ``genre_filter`` empty OR ``self.genre_filter`` overlaps
          ``signals.content_genres``
        """


def provider_matches(provider: MetadataProvider, signals: Signals) -> bool:
    """Reference implementation of :meth:`MetadataProvider.matches`.

    Dispatcher implementations should follow this exact gate so
    cross-package routing is consistent.
    """
    media = getattr(provider, "media", None) or set()
    if media and signals.medium and signals.medium not in media:
        return False
    genre_filter = getattr(provider, "genre_filter", None) or set()
    if genre_filter:
        tags = set(signals.content_genres or [])
        if not (tags & genre_filter):
            return False
    return True
