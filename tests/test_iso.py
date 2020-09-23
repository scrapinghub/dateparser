from datetime import datetime, MAXYEAR, MINYEAR
from unittest import TestCase

from parameterized import parameterized, param

from dateparser import parse
from dateparser.date import DateDataParser, _parse_iso_date


class TestISOParser(TestCase):

    @parameterized.expand([
        param("2017-06-22", True),
        param("201706-22", False),
        param("2017-0622", False),
        param("20170622", True),
        param("+000002017-06-22", True),
        param("+00000201706-22", False),
        param("+000002017-0622", False),
        param("+0000020170622", True),
    ])
    def test_day_formats(self, date_string, is_valid):
        actual = _parse_iso_date(date_string)
        expected = (
            None if not is_valid
            else {
                "date_obj": datetime(2017, 6, 22),
                "period": "day",
                "locale": None,
            }
        )
        self.assertEqual(actual, expected)

    @parameterized.expand([
        # datetime year limits
        param(
            f"{MAXYEAR+1}-01-01",
            None,
        ),
        param(
            f"{MAXYEAR}-12-31",
            {"date_obj": datetime(MAXYEAR, 12, 31), "period": "day"},
        ),
        param(
            f"{MINYEAR:04}-01-01",
            {"date_obj": datetime(MINYEAR, 1, 1), "period": "day"},
        ),
        param(
            f"{MINYEAR-1:04}-12-31",
            None,
        ),

        # month limits
        param(
            "2020-00-01",
            None,
        ),
        param(
            "2020-01-01",
            {"date_obj": datetime(2020, 1, 1), "period": "day"},
        ),
        param(
            "2020-12-01",
            {"date_obj": datetime(2020, 12, 1), "period": "day"},
        ),
        param(
            "2020-13-01",
            None,
        ),

        # day limits
        param(
            "2020-01-00",
            None,
        ),
        param(
            "2020-01-01",
            {"date_obj": datetime(2020, 1, 1), "period": "day"},
        ),
        param(
            "2020-01-31",
            {"date_obj": datetime(2020, 1, 31), "period": "day"},
        ),
        param(
            "2020-01-32",
            None,
        ),
        param(
            "2020-04-30",
            {"date_obj": datetime(2020, 4, 30), "period": "day"},
        ),
        param(
            "2020-04-31",  # 30-day month
            None,
        ),
        param(
            "2020-02-29",
            {"date_obj": datetime(2020, 2, 29), "period": "day"},
        ),
        param(
            "2020-02-30",  # February on leap year
            None,
        ),
        param(
            "2021-02-28",
            {"date_obj": datetime(2021, 2, 28), "period": "day"},
        ),
        param(
            "2021-02-29",  # February on non-leap year
            None,
        ),
    ])
    def test_limits(self, date_string, result):
        actual = _parse_iso_date(date_string)
        expected = None if result is None else {**result, "locale": None}
        self.assertEqual(actual, expected)

    def test_fallback_for_parse(self):
        # TODO: Make sure that without the ISO parser it would not work
        actual = parse("2017-06-22", languages=["it"])
        expected = datetime(2017, 6, 22)
        self.assertEqual(actual, expected)

    def test_fallback_for_datedataparser(self):
        # TODO: Make sure that without the ISO parser it would not work
        actual = DateDataParser(languages=["it"]).get_date_data("2017-06-22")
        expected = {'date_obj': datetime(2017, 6, 22), 'period': "day", 'locale': None}
        self.assertEqual(actual, expected)
