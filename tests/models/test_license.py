"""Tests for ``License``."""
from mediavocab import License


def test_default_is_all_rights_reserved():
    lic = License.from_spdx("")
    assert lic.identifier == "all_rights_reserved"
    assert lic.commercial is False
    assert lic.derivatives is False
    assert lic.is_open() is False


def test_cc0_is_public_domain():
    lic = License.from_spdx("CC0-1.0")
    assert lic.is_public_domain is True
    assert lic.is_open() is True
    assert lic.attribution is False
    assert lic.commercial is True


def test_cc_by_sa_4_is_share_alike():
    lic = License.from_spdx("CC-BY-SA-4.0")
    assert lic.attribution is True
    assert lic.share_alike is True
    assert lic.commercial is True
    assert lic.derivatives is True
    assert lic.is_open() is True


def test_cc_by_nc_nd_is_most_restrictive_open():
    lic = License.from_spdx("CC-BY-NC-ND-4.0")
    assert lic.commercial is False
    assert lic.derivatives is False
    assert lic.share_alike is False
    assert lic.is_open() is True


def test_unknown_string_preserved_and_restricted():
    lic = License.from_spdx("Custom-EULA-2.1")
    assert lic.identifier == "Custom-EULA-2.1"
    assert lic.is_open() is False
    assert lic.commercial is False
