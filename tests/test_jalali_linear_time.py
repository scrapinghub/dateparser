import pytest

pytest.importorskip("convertdate")

from tests.linear_time import assert_fast

SETUP = """
from dateparser.calendars.jalali import JalaliCalendar
from dateparser.calendars.jalali_parser import jalali_parser
"""

# "۱۳ فروردین ۱۳۹۰", a valid date, written with escapes to keep the statements ASCII.
DATE = "'\\u06f1\\u06f3 \\u0641\\u0631\\u0648\\u0631\\u062f\\u06cc\\u0646 \\u06f1\\u06f3\\u06f9\\u06f0'"


@pytest.mark.parametrize(
    "date_string",
    [
        "' ' * 80_000 + 'x'",
        "'x' + ' ' * 80_000",
        "'\\t\\n' * 40_000 + 'x'",
        "'\\u00a0' * 80_000 + 'x'",
        "'12' + ' ' * 80_000 + 'x'",
        "' ' * 80_000 + '\\u0648x'",
        f"{DATE} + ' ' * 80_000",
    ],
)
def test_long_whitespace_run_does_not_take_quadratic_time(date_string: str) -> None:
    assert_fast(
        SETUP,
        [
            f"jalali_parser.to_latin({date_string})",
            f"JalaliCalendar({date_string}).get_date()",
        ],
    )
