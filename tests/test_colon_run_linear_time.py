import pytest

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
