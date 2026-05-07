"""PlaybackModality — the orthogonal routing axis (spec axiom 13).

A request verb collapses cleanly onto a modality: *"play X"* ⇒ AUDIO,
*"watch X"* / *"show me X"* ⇒ VIDEO, *"open X"* ⇒ TEXT or INTERACTIVE.
The resolver gates providers on ``Signals.modality``, so a
``MediaType.GENERIC`` query routed with ``modality=AUDIO`` never
touches video-only providers.

Modality is **not on Work** — it's a routing concern, not identity.
Use :func:`infer_modality` to derive a default from the work's
``MediaType``.
"""
from typing import ClassVar, Set

from mediavocab import (
    MediaType, MetadataProvider, PlaybackModality, ProviderMatch,
    Signals, infer_modality,
)


# ---------------------------------------------------------------------------
# Three stub providers — declare modality alongside media.
# ---------------------------------------------------------------------------

class AudioOnlyProvider(MetadataProvider):
    name: ClassVar[str] = "stub_audio"
    modality: ClassVar[Set[PlaybackModality]] = {PlaybackModality.AUDIO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return ProviderMatch(provider=self.name, confidence=1.0, signals=signals)


class VideoOnlyProvider(MetadataProvider):
    name: ClassVar[str] = "stub_video"
    modality: ClassVar[Set[PlaybackModality]] = {PlaybackModality.VIDEO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return ProviderMatch(provider=self.name, confidence=1.0, signals=signals)


class UniversalProvider(MetadataProvider):
    name: ClassVar[str] = "stub_universal"

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return ProviderMatch(provider=self.name, confidence=1.0, signals=signals)


def main() -> None:
    providers = [AudioOnlyProvider(), VideoOnlyProvider(), UniversalProvider()]

    print("Default MediaType → PlaybackModality mapping:")
    for mt in (MediaType.MUSIC, MediaType.MOVIE, MediaType.BOOK,
               MediaType.GAME, MediaType.GENERIC):
        print(f"  {mt.value:<22} → {infer_modality(mt).value}")

    print("\nVerb → modality routing demonstration:")
    cases = [
        ("\"play me Inception\" — AUDIO intent on a video work",
         Signals(title="Inception", medium=MediaType.MOVIE,
                 modality=PlaybackModality.AUDIO)),
        ("\"watch Inception\" — VIDEO intent on a video work",
         Signals(title="Inception", medium=MediaType.MOVIE,
                 modality=PlaybackModality.VIDEO)),
        ("\"play Daft Punk\" — AUDIO intent, no specific media hint",
         Signals(title="Daft Punk", modality=PlaybackModality.AUDIO)),
        ("no modality hint — universal routing",
         Signals(title="Anything", medium=MediaType.MOVIE)),
    ]
    for label, sig in cases:
        matched = [p.name for p in providers if p.matches(sig)]
        print(f"\n  {label}")
        print(f"    → providers: {matched}")


if __name__ == "__main__":
    main()
