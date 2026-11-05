import pytest

from dateparser.freshness_date_parser import PATTERN
from tests.linear_time import assert_fast

SETUP = """
from dateparser import date
from dateparser.conf import settings
from dateparser.freshness_date_parser import PATTERN
from dateparser.languages import default_loader
from dateparser.languages.dictionary import Dictionary

def split_relative(shortname, text):
    dictionary = Dictionary(default_loader.get_locale(shortname).info, settings)
    dictionary._get_split_relative_regex_cache().split(text)
"""


@pytest.mark.parametrize(
    "date_string",
    ["'9' * 60_000 + '.'", "'9' * 30_000 + '. ' + '9' * 30_000"],
)
def test_sanitize_long_digit_run_does_not_take_quadratic_time(date_string: str) -> None:
    assert_fast(SETUP, [f"date.sanitize_date({date_string})"])


@pytest.mark.parametrize("whitespace", [" ", "\t", "\n", "　"])
@pytest.mark.parametrize("prefix", ["", "-", "+"])
def test_pattern_whitespace_run_does_not_take_quadratic_time(
    prefix: str, whitespace: str
) -> None:
    text = f"{prefix!r} + {whitespace!r} * 15_000"
    assert_fast(SETUP, [f"PATTERN.findall({text})", f"PATTERN.sub('', {text} + 'x')"])


def test_pattern_still_matches_signed_quantities() -> None:
    assert PATTERN.findall("in 5 day, - 3 hour, +2 week") == [
        ("5", "day"),
        ("- 3", "hour"),
        ("+2", "week"),
    ]


@pytest.mark.parametrize("shortname", ["ja", "zh", "zh-Hans", "zh-Hant", "yue"])
def test_split_relative_digit_run_does_not_take_quadratic_time(
    shortname: str,
) -> None:
    assert_fast(
        SETUP,
        [
            f"split_relative({shortname!r}, '9' * 12_000)",
            f"split_relative({shortname!r}, '9' * 12_000 + 'x')",
        ],
    )
