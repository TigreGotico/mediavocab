"""PlaybackType — the orthogonal routing axis (A6).

A request verb collapses cleanly onto a playback type: *"play X"* ⇒ AUDIO,
*"watch X"* / *"show me X"* ⇒ VIDEO, *"open X"* ⇒ PAGED or INTERACTIVE.
The resolver gates providers on `Signals.playback_type`, so a
`MediaType.GENERIC` query routed with `playback_type=AUDIO` never touches
video-only providers.

PlaybackType is NOT on Work — it's a routing concern, not identity (A6).
Use `infer_playback_type` to derive a default from `MediaType`.
"""
from typing import ClassVar, Set

from mediavocab import (
    MediaType, MetadataProvider, PlaybackType, ProviderMatch,
    Signals, infer_playback_type,
)


class AudioOnlyProvider(MetadataProvider):
    name: ClassVar[str] = "stub_audio"
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.AUDIO}

    def is_available(self) -> bool:
        return True

    def lookup(self, signals: Signals):
        return ProviderMatch(provider=self.name, confidence=1.0, signals=signals)


class VideoOnlyProvider(MetadataProvider):
    name: ClassVar[str] = "stub_video"
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.VIDEO}

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

    print("Default MediaType → PlaybackType mapping:")
    for mt in (MediaType.MUSIC, MediaType.MOVIE, MediaType.BOOK,
               MediaType.GAME, MediaType.PLAYLIST):
        print(f"  {mt.value:<22} → {infer_playback_type(mt).value}")

    print("\nVerb → playback-type routing demonstration:")
    cases = [
        ("\"play me Inception\" — AUDIO intent on a video work",
         Signals(title="Inception", medium=MediaType.MOVIE,
                 playback_type=PlaybackType.AUDIO)),
        ("\"watch Inception\" — VIDEO intent on a video work",
         Signals(title="Inception", medium=MediaType.MOVIE,
                 playback_type=PlaybackType.VIDEO)),
        ("\"play Daft Punk\" — AUDIO intent, no specific media hint",
         Signals(title="Daft Punk", playback_type=PlaybackType.AUDIO)),
        ("no playback hint — universal routing",
         Signals(title="Anything", medium=MediaType.MOVIE)),
    ]
    for label, sig in cases:
        matched = [p.name for p in providers if p.matches(sig)]
        print(f"\n  {label}")
        print(f"    → providers: {matched}")


if __name__ == "__main__":
    main()
