# Classifying scraped content

`classify_video()` and `ContentType` were removed from mediavocab in v1.1 —
heuristic classification based on title strings is application logic, not
vocabulary. It belongs in downstream tools, not in a schema library.

This pattern shows how to classify scraped media content using the tools
mediavocab does ship.

## Step 1 — Parse the title

`parse_title()` extracts structured signals without needing to know the MediaType:

```python
from mediavocab.text import parse_title

result = parse_title("Blade Runner: The Director's Cut [1992] [Blu-ray]")
# result.title         → "Blade Runner"
# result.year          → 1992
# result.variant_kind  → VariantKind.DIRECTORS
# result.source_format → "Blu-ray"
# result.packaging     → None
```

## Step 2 — Build a query Signals

Use the parse result plus any domain knowledge (channel tags, feed metadata)
to build a Signals bag:

```python
from mediavocab import MediaType, Signals

query = Signals.as_query(
    title=result.title,
    year=result.year,
    variant_kind=result.variant_kind,
    source_format=result.source_format,
    medium=MediaType.MOVIE,  # you know this is a movie
    content_genres=["sci_fi"],  # from channel tags or feed metadata
)
```

If you don't know the MediaType, leave `medium=None` and let the resolver
fan out to all compatible providers.

## Step 3 — Resolve with a provider

Pass the query to a resolver (e.g. metadatarr):

```python
# metadatarr example — not shown here
# result_signals = resolver.resolve(query).signals
```

Or, if you have enough information, build a Work directly:

```python
from mediavocab import Work

work = Work.from_signals(query, production_country="US")
```

`Work.from_signals()` maps Signals fields to Work fields and routes the
`country` hint to the appropriate slot (production/publication/broadcaster)
based on MediaType.

## Classification heuristics without a resolver

If you have no resolver and need a best guess at MediaType from title alone:

```python
import re

_PODCAST_RE = re.compile(r"\b(episode|ep\.?\s*\d|podcast|interview)\b", re.I)
_AUDIOBOOK_RE = re.compile(r"\b(audiobook|narrated by|unabridged)\b", re.I)
_MUSIC_RE = re.compile(r"\b(album|single|EP|LP|track\s*\d)\b", re.I)

def guess_media_type(title: str, description: str = "") -> "MediaType":
    from mediavocab import MediaType
    text = f"{title} {description}"
    if _PODCAST_RE.search(text):
        return MediaType.PODCAST
    if _AUDIOBOOK_RE.search(text):
        return MediaType.AUDIOBOOK
    if _MUSIC_RE.search(text):
        return MediaType.MUSIC
    return MediaType.MOVIE  # safest default for video content
```

## Using content_genres for routing

Set `content_genres` from known tags before passing to a resolver — it
narrows provider dispatch via `genre_filter`:

```python
from mediavocab import KNOWN_GENRES

def sanitise_genres(raw_tags):
    """Normalise provider tags to KNOWN_GENRES values."""
    mapping = {"science fiction": "sci_fi", "k-pop": "pop", "j-pop": "pop",
               "hip hop": "hip_hop", "r&b": "rnb"}
    result = []
    for tag in raw_tags:
        normalised = tag.strip().lower().replace(" ", "_").replace("-", "_")
        normalised = mapping.get(tag.strip().lower(), normalised)
        if normalised in KNOWN_GENRES:
            result.append(normalised)
    return result
```
