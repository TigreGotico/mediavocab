"""Tests for `mediavocab.models.license` free-function predicates (spec §7.2)."""
import pytest

from mediavocab.models.license import (
    License,
    allows_commercial,
    allows_derivatives,
    allows_share_alike,
    is_open,
    is_public_domain,
    requires_attribution,
)


# ---------------------------------------------------------------------------
# Creative Commons family
# ---------------------------------------------------------------------------

class TestCreativeCommons:
    def test_cc_by(self):
        s = "CC-BY-4.0"
        assert is_open(s)
        assert not is_public_domain(s)
        assert requires_attribution(s)
        assert allows_commercial(s)
        assert allows_derivatives(s)
        assert not allows_share_alike(s)

    def test_cc_by_sa(self):
        s = "CC-BY-SA-4.0"
        assert is_open(s)
        assert allows_share_alike(s)
        assert allows_commercial(s)

    def test_cc_by_nc(self):
        s = "CC-BY-NC-4.0"
        assert is_open(s)
        assert not allows_commercial(s)
        assert allows_derivatives(s)

    def test_cc_by_nd(self):
        s = "CC-BY-ND-4.0"
        assert is_open(s)
        assert allows_commercial(s)
        assert not allows_derivatives(s)

    def test_cc_by_nc_nd(self):
        s = "CC-BY-NC-ND-4.0"
        assert is_open(s)
        assert not allows_commercial(s)
        assert not allows_derivatives(s)
        assert not allows_share_alike(s)


# ---------------------------------------------------------------------------
# Public domain family
# ---------------------------------------------------------------------------

class TestPublicDomain:
    @pytest.mark.parametrize("s", ["CC0-1.0", "public_domain", "PDM"])
    def test_pd_open_and_attribution_free(self, s):
        assert is_open(s)
        assert is_public_domain(s)
        assert not requires_attribution(s)
        assert allows_commercial(s)
        assert allows_derivatives(s)


# ---------------------------------------------------------------------------
# Open-source permissive / copyleft
# ---------------------------------------------------------------------------

class TestOpenSource:
    @pytest.mark.parametrize("s", ["MIT", "BSD-3-Clause", "Apache-2.0", "MPL-2.0", "ISC"])
    def test_permissive_is_open(self, s):
        assert is_open(s), f"{s!r} should be open"
        assert not allows_share_alike(s)
        assert allows_commercial(s)
        assert allows_derivatives(s)

    @pytest.mark.parametrize("s", ["GPL-3.0-only", "LGPL-3.0-only", "AGPL-3.0-only"])
    def test_copyleft_is_share_alike(self, s):
        assert is_open(s)
        assert allows_share_alike(s)
        assert allows_commercial(s)


# ---------------------------------------------------------------------------
# Restrictive / unknown — conservative defaults
# ---------------------------------------------------------------------------

class TestRestrictive:
    @pytest.mark.parametrize("s", ["all_rights_reserved", "ARR", "proprietary", ""])
    def test_arr_is_closed(self, s):
        assert not is_open(s)
        assert not is_public_domain(s)
        assert not allows_commercial(s)
        assert not allows_derivatives(s)
        assert not allows_share_alike(s)

    def test_arr_conservatively_requires_attribution(self):
        """Unknown / restrictive defaults to most-restrictive (spec §7.2)."""
        assert requires_attribution("")
        assert requires_attribution("all_rights_reserved")
        assert requires_attribution("Some-Unknown-Licence-9.9")

    def test_unknown_is_closed(self):
        assert not is_open("Some-Unknown-Licence-9.9")
        assert not allows_commercial("Some-Unknown-Licence-9.9")


# ---------------------------------------------------------------------------
# Round-trip through the typed view
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_from_spdx_preserves_identifier(self):
        lic = License.from_spdx("CC-BY-SA-4.0")
        assert lic.identifier == "CC-BY-SA-4.0"

    def test_unknown_preserves_string(self):
        lic = License.from_spdx("Some-Custom-Licence")
        assert lic.identifier == "Some-Custom-Licence"

    def test_empty_falls_back_to_arr(self):
        lic = License.from_spdx("")
        assert lic.identifier == "all_rights_reserved"
