from datetime import datetime

from dateparser.calendars import CalendarBase, non_gregorian_parser
from dateparser.conf import Settings


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
