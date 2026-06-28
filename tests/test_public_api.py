"""Public-API surface snapshot — freezes the 1.0 contract.

Every breaking change this package can inflict on a consumer is a *removal* or
a *rename*: a deleted export, a dropped enum member, a renamed field. Consumers
discover those at import time, repo by repo, often months later.

This test freezes the public surface — exported names, enum members (name +
string value), and model field names — and asserts the frozen 1.0 set is still
a subset of what's exported now. So:

  * removing or renaming anything frozen here -> this test FAILS
  * adding new things -> passes (additions are non-breaking)

A failure means a breaking change. If it is intended (a major bump), update the
frozen sets deliberately and note it in the migration guide — do not edit them
to silence a red test.
"""
import mediavocab as mv
from mediavocab import (
    MediaType, RelationRole, WorkRelationKind, ReleaseRelationKind, ContentForm,
    ProgrammeFormat, StreamMode, EntityKind, OrganisationKind, VariantKind,
    PlaybackType, ReleaseStatus, MembershipKind, TemporalState, CreditSection,
    AccessibilityKind, SignalsRole,
    Work, Release, Entity, EntityRef, ExternalIds, Signals, Credit,
)


# ---------------------------------------------------------------------------
# Frozen 1.0 surface
# ---------------------------------------------------------------------------

FROZEN_EXPORTS = {
    "AccessibilityKind", "AccessibilityTrack", "Appearance", "AvailabilityWindow",
    "COUNTRY_SLOT_FOR", "Chapter", "ClassificationResult", "Conflict", "ContentForm",
    "Credit", "CreditSection", "DEFAULT_STRATEGY", "Entity", "EntityKind", "EntityRef",
    "ExternalIds", "IdentityConflict", "KNOWN_EXTERNAL_IDS", "KNOWN_GENRES", "License",
    "LocalizedTitle", "MEDIA_TYPE_TO_PLAYBACK_TYPE", "MediaType", "Membership",
    "MembershipKind", "MergeStrategy", "MetadataProvider", "OrganisationKind",
    "PIPELINE_SENTINELS", "PlaybackType", "ProgrammeFormat", "ProviderMatch",
    "RelationRole", "Release", "ReleasePackaging", "ReleaseRelation",
    "ReleaseRelationKind", "ReleaseStatus", "ResolutionConflict", "SPEC_VERSION",
    "SignalConflict", "Signals", "SignalsRole", "Stream", "StreamMode",
    "TemporalState", "VariantKind", "Work", "WorkRelation", "WorkRelationKind",
    "__version__", "classify_video", "extract_tags", "infer_playback_type",
    "compare_signals", "merge_signals", "match_quality", "signal_hash",
}

FROZEN_ENUMS = {
    "MediaType": {('AUDIOBOOK', 'audiobook'), ('AUDIO_DRAMA', 'audio_drama'), ('BOOK', 'book'), ('COMIC', 'comic'), ('CONTROL', 'control'), ('EPISODIC_SERIES', 'episodic_series'), ('GAME', 'game'), ('GENERIC', 'generic'), ('INTERACTIVE_FICTION', 'interactive_fiction'), ('MOVIE', 'movie'), ('MUSIC', 'music'), ('MUSIC_VIDEO', 'music_video'), ('NOT_MEDIA', 'not_media'), ('PLAYLIST', 'playlist'), ('PODCAST', 'podcast'), ('PROCEDURAL_AMBIENT', 'procedural_ambient'), ('RADIO', 'radio'), ('SHORT_FILM', 'short_film'), ('SOUND_EFFECT', 'sound_effect'), ('TV', 'tv')},
    "RelationRole": {('ACTOR', 'actor'), ('ARRANGER', 'arranger'), ('AUTHOR', 'author'), ('CINEMATOGRAPHER', 'cinematographer'), ('COMPOSER', 'composer'), ('CONDUCTOR', 'conductor'), ('CREATOR', 'creator'), ('CURATOR', 'curator'), ('DEVELOPER', 'developer'), ('DIRECTOR', 'director'), ('DISTRIBUTOR', 'distributor'), ('DJ', 'dj'), ('EDITOR', 'editor'), ('FEATURING', 'featuring'), ('GUEST', 'guest'), ('HOST', 'host'), ('ILLUSTRATOR', 'illustrator'), ('LABEL', 'label'), ('LYRICIST', 'lyricist'), ('NARRATOR', 'narrator'), ('OTHER', 'other'), ('PERFORMER', 'performer'), ('PORTER', 'porter'), ('PRODUCER', 'producer'), ('PUBLISHER', 'publisher'), ('REMIXER', 'remixer'), ('SCREENWRITER', 'screenwriter'), ('TRANSLATOR', 'translator')},
    "WorkRelationKind": {('ADAPTED_FROM', 'adapted_from'), ('BONUS_FOR', 'bonus_for'), ('CLIP_OF', 'clip_of'), ('COVERS', 'covers'), ('DERIVED_FROM', 'derived_from'), ('DLC_FOR', 'dlc_for'), ('EXPANSION_OF', 'expansion_of'), ('FANEDIT_OF', 'fanedit_of'), ('LIVE_VERSION', 'live_version'), ('MIX_OF', 'mix_of'), ('PART_OF', 'part_of'), ('PREQUEL_TO', 'prequel_to'), ('REACTION_TO', 'reaction_to'), ('REMIX_OF', 'remix_of'), ('SAMPLES', 'samples'), ('SEQUEL_TO', 'sequel_to'), ('SOUNDTRACK_FOR', 'soundtrack_for'), ('TRAILER_FOR', 'trailer_for')},
    "ReleaseRelationKind": {('DERIVED_FROM', 'derived_from'), ('MIRROR_OF', 'mirror_of'), ('PORT_OF', 'port_of'), ('REISSUE_OF', 'reissue_of'), ('REMASTER_OF', 'remaster_of'), ('SUPERSEDES', 'supersedes')},
    "ContentForm": {('BEHIND_SCENES', 'behind_scenes'), ('EXCERPT', 'excerpt'), ('OTHER', 'other'), ('PRIMARY', 'primary'), ('REACTION', 'reaction'), ('SOCIAL_CLIP', 'social_clip'), ('SUPPLEMENT', 'supplement'), ('TEASER', 'teaser'), ('TRAILER', 'trailer')},
    "ProgrammeFormat": {('CONCERT', 'concert'), ('DOCUMENTARY', 'documentary'), ('NEWS', 'news'), ('OTHER', 'other'), ('QUIZ', 'quiz'), ('REALITY', 'reality'), ('SPORTS', 'sports'), ('STAND_UP', 'stand_up'), ('TALK_SHOW', 'talk_show')},
    "StreamMode": {('CONTINUOUS', 'continuous'), ('LIVE', 'live'), ('ON_DEMAND', 'on_demand')},
    "EntityKind": {('DEVICE', 'device'), ('GROUP', 'group'), ('ORGANISATION', 'organisation'), ('OTHER', 'other'), ('PERSON', 'person'), ('SERIES', 'series')},
    "OrganisationKind": {('BROADCASTER', 'broadcaster'), ('DEVELOPER', 'developer'), ('DISTRIBUTOR', 'distributor'), ('LABEL', 'label'), ('NETWORK', 'network'), ('OTHER', 'other'), ('PUBLISHER', 'publisher'), ('STREAMING_SERVICE', 'streaming_service'), ('STUDIO', 'studio')},
    "VariantKind": {('COLORIZED', 'colorized'), ('COMPILATION', 'compilation'), ('DIRECTORS', 'directors'), ('EXTENDED', 'extended'), ('FANEDIT', 'fanedit'), ('MOVIE_TO_TV', 'movie_to_tv'), ('OTHER', 'other'), ('PRESERVATION', 'preservation'), ('REMASTERED', 'remastered'), ('THEATRICAL', 'theatrical'), ('TV_TO_MOVIE', 'tv_to_movie'), ('UPSCALED', 'upscaled')},
    "PlaybackType": {('AUDIO', 'audio'), ('INTERACTIVE', 'interactive'), ('PAGED', 'paged'), ('UNKNOWN', 'unknown'), ('VIDEO', 'video')},
    "ReleaseStatus": {('ANNOUNCED', 'announced'), ('CANCELLED', 'cancelled'), ('IN_PRODUCTION', 'in_production'), ('RELEASED', 'released'), ('UNKNOWN', 'unknown'), ('WITHDRAWN', 'withdrawn')},
    "MembershipKind": {('MEMBER', 'member'), ('SESSION', 'session'), ('TOURING', 'touring')},
    "TemporalState": {('ACTIVE', 'active'), ('ENDED', 'ended'), ('INACTIVE_GROUP', 'inactive_group')},
    "CreditSection": {('GUEST', 'guest'), ('PRINCIPAL', 'principal'), ('STAFF', 'staff')},
    "AccessibilityKind": {('AUDIO_DESCRIPTION', 'audio_description'), ('CAPTIONS', 'captions'), ('LYRICS', 'lyrics'), ('SIGN_LANGUAGE', 'sign_language'), ('SUBTITLES', 'subtitles'), ('TRANSCRIPT', 'transcript')},
    "SignalsRole": {('OBSERVATION', 'observation'), ('QUERY', 'query'), ('RESULT', 'result')},
}

FROZEN_MODEL_FIELDS = {
    "Work": {'aka', 'broadcaster_country', 'content_form', 'content_genres', 'credits', 'edition', 'episode', 'episode_orderings', 'external_ids', 'extra', 'language', 'localized_titles', 'media_type', 'original_languages', 'production_country', 'programme_format', 'publication_country', 'relations', 'release_status', 'runtime', 'season', 'series_title', 'source_format', 'title', 'tracklist', 'variant_kind', 'year'},
    "Release": {'accessibility', 'aspect_ratio', 'audio_channels', 'audio_language', 'audio_present', 'availability_windows', 'bitrate', 'chapters', 'codec', 'color', 'container', 'contents', 'distributor', 'edition', 'external_ids', 'extra', 'frame_rate', 'hdr', 'image', 'label', 'license', 'match_confidence', 'packaging', 'platform', 'region', 'region_locked', 'regions_available', 'relations', 'release_date', 'release_status', 'resolution', 'sample_rate', 'stream_mode', 'subtitle_languages', 'uri', 'work'},
    "Entity": {'aliases', 'birth_year', 'death_year', 'disbanded', 'external_ids', 'extra', 'formed', 'kind', 'memberships', 'name', 'org_kind', 'part_of', 'years_active'},
    "EntityRef": {'external_ids', 'kind', 'localized_names', 'name'},
    "ExternalIds": {'anidb_id', 'anilist_character_id', 'anilist_id', 'anilist_staff_id', 'anilist_studio_id', 'apple_podcast_id', 'audible_asin', 'audiodb_album_id', 'audiodb_artist_id', 'audiodb_track_id', 'bandcamp_band_id', 'bluray_com_id', 'derived_from_imdb', 'discogs_artist', 'discogs_release', 'dvdcompare_id', 'extra', 'fanedit_id', 'goodreads', 'google_books_id', 'igdb_id', 'iheart_artist_id', 'iheart_episode_id', 'iheart_playlist_id', 'iheart_podcast_id', 'iheart_station_id', 'iheart_track_id', 'imdb', 'imdb_person', 'isbn_10', 'isbn_13', 'librivox_id', 'listen_notes_id', 'mal_character_id', 'mal_id', 'mal_person_id', 'mal_studio_id', 'metal_archives_artist', 'metal_archives_band', 'metal_archives_label', 'metal_archives_release', 'metal_archives_song', 'musicbrainz_artist', 'musicbrainz_label', 'musicbrainz_recording', 'musicbrainz_release', 'musicbrainz_release_group', 'musicbrainz_work', 'olid', 'opencritic_id', 'podcast_index_id', 'rawg_id', 'soundcloud_user_id', 'tmdb_movie', 'tmdb_person', 'tmdb_tv', 'trakt_id', 'tvdb', 'tvmaze', 'wikidata', 'youtube_channel_id', 'youtube_music_artist_browse_id'},
    "Signals": {'artist', 'content_form', 'content_genres', 'country', 'edition', 'episode', 'fanedit_subtype', 'include_variants', 'language', 'medium', 'playback_type', 'region', 'role', 'runtime', 'season', 'source_format', 'title', 'variant_kind', 'year'},
    "Credit": {'entity', 'note', 'relation_role', 'role', 'section'},
}

_ENUMS = {E.__name__: E for E in [
    MediaType, RelationRole, WorkRelationKind, ReleaseRelationKind, ContentForm,
    ProgrammeFormat, StreamMode, EntityKind, OrganisationKind, VariantKind,
    PlaybackType, ReleaseStatus, MembershipKind, TemporalState, CreditSection,
    AccessibilityKind, SignalsRole,
]}
_MODELS = {M.__name__: M for M in [Work, Release, Entity, EntityRef, ExternalIds, Signals, Credit]}


def test_no_public_export_removed():
    current = set(mv.__all__)
    removed = FROZEN_EXPORTS - current
    assert not removed, f"public exports removed/renamed (breaking): {sorted(removed)}"


def test_exported_names_are_resolvable():
    for name in mv.__all__:
        assert hasattr(mv, name), f"{name} is in __all__ but not importable"


def test_no_enum_member_removed():
    for enum_name, frozen in FROZEN_ENUMS.items():
        current = {(m.name, m.value) for m in _ENUMS[enum_name]}
        removed = frozen - current
        assert not removed, (
            f"{enum_name} members removed/renamed (breaking): {sorted(removed)}")


def test_no_model_field_removed():
    for model_name, frozen in FROZEN_MODEL_FIELDS.items():
        current = set(_MODELS[model_name].model_fields)
        removed = frozen - current
        assert not removed, (
            f"{model_name} fields removed/renamed (breaking): {sorted(removed)}")
