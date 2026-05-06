from mediavocab.models import external_ids as eid


def test_known_keys_are_lowercase_strings():
    for k in eid.ALL_KNOWN_KEYS:
        assert isinstance(k, str)
        assert k == k.lower()
        assert " " not in k


def test_known_keys_unique():
    assert len(eid.ALL_KNOWN_KEYS) == len(set(eid.ALL_KNOWN_KEYS))


def test_a_few_well_known():
    assert eid.IMDB == "imdb"
    assert eid.MUSICBRAINZ_RECORDING == "musicbrainz_recording"
    assert eid.HOME_ASSISTANT == "home_assistant"
