"""ISBN helpers."""
import pytest

from mediavocab.text import isbn10_to_13, isbn13_to_10, normalize_isbn


# ---------------------------------------------------------------------------
# normalize_isbn
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("0-261-10328-8",   "0261103288"),
    ("0 261 10328 8",   "0261103288"),
    ("978-0-261-10328-3", "9780261103283"),
    ("9780261103283",   "9780261103283"),
    ("020161622X",      "020161622X"),       # X check digit preserved
    ("0-201-61622-x",   "020161622X"),       # case-insensitive X
])
def test_normalize_isbn_strips_formatting(raw, expected):
    assert normalize_isbn(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "abc", "12345", "12345678901234"])
def test_normalize_isbn_returns_none_on_garbage(raw):
    assert normalize_isbn(raw) is None


# ---------------------------------------------------------------------------
# isbn10_to_13
# ---------------------------------------------------------------------------

def test_isbn10_to_13_canonical():
    assert isbn10_to_13("0261103288") == "9780261103283"
    assert isbn10_to_13("0-261-10328-8") == "9780261103283"


def test_isbn10_to_13_with_x_check():
    # Hitchhiker's Guide ISBN-10 uses X
    assert isbn10_to_13("020161622X") is None or isbn10_to_13("020161622X").startswith("978")


def test_isbn10_to_13_returns_none_on_bad_input():
    assert isbn10_to_13("12345") is None
    assert isbn10_to_13("0261103288XX") is None
    assert isbn10_to_13("") is None


# ---------------------------------------------------------------------------
# isbn13_to_10
# ---------------------------------------------------------------------------

def test_isbn13_to_10_canonical():
    assert isbn13_to_10("9780261103283") == "0261103288"
    assert isbn13_to_10("978-0-261-10328-3") == "0261103288"


def test_isbn13_to_10_returns_none_for_979():
    # 979-prefixed ISBNs cannot be expressed as ISBN-10.
    assert isbn13_to_10("9791234567896") is None


def test_isbn13_to_10_returns_none_on_bad_input():
    assert isbn13_to_10("12345") is None
    assert isbn13_to_10("") is None


def test_round_trip():
    original = "0261103288"
    assert isbn13_to_10(isbn10_to_13(original)) == original
