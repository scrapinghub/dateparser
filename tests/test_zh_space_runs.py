"""Chinese dates followed by long runs of spaces are simplified in linear time."""

from time import process_time

import pytest

from dateparser.conf import settings
from dateparser.languages import default_loader


@pytest.mark.parametrize("shortname", ["zh", "zh-Hans", "zh-Hant"])
def test_long_run_of_spaces_after_a_date(shortname: str) -> None:
    locale = default_loader.get_locale(shortname)
    date_string = "1年1月1" + " " * 20_000
    start = process_time()
    result = locale._simplify(date_string, settings=settings)
    assert process_time() - start < 0.3
    assert result == "1-1-1"


@pytest.mark.parametrize(
    ("shortname", "date_string", "expected"),
    [
        ("zh", "1年1月1 2点3", "1-1-1 2:3"),
        ("zh", "1年1月1日2点3", "1-1-1 2:3"),
        ("zh", "1年1月1日 2:3", "1-1-1 2:3"),
        ("zh-Hans", "1年1月1  2点3", "1-1-1 2:3"),
        ("zh-Hans", "1年1月1日 2点3", "1-1-1 2:3"),
        ("zh-Hant", "1年1月1 2點3", "1-1-1 2:3"),
        ("zh-Hant", "1年1月1日 2點3", "1-1-1 2:3"),
    ],
)
def test_time_after_a_date_with_or_without_the_day_character(
    shortname: str, date_string: str, expected: str
) -> None:
    locale = default_loader.get_locale(shortname)
    assert locale._simplify(date_string, settings=settings) == expected
