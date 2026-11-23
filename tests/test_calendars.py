from datetime import datetime

from dateparser.calendars import CalendarBase, non_gregorian_parser
from dateparser.calendars.minguo import MinguoCalendar
from dateparser.conf import Settings
from dateparser.date import DateDataParser


def test_to_latin_defaults() -> None:
    assert non_gregorian_parser.to_latin(" 1 x ") == "1 x"


def test_get_date_with_partless_parser() -> None:
    class _Parser:
        @classmethod
        def parse(
            cls, datestring: str, settings: Settings
        ) -> tuple[datetime, str | None]:
            return datetime(2020, 1, 2), "day"

    class _Calendar(CalendarBase):
        parser = _Parser()

    date_data = _Calendar("foo").get_date()
    assert date_data is not None
    assert (date_data.date_obj, date_data.period, date_data.parts) == (
        datetime(2020, 1, 2),
        "day",
        (),
    )


def test_leap_second_is_flagged_on_calendar_date_data() -> None:
    date_data = MinguoCalendar("105-12-31 23:59:60").get_date()
    assert date_data is not None
    assert date_data.date_obj == datetime(2016, 12, 31, 23, 59, 59)
    assert date_data.leap_second == 60


def test_leap_second_flag_does_not_leak_from_a_prior_gregorian_parse() -> None:
    # Calendars bypass `_DateLocaleParser`'s resets and call `_parser.parse()`
    # directly, so a flag left set by a prior, unrelated leap-second parse
    # must not leak in and reject a calendar date that never touched
    # `strptime()` with a clamped second.
    DateDataParser().get_date_data("December 31st, 2016 23:59:60 UTC")

    date_data = MinguoCalendar("105-01-01").get_date()
    assert date_data is not None
    assert date_data.date_obj == datetime(2016, 1, 1)
    assert date_data.leap_second is None


def test_leap_second_flag_does_not_leak_into_a_parser_that_never_touches_it() -> None:
    # Not every calendar parser routes through `_parser._parse_with_parts`
    # (e.g. the French Republican calendar does not), so `CalendarBase`
    # itself, not just `_parser`, must reset the flag before delegating.
    class _Parser:
        @classmethod
        def _parse_with_parts(
            cls, datestring: str, settings: Settings
        ) -> tuple[datetime, str | None, tuple[str, ...]]:
            return datetime(2020, 1, 2), "day", ()

    class _Calendar(CalendarBase):
        parser = _Parser()

    DateDataParser().get_date_data("December 31st, 2016 23:59:60 UTC")

    date_data = _Calendar("foo").get_date()
    assert date_data is not None
    assert date_data.leap_second is None
