"""Use the MediaType sentinels as terminal classifier outputs.

A classifier may produce both media and non-media outputs. The sentinel
MediaTypes (GENERIC, NOT_MEDIA, CONTROL) let the routing layer cleanly
exclude non-media intents BEFORE attempting any provider resolution. By T8
they NEVER reach a canonical Work — they live on the resolver bag
(Signals.medium).
"""
from mediavocab import MediaType, Signals
from mediavocab.helpers import is_not_media, is_generic, is_control


def main() -> None:
    queries = [
        ("when is Christopher Nolan's birthday",   MediaType.NOT_MEDIA),
        ("turn off the lights",                    MediaType.NOT_MEDIA),
        ("pause",                                  MediaType.CONTROL),
        ("seek to 3:00",                           MediaType.CONTROL),
        ("play Inception",                         MediaType.MOVIE),
        ("play something fun",                     MediaType.GENERIC),
    ]

    print("Classifier verdict on resolver-side Signals (never on Work):")
    for utter, classified in queries:
        sig = Signals(title=utter, medium=classified)
        m = sig.medium
        if is_not_media(m):
            tag = "[skip]   "
            verdict = "NOT_MEDIA"
        elif is_control(m):
            tag = "[control]"
            verdict = "CONTROL"
        elif is_generic(m):
            tag = "[resolve]"
            verdict = "GENERIC"
        else:
            tag = "[media]  "
            verdict = m.value
        print(f"  {tag} {utter!r:40s} -> {verdict}")


if __name__ == "__main__":
    main()
