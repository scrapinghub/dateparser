from datetime import MAXYEAR, MINYEAR, datetime, timedelta, timezone
from typing import Any
from unittest import TestCase

from parameterized import param, parameterized

from dateparser import parse
from dateparser.conf import settings
from dateparser.date import DateDataParser


def _parse_iso_date(date_string: str) -> dict[str, Any] | None:
    date_data = DateDataParser(settings={"PARSERS": ["iso"]}).get_date_data(date_string)
    if date_data.date_obj is None:
        return None
    return {
        "date_obj": date_data.date_obj,
        "period": date_data.period,
        "locale": date_data.locale,
    }


class TestISOParser(TestCase):
    @parameterized.expand(
        [
            param("2017-06-22", True),
            param("201706-22", False),
            param("2017-0622", False),
            param("20170622", True),
            param("+000002017-06-22", True),
            param("+00000201706-22", False),
            param("+000002017-0622", False),
            param("+0000020170622", True),
        ]
    )
    def test_day_formats(self, date_string: str, is_valid: bool) -> None:
        actual = _parse_iso_date(date_string)
        expected = (
            None
            if not is_valid
            else {
                "date_obj": datetime(2017, 6, 22),
                "period": "day",
                "locale": None,
            }
        )
        self.assertEqual(actual, expected)

    @parameterized.expand(
        [
            param("2020-01-02 03:04:05.6789", True, 5, 678900),
            param("2020-01-02 03:04:05,6789", True, 5, 678900),
            param("2020-01-02 03:04:05.678", True, 5, 678000),
            param("2020-01-02 03:04:05,678", True, 5, 678000),
            param("2020-01-02 03:04:05.67", True, 5, 670000),
            param("2020-01-02 03:04:05,67", True, 5, 670000),
            param("2020-01-02 03:04:05.6", True, 5, 600000),
            param("2020-01-02 03:04:05,6", True, 5, 600000),
            param("2020-01-02 03:04:05", True, 5),
            param("2020-01-02 03:04", True),
            param("2020-01-02T03:04:05.6789", True, 5, 678900),
            param("2020-01-02T03:04:05,6789", True, 5, 678900),
            param("2020-01-02T03:04:05.678", True, 5, 678000),
            param("2020-01-02T03:04:05,678", True, 5, 678000),
            param("2020-01-02T03:04:05.67", True, 5, 670000),
            param("2020-01-02T03:04:05,67", True, 5, 670000),
            param("2020-01-02T03:04:05.6", True, 5, 600000),
            param("2020-01-02T03:04:05,6", True, 5, 600000),
            param("2020-01-02T03:04:05", True, 5),
            param("2020-01-02T03:04", True),
            param("20200102 030405.6789", False),
            param("20200102 030405,6789", False),
            param("20200102 030405.678", False),
            param("20200102 030405,678", False),
            param("20200102 030405.67", False),
            param("20200102 030405,67", False),
            param("20200102 030405.6", False),
            param("20200102 030405,6", False),
            param("20200102 030405", False),
            param("20200102 0304", False),
            param("20200102T030405.6789", True, 5, 678900),
            param("20200102T030405,6789", True, 5, 678900),
            param("20200102T030405.678", True, 5, 678000),
            param("20200102T030405,678", True, 5, 678000),
            param("20200102T030405.67", True, 5, 670000),
            param("20200102T030405,67", True, 5, 670000),
            param("20200102T030405.6", True, 5, 600000),
            param("20200102T030405,6", True, 5, 600000),
            param("20200102T030405", True, 5),
            param("20200102T0304", True),
            param("+000002020-01-02 03:04:05.6789", True, 5, 678900),
            param("+000002020-01-02 03:04:05,6789", True, 5, 678900),
            param("+000002020-01-02 03:04:05.678", True, 5, 678000),
            param("+000002020-01-02 03:04:05,678", True, 5, 678000),
            param("+000002020-01-02 03:04:05.67", True, 5, 670000),
            param("+000002020-01-02 03:04:05,67", True, 5, 670000),
            param("+000002020-01-02 03:04:05.6", True, 5, 600000),
            param("+000002020-01-02 03:04:05,6", True, 5, 600000),
            param("+000002020-01-02 03:04:05", True, 5),
            param("+000002020-01-02 03:04", True),
            param("+000002020-01-02T03:04:05.6789", True, 5, 678900),
            param("+000002020-01-02T03:04:05,6789", True, 5, 678900),
            param("+000002020-01-02T03:04:05.678", True, 5, 678000),
            param("+000002020-01-02T03:04:05,678", True, 5, 678000),
            param("+000002020-01-02T03:04:05.67", True, 5, 670000),
            param("+000002020-01-02T03:04:05,67", True, 5, 670000),
            param("+000002020-01-02T03:04:05.6", True, 5, 600000),
            param("+000002020-01-02T03:04:05,6", True, 5, 600000),
            param("+000002020-01-02T03:04:05", True, 5),
            param("+000002020-01-02T03:04", True),
            param("+0000020200102 030405.6789", False),
            param("+0000020200102 030405,6789", False),
            param("+0000020200102 030405.678", False),
            param("+0000020200102 030405,678", False),
            param("+0000020200102 030405.67", False),
            param("+0000020200102 030405,67", False),
            param("+0000020200102 030405.6", False),
            param("+0000020200102 030405,6", False),
            param("+0000020200102 030405", False),
            param("+0000020200102 0304", False),
            param("+0000020200102T030405.6789", True, 5, 678900),
            param("+0000020200102T030405,6789", True, 5, 678900),
            param("+0000020200102T030405.678", True, 5, 678000),
            param("+0000020200102T030405,678", True, 5, 678000),
            param("+0000020200102T030405.67", True, 5, 670000),
            param("+0000020200102T030405,67", True, 5, 670000),
            param("+0000020200102T030405.6", True, 5, 600000),
            param("+0000020200102T030405,6", True, 5, 600000),
            param("+0000020200102T030405", True, 5),
            param("+0000020200102T0304", True),
        ]
    )
    def test_date_time_formats(
        self, date_string: str, is_valid: bool, seconds: int = 0, microseconds: int = 0
    ) -> None:
        actual = _parse_iso_date(date_string)
        expected = (
            None
            if not is_valid
            else {
                "date_obj": datetime(2020, 1, 2, 3, 4, seconds, microseconds),
                "period": "time",
                "locale": None,
            }
        )
        self.assertEqual(actual, expected)

    @parameterized.expand(
        [
            # datetime year limits
            param(
                f"{MAXYEAR + 1}-01-01",
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
                f"{MINYEAR - 1:04}-12-31",
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
            # hour limits
            param(
                "2020-01-01 -01:00:00",
                None,
            ),
            param(
                "2020-01-01 -00:00:00",
                None,
            ),
            param(
                "2020-01-01 00:00:00",
                {"date_obj": datetime(2020, 1, 1, 0, 0, 0), "period": "time"},
            ),
            param(
                "2020-01-01 23:00:00",
                {"date_obj": datetime(2020, 1, 1, 23, 0, 0), "period": "time"},
            ),
            param(
                "2020-01-01 24:00:00",
                None,
            ),
            param(
                "2020-01-01 25:00:00",
                None,
            ),
            # minute limits
            param(
                "2020-01-01 00:-01:00",
                None,
            ),
            param(
                "2020-01-01 00:-00:00",
                None,
            ),
            # Duplicate test of 2020-01-01 00:00:00 omitted
            param(
                "2020-01-01 00:59:00",
                {"date_obj": datetime(2020, 1, 1, 0, 59, 0), "period": "time"},
            ),
            param(
                "2020-01-01 00:60:00",
                None,
            ),
            param(
                "2020-01-01 00:61:00",
                None,
            ),
            # second limits
            param(
                "2020-01-01 00:00:-01",
                None,
            ),
            param(
                "2020-01-01 00:00:-00",
                None,
            ),
            # Duplicate test of 2020-01-01 00:00:00 omitted
            param(
                "2020-01-01 00:00:59",
                {"date_obj": datetime(2020, 1, 1, 0, 0, 59), "period": "time"},
            ),
            param(
                "2020-01-01 00:00:60",
                None,
            ),
            param(
                "2020-01-01 00:00:61",
                None,
            ),
            # microsecond limits
            param(
                "2020-01-01 00:00:-00.000001",
                None,
            ),
            param(
                "2020-01-01 00:00:-00.000000",
                None,
            ),
            param(
                "2020-01-01 00:00:00.000000",
                {"date_obj": datetime(2020, 1, 1, 0, 0, 0, 0), "period": "time"},
            ),
            param(
                "2020-01-01 00:00:00.999999",
                {"date_obj": datetime(2020, 1, 1, 0, 0, 0, 999999), "period": "time"},
            ),
        ]
    )
    def test_limits(self, date_string: str, result: dict[str, Any] | None) -> None:
        actual = _parse_iso_date(date_string)
        expected = None if result is None else {**result, "locale": None}
        self.assertEqual(actual, expected)

    # Notes:
    #
    # -   Python rounds to the nearest even number: 1.5 and 2.5 are both
    #     rounded to 2.
    #
    # -   We do not round above the limit of microseconds: 999999.
    @parameterized.expand(
        [
            param("2020-01-01 00:00:00.0000000", 0),
            param("2020-01-01 00:00:00.0000001", 0),
            param("2020-01-01 00:00:00.0000004", 0),
            param("2020-01-01 00:00:00.0000005", 0),
            param("2020-01-01 00:00:00.0000006", 1),
            param("2020-01-01 00:00:00.0000009", 1),
            param("2020-01-01 00:00:00.0000010", 1),
            param("2020-01-01 00:00:00.0000011", 1),
            param("2020-01-01 00:00:00.0000014", 1),
            param("2020-01-01 00:00:00.0000015", 2),
            param("2020-01-01 00:00:00.0000016", 2),
            param("2020-01-01 00:00:00.0000019", 2),
            param("2020-01-01 00:00:00.9999984", 999998),
            param("2020-01-01 00:00:00.9999985", 999998),
            param("2020-01-01 00:00:00.9999986", 999999),
            param("2020-01-01 00:00:00.9999989", 999999),
            param("2020-01-01 00:00:00.9999990", 999999),
            param("2020-01-01 00:00:00.9999991", 999999),
            param("2020-01-01 00:00:00.9999994", 999999),
            param("2020-01-01 00:00:00.9999995", 999999),
            param("2020-01-01 00:00:00.9999996", 999999),
            param("2020-01-01 00:00:00.9999999", 999999),
        ]
    )
    def test_microsecond_rounding(self, date_string: str, microseconds: int) -> None:
        actual = _parse_iso_date(date_string)
        expected = {
            "date_obj": datetime(2020, 1, 1, 0, 0, 0, microseconds),
            "period": "time",
            "locale": None,
        }
        self.assertEqual(actual, expected)

    @parameterized.expand(
        [
            param("20210101T000000Z", datetime(2021, 1, 1, tzinfo=timezone.utc)),
            param(
                "20210101T123045,5-0330",
                datetime(
                    2021,
                    1,
                    1,
                    12,
                    30,
                    45,
                    500000,
                    tzinfo=timezone(-timedelta(hours=3, minutes=30)),
                ),
            ),
            param("20210629", datetime(2021, 6, 29)),
        ]
    )
    def test_parse(self, date_string: str, expected: datetime) -> None:
        self.assertEqual(parse(date_string), expected)

    def test_disabled(self) -> None:
        parsers = [p for p in settings.PARSERS if p != "iso"]
        self.assertIsNone(parse("20210629", settings={"PARSERS": parsers}))
