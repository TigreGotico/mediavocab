"""Serialization round-trip — the persisted form is part of the 1.0 contract.

Consumers serialize Works/Releases/Entities to dict/JSON (caches, datasets,
APIs) and read them back. If a round-trip ever stops reconstructing the same
identity, every persisted record silently rots. These tests pin that a model
survives ``model_dump`` / ``model_dump_json`` → ``model_validate`` with its
identity hash intact.
"""
from mediavocab import (
    Work, Release, Entity, EntityRef, ExternalIds, MediaType, EntityKind,
    OrganisationKind, ContentForm, VariantKind,
)
from mediavocab.text import work_hash, release_hash


def _work():
    return Work(
        title="Blade Runner", media_type=MediaType.MOVIE, year=1982,
        production_country="US", language="en", runtime=117.0,
        content_form=ContentForm.PRIMARY, variant_kind=VariantKind.DIRECTORS,
        edition="Final Cut", source_format="bluray",
        content_genres=["sci_fi"], aka=["Blade Runner: The Final Cut"],
        external_ids={"imdb": "tt0083658"},
    )


def test_work_dict_roundtrip_preserves_identity():
    w = _work()
    w2 = Work.model_validate(w.model_dump())
    assert work_hash(w) == work_hash(w2)
    assert w2.country == "US"  # property still resolves


def test_work_json_roundtrip_preserves_identity():
    w = _work()
    w2 = Work.model_validate_json(w.model_dump_json())
    assert work_hash(w) == work_hash(w2)


def test_release_roundtrip_preserves_identity():
    r = Release(work=_work(), codec="audio/mpeg", container="mp3",
                bitrate="320", region="US", platform="bandcamp")
    r2 = Release.model_validate(r.model_dump())
    assert release_hash(r) == release_hash(r2)


def test_entity_roundtrip():
    e = Entity(name="BBC Radio 4", kind=EntityKind.ORGANISATION,
               org_kind=OrganisationKind.BROADCASTER, aliases=["R4"],
               external_ids={"wikidata": "Q1063"})
    e2 = Entity.model_validate(e.model_dump())
    assert e2 == e


def test_external_ids_dict_roundtrip():
    ids = ExternalIds(imdb="tt1", tmdb_movie=348, igdb_id=7,
                      extra={"soundcloud_track_id": "9"})
    assert ExternalIds.from_dict(ids.to_dict()) == ids
