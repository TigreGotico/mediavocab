"""schema.org JSON-LD serialisation for Work and Release.

Produces dicts compatible with ``json.dumps`` that conform to schema.org
markup. Consumers can embed the output in ``<script type="application/ld+json">``
tags for SEO, pass it to linked-data pipelines, or use it as a portable
interchange format with tools that understand schema.org.

Only a subset of schema.org properties is mapped — the ones that correspond
directly to mediavocab fields with high confidence. Extension properties go
in ``extra_props`` kwargs.

Reference: https://schema.org
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from mediavocab.models.work import Release, Work

from mediavocab.taxonomy.media_type import MediaType

# mediavocab MediaType → schema.org @type
_TYPE_MAP: Dict[MediaType, str] = {
    MediaType.MOVIE:              "Movie",
    MediaType.SHORT_FILM:         "ShortStory",  # closest available
    MediaType.EPISODIC_SERIES:    "TVSeries",
    MediaType.TV:                 "BroadcastService",
    MediaType.MUSIC:              "MusicRecording",
    MediaType.MUSIC_VIDEO:        "MusicVideoObject",
    MediaType.PODCAST:            "PodcastSeries",
    MediaType.AUDIOBOOK:          "Audiobook",
    MediaType.AUDIO_DRAMA:        "RadioEpisode",
    MediaType.RADIO:              "RadioStation",
    MediaType.BOOK:               "Book",
    MediaType.COMIC:              "ComicStory",
    MediaType.GAME:               "VideoGame",
    MediaType.INTERACTIVE_FICTION: "SoftwareApplication",
    MediaType.SOUND_EFFECT:       "AudioObject",
    MediaType.PROCEDURAL_AMBIENT: "AudioObject",
    MediaType.PLAYLIST:           "MusicPlaylist",
}


def _iso_duration(seconds: float) -> str:
    """Convert seconds to ISO 8601 duration string (e.g. PT1H47M22S)."""
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    parts = "PT"
    if h:
        parts += f"{h}H"
    if m:
        parts += f"{m}M"
    if s or not (h or m):
        parts += f"{s}S"
    return parts


def work_to_schema_org(work: "Work", **extra_props) -> Dict[str, Any]:
    """Serialise a ``Work`` to a schema.org JSON-LD dict.

    Args:
        work: the Work to serialise.
        **extra_props: additional schema.org properties to merge in.

    Returns:
        A plain dict suitable for ``json.dumps``. The ``@context`` key is
        always ``"https://schema.org"``.
    """
    schema_type = _TYPE_MAP.get(work.media_type, "CreativeWork")

    out: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type":    schema_type,
        "name":     work.title,
    }

    if work.year:
        out["datePublished"] = str(work.year)
    if work.language:
        out["inLanguage"] = work.language
    if work.runtime:
        out["duration"] = _iso_duration(work.runtime)
    if work.content_genres:
        out["genre"] = list(work.content_genres)

    country = work.country
    if country:
        out["countryOfOrigin"] = {"@type": "Country", "name": country}

    if work.series_title:
        out["partOfSeries"] = {"@type": "CreativeWorkSeries",
                               "name": work.series_title}
    if work.season is not None:
        out["seasonNumber"] = work.season
    if work.episode is not None:
        out["episodeNumber"] = work.episode

    if work.aka:
        out["alternateName"] = work.aka[0] if len(work.aka) == 1 else work.aka

    # External IDs → sameAs links for well-known authorities
    eids = work.external_ids or {}
    same_as = []
    if eids.get("imdb"):
        same_as.append(f"https://www.imdb.com/title/{eids['imdb']}/")
    if eids.get("tmdb") or eids.get("tmdb_movie"):
        tid = eids.get("tmdb") or eids.get("tmdb_movie")
        same_as.append(f"https://www.themoviedb.org/movie/{tid}")
    if eids.get("musicbrainz_recording"):
        same_as.append(
            f"https://musicbrainz.org/recording/{eids['musicbrainz_recording']}"
        )
    if eids.get("wikidata"):
        same_as.append(f"https://www.wikidata.org/wiki/{eids['wikidata']}")
    if same_as:
        out["sameAs"] = same_as[0] if len(same_as) == 1 else same_as

    out.update(extra_props)
    return out


def release_to_schema_org(release: "Release", **extra_props) -> Dict[str, Any]:
    """Serialise a ``Release`` to a schema.org JSON-LD dict.

    Starts from ``work_to_schema_org(release.work)`` and adds delivery /
    availability / rights properties from the Release.

    Args:
        release: the Release to serialise.
        **extra_props: additional schema.org properties to merge in.
    """
    out = work_to_schema_org(release.work)

    if release.uri:
        out["url"] = release.uri
        out["contentUrl"] = release.uri
    if release.container:
        out["encodingFormat"] = release.container
    if release.audio_language:
        out["inLanguage"] = release.audio_language  # override with dub language

    if release.license:
        if release.license.url:
            out["license"] = release.license.url
        elif release.license.identifier:
            out["license"] = release.license.identifier

    if release.regions_available:
        out["availableInCountry"] = [
            {"@type": "Country", "name": r} for r in release.regions_available
        ]

    if release.available_from:
        out["availabilityStarts"] = str(release.available_from)
    if release.available_until:
        out["availabilityEnds"] = str(release.available_until)

    if release.image:
        out["image"] = release.image

    out.update(extra_props)
    return out
