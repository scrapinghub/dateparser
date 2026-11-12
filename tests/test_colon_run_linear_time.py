import itertools

import pytest
import regex

from dateparser.date import sanitize_date
from tests.linear_time import assert_fast

SETUP = """
from dateparser.date import sanitize_date
"""


@pytest.mark.parametrize(
    "date_string",
    [
        "'a' + ':' * 80_000 + 'b'",
        "':' * 80_000 + 'b'",
        "'12:30' + ':' * 80_000 + '1'",
        "'a' + ':' * 40_000 + ' ' + ':' * 40_000 + 'b'",
    ],
)
def test_long_colon_run_does_not_take_quadratic_time(date_string: str) -> None:
    assert_fast(SETUP, [f"sanitize_date({date_string})"])


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("2019:", "2019"),
        ("2019:::", "2019"),
        ("12:30:", "12:30"),
        ("12:30::::", "12:30"),
        (":::2019", ":::2019"),
        (":::2019:::", ":::2019"),
        (": 12:30 ::", ": 12:30"),
        ("a::b::", "a::b"),
        ("a::b", "a::b"),
        ("  2019::: ", "2019"),
        ("2019 :: ", "2019 ::"),
        ("2019:::" + ":" * 1000, "2019"),
    ],
)
def test_trailing_colons_are_stripped(date_string: str, expected: str) -> None:
    assert sanitize_date(date_string) == expected


SETUP_DEPRECATED = """
import warnings
warnings.simplefilter("ignore")
from dateparser.date import RE_TRIM_COLONS
"""


@pytest.mark.parametrize(
    "date_string",
    [
        "'a' + ':' * 80_000 + 'b'",
        "':' * 40_000 + '\\nx'",
        "'12:30' + ':' * 40_000 + '\\n1'",
    ],
)
def test_deprecated_re_trim_colons_does_not_take_quadratic_time(
    date_string: str,
) -> None:
    assert_fast(
        SETUP_DEPRECATED,
        [
            f"RE_TRIM_COLONS.sub(r'\\1', {date_string})",
            f"RE_TRIM_COLONS.search({date_string})",
        ],
    )


# What RE_TRIM_COLONS was before it was deprecated.
_FORMER_RE_TRIM_COLONS = r"(\S.*?):*$"


def _deprecated_re_trim_colons() -> "regex.Pattern[str]":
    with pytest.warns(FutureWarning, match="RE_TRIM_COLONS"):
        from dateparser.date import RE_TRIM_COLONS  # noqa: PLC0415
    pattern: regex.Pattern[str] = RE_TRIM_COLONS
    return pattern


def _what_a_pattern_finds(
    pattern: "regex.Pattern[str]", text: str
) -> tuple[object, ...]:
    found = pattern.search(text)
    return (
        None if found is None else (found.span(), found.span(1), found.group(1)),
        pattern.sub(r"\1", text),
        pattern.sub(r"[\1]", text),
        pattern.subn(r"<\1>", text),
        pattern.findall(text),
    )


@pytest.mark.parametrize(
    ("date_string", "expected"),
    [
        ("2019::", "2019"),
        ("  2019 :: ", "  2019 :: "),
        (":::", ":"),
        ("::: ", "::: "),
        ("a:b:c:", "a:b:c"),
        ("a::\nb::", "a::\nb"),
        ("a::\n", "a\n"),
        ("a\n::", "a\n:"),
        ("", ""),
    ],
)
def test_deprecated_re_trim_colons_still_trims_colons(
    date_string: str, expected: str
) -> None:
    assert _deprecated_re_trim_colons().sub(r"\1", date_string) == expected
    assert regex.sub(_FORMER_RE_TRIM_COLONS, r"\1", date_string) == expected


def test_deprecated_re_trim_colons_finds_what_it_found() -> None:
    """Test that every string of up to 7 characters of the kinds that the
    pattern treats differently (a colon, a space, a line break, any other
    character) gives the same matches, spans and groups as the former pattern."""
    former = regex.compile(_FORMER_RE_TRIM_COLONS)
    pattern = _deprecated_re_trim_colons()
    for length in range(8):
        for characters in itertools.product("a: \n", repeat=length):
            text = "".join(characters)
            assert _what_a_pattern_finds(pattern, text) == _what_a_pattern_finds(
                former, text
            ), repr(text)


# Other characters that \s matches, which the patterns treat as whitespace.
_OTHER_WHITESPACE = "\r\t\x0b\x0c\x85\xa0\u2028"


def test_deprecated_re_trim_colons_finds_what_it_found_other_whitespace() -> None:
    """Test that every string of up to 4 characters of a colon, a letter, a space,
    a line break and other whitespace gives the same matches, spans and groups as
    the former pattern."""
    former = regex.compile(_FORMER_RE_TRIM_COLONS)
    pattern = _deprecated_re_trim_colons()
    alphabet = "a: \n" + _OTHER_WHITESPACE
    for length in range(5):
        for characters in itertools.product(alphabet, repeat=length):
            text = "".join(characters)
            assert _what_a_pattern_finds(pattern, text) == _what_a_pattern_finds(
                former, text
            ), repr(text)
