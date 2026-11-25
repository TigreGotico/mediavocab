# Independent creators, YouTube, AI-generated content
<!-- agent-hint
covers: how to model independent creators, YouTube and AI content
source: mediavocab/models/entity.py
generated: no
verify: python -m pytest -q tests/models/test_entity.py
see: classifying-scraped-content.md
-->

## YouTube and independent creators

A YouTube series is a `SERIES` Entity. Individual episodes are `Work`s with
`media_type=MediaType.EPISODIC_SERIES` and `episode` set. The channel/creator is a
`PERSON` or `GROUP` Entity with `external_ids = {"youtube": "@channel"}`.
The platform itself is an `ORGANISATION` Entity (rarely needed in records).

Single one-off videos: `MediaType.MOVIE` with `runtime` set. YouTube channel
as the publishing entity in `credits` (`RelationRole.PUBLISHER`).

## AI-generated content

Tag with `content_genres += [GENRE_AI_GENERATED]`. The model used (Suno,
Runway, etc.) goes in `Entity.extra` or on the relevant `Credit.note`. The
Work itself is classified by what it *is* (MUSIC, MOVIE, IMAGE-as-MOVIE-still, …)
and the AI-generated genre is an orthogonal flag exactly like `GENRE_ADULT`.

---
[← Motion comics](motion-comics.md) · [Home](../README.md) · [Classifying scraped content →](classifying-scraped-content.md)
