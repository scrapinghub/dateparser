from datetime import datetime

from parameterized import param, parameterized

from dateparser.calendars.minguo import MinguoCalendar, _minguo_parser
from dateparser.conf import settings
from tests import BaseTestCase


class TestMinguoCalendar(BaseTestCase):
    @parameterized.expand(
        [
            param("101/05/25", datetime(2012, 5, 25)),
            param("民國101年5月25日 08:36", datetime(2012, 5, 25, 8, 36)),
            param("99.12.31", datetime(2010, 12, 31)),
            param("5/1/2", datetime(1916, 1, 2)),
            param("101/2/29", datetime(2012, 2, 29)),
        ]
    )
    def test_parse(self, date_string: str, expected: datetime) -> None:
        date_data = MinguoCalendar(date_string).get_date()
        assert date_data is not None
        self.assertEqual(date_data.date_obj, expected)
        self.assertEqual(date_data.period, "day")

    @parameterized.expand(
        [
            param("101-02", datetime(2012, 2, 29), "month"),
            param("110", datetime(2021, 3, 31), "year"),
        ]
    )
    def test_partial(self, date_string: str, expected: datetime, period: str) -> None:
        current = settings.replace(RELATIVE_BASE=datetime(2026, 3, 31))
        self.assertEqual(_minguo_parser.parse(date_string, current), (expected, period))

    @parameterized.expand(
        [
            param("2012/05/25"),
            param("0/1/1"),
            param("102/2/29"),
            param("101/05/25 08:36 92694"),
        ]
    )
    def test_invalid(self, date_string: str) -> None:
        self.assertIsNone(MinguoCalendar(date_string).get_date())
