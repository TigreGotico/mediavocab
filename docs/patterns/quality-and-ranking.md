# Quality and release ranking

Release ranking is application logic, not vocabulary. A scorer encodes
preferences (4K > 1080p, Atmos > stereo) that differ meaningfully between a
home-theatre collector, a mobile listener, and a bandwidth-constrained
archivist — no single ranking is correct, so mediavocab ships the release
fields and the availability predicate but leaves the scoring to the consumer.

This pattern shows how to implement release ranking for your use case.

## Pre-filter: is this release available?

Before ranking, filter to releases the user can actually access:

```python
from mediavocab.helpers import is_available

region = "US"
now = "2026-05-28"

accessible = [r for r in releases if is_available(r, region=region, at=now)]
```

## Reference implementation

Sort by a tuple: earlier elements in the tuple break ties later elements.
Adjust the ordering for your preference model.

```python
from mediavocab import Release, ReleasePackaging, VariantKind

# Preference rankings — higher index = better.
_RESOLUTION = ("", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p")
_HDR        = ("", "HDR10", "HDR10+", "HLG", "Dolby Vision")
_AUDIO      = ("", "mono", "stereo", "5.1", "7.1", "Atmos")
_PACKAGING  = {
    ReleasePackaging.BOOTLEG:  -1,
    ReleasePackaging.PROMO:     0,
    ReleasePackaging.OTHER:     0,
    ReleasePackaging.REGIONAL:  1,
    ReleasePackaging.REISSUE:   2,
    ReleasePackaging.BOX_SET:   3,
    ReleasePackaging.DELUXE:    4,
}
_VARIANT = {
    VariantKind.FANEDIT:      1,
    VariantKind.THEATRICAL:   2,
    VariantKind.EXTENDED:     3,
    VariantKind.REMASTERED:   4,
    VariantKind.PRESERVATION: 5,
    VariantKind.DIRECTORS:    6,
}


def _idx(value, order):
    try:
        return order.index(value or "")
    except ValueError:
        return -1


def quality_score(release: Release) -> tuple:
    """Sortable tuple — higher = preferred. Adjust weights for your use case."""
    return (
        _VARIANT.get(release.work.variant_kind, 0),
        _PACKAGING.get(release.packaging, 0),
        _idx(release.resolution, _RESOLUTION),
        _idx(release.hdr, _HDR),
        _idx(release.audio_channels, _AUDIO),
        release.sample_rate or 0,
    )


def best_release(*releases: Release):
    """Return the highest-quality Release, or None if empty."""
    if not releases:
        return None
    return max(releases, key=quality_score)
```

## Licence-aware ranking

Prefer open releases over proprietary ones:

```python
from mediavocab.helpers import release_is_open

open_releases = [r for r in releases if release_is_open(r)]
candidates = open_releases or releases  # fall back to all if none open
winner = best_release(*candidates)
```

## Format-preference ranking

A mobile-first app prefers small files:

```python
def mobile_score(release: Release) -> tuple:
    """Lower resolution is better for mobile."""
    LOW_BANDWIDTH = ("480p", "720p", "1080p", "2160p")
    return (
        _idx(release.resolution, LOW_BANDWIDTH),
        release.bitrate or "",  # smaller bitrate preferred
    )
```

## Using `score_breakdown` for debugging

`score_breakdown(query, candidate)` explains why `score()` returned a given value:

```python
from mediavocab.text import score_breakdown
bd = score_breakdown(film_a, film_b)
print(f"title={bd.title:.2f}, year={bd.year}, media={bd.media_type}, total={bd.total:.2f}")
```
