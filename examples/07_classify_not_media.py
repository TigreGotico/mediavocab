"""Use NOT_MEDIA as a terminal classifier sentinel.

A classifier may produce both media and non-media outputs. NOT_MEDIA lets
the routing layer cleanly exclude non-media intents BEFORE attempting any
provider resolution. GENERIC is the transient counterpart: type unknown,
resolution may clarify.
"""
from mediavocab import MediaType, Work
from mediavocab.helpers import is_not_media, is_generic


def main() -> None:
    inputs = [
        Work(title="when is Christopher Nolan's birthday",
             media_type=MediaType.NOT_MEDIA),
        Work(title="turn off the lights",
             media_type=MediaType.NOT_MEDIA),
        Work(title="play Inception",
             media_type=MediaType.MOVIE),
        Work(title="play something fun",
             media_type=MediaType.GENERIC),
    ]

    for w in inputs:
        if is_not_media(w):
            print(f"  [skip]    {w.title!r}  -> NOT_MEDIA")
        elif is_generic(w):
            print(f"  [resolve] {w.title!r}  -> GENERIC")
        else:
            print(f"  [media]   {w.title!r}  -> {w.media_type.value}")


if __name__ == "__main__":
    main()
