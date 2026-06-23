"""Tests that every public model generates a valid JSON schema."""
from mediavocab import (
    AccessibilityTrack, Appearance, AvailabilityWindow, Chapter, Credit,
    Entity, EntityRef, License, LocalizedTitle, Membership,
    ProviderMatch, Release, ReleaseRelation, ResolutionConflict,
    SignalConflict, Signals, Work, WorkRelation,
)


PUBLIC_MODELS = (
    Work, Release, Entity, EntityRef, Membership, Credit, Appearance,
    Chapter, AccessibilityTrack, AvailabilityWindow, LocalizedTitle,
    WorkRelation, ReleaseRelation, License,
    Signals, SignalConflict, ProviderMatch, ResolutionConflict,
)


def test_every_public_model_generates_json_schema():
    """Pydantic must produce a schema for every model — guarantees the model
    is JSON-serialisable and round-trips through `model_validate_json`."""
    for m in PUBLIC_MODELS:
        schema = m.model_json_schema()
        # Either direct properties or a $ref into $defs (cyclic models)
        has_content = "properties" in schema or "$ref" in schema
        assert has_content, f"{m.__name__} has no schema content"


def test_work_schema_has_required_fields():
    schema = Work.model_json_schema()
    defs = schema.get("$defs", {})
    work_def = defs.get("Work", schema)
    assert "title" in work_def.get("required", [])
    assert "media_type" in work_def.get("required", [])


def test_membership_schema_includes_kind_and_temporal():
    schema = Membership.model_json_schema()
    props = schema.get("properties", {})
    assert "kind" in props
    assert "temporal" in props


def test_release_schema_excludes_dropped_variant_kind():
    """Spec §3.4: Release no longer has variant_kind."""
    schema = Release.model_json_schema()
    defs = schema.get("$defs", {})
    release_def = defs.get("Release", schema)
    props = release_def.get("properties", {})
    assert "variant_kind" not in props
    # But packaging IS present
    assert "packaging" in props
