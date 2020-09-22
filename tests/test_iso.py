from datetime import datetime, MAXYEAR, MINYEAR
from unittest import TestCase

from parameterized import parameterized, param

from dateparser import parse
from dateparser.date import DateDataParser, _parse_iso_date


class TestISOParser(TestCase):


    @parameterized.expand([
        # formats
        param(
            "2017-06-22",
            {"date_obj": datetime(2017, 6, 22), "period": "day"},
        ),
        param(
            "+000002017-06-22",
            {"date_obj": datetime(2017, 6, 22), "period": "day"},
        ),

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
            "2020-04-31",
            None,
        ),
        param(
            "2020-02-29",
            {"date_obj": datetime(2020, 2, 29), "period": "day"},
        ),
        param(
            "2020-02-30",
            None,
        ),
        param(
            "2021-02-28",
            {"date_obj": datetime(2021, 2, 28), "period": "day"},
        ),
        param(
            "2021-02-29",
            None,
        ),
    ])
    def test_parser(self, date_string, result):
        actual = _parse_iso_date(date_string)
        expected = None if result is None else {**result, "locale": None}
        self.assertEqual(actual, expected)

    def test_fallback_for_parse(self):
        actual = parse("2017-06-22", languages=["it"])
        expected = datetime(2017, 6, 22)
        self.assertEqual(actual, expected)

    def test_fallback_for_datedataparser(self):
        actual = DateDataParser(languages=["it"]).get_date_data("2017-06-22")
        expected = {'date_obj': datetime(2017, 6, 22), 'period': "day", 'locale': None}
        self.assertEqual(actual, expected)
