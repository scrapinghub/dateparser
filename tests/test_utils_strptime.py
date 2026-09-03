import locale
from datetime import datetime
from unittest import SkipTest
import warnings

from parameterized import param, parameterized

from dateparser.utils.strptime import strptime
from tests import BaseTestCase


class TestStrptime(BaseTestCase):
    def setUp(self):
        super().setUp()

    def given_system_locale_is(self, locale_str):
        try:
            locale.setlocale(locale.LC_ALL, locale_str)
        except locale.Error:
            raise SkipTest("Locale {} is not installed".format(locale_str))

    def when_date_string_is_parsed(self, date_string, fmt):
        try:
            self.result = strptime(date_string, fmt)
        except ValueError as e:
            self.result = e

    def when_date_string_is_parsed_using_datetime_strptime(self, date_string, fmt):
        try:
            self.result = datetime.strptime(date_string, fmt)
        except ValueError as e:
            self.result = e

    def then_date_object_is(self, expected):
        assert self.result == expected

    def then_date_object_is_instance_of(self, expected):
        assert isinstance(self.result, expected)

    @parameterized.expand(
        [
            param("21 January 2010", "%d %B %Y", expected=datetime(2010, 1, 21, 0, 0)),
            param("2 Mar 2010", "%d %b %Y", expected=datetime(2010, 3, 2, 0, 0)),
            param(
                "12 December 10 10:30",
                "%d %B %y %H:%M",
                expected=datetime(2010, 12, 12, 10, 30),
            ),
            param(
                "12 December 10 22:41",
                "%d %B %y %H:%M",
                expected=datetime(2010, 12, 12, 22, 41),
            ),
            param(
                "12 February 2016 11:41",
                "%d %B %Y %I:%M",
                expected=datetime(2016, 2, 12, 11, 41),
            ),
            param("21 Jan 2010", "%d %b %Y", expected=datetime(2010, 1, 21, 0, 0)),
            param(
                "12 Dec 10 10:30",
                "%d %b %y %H:%M",
                expected=datetime(2010, 12, 12, 10, 30),
            ),
            param(
                "12 Feb 2016 11:41",
                "%d %b %Y %I:%M",
                expected=datetime(2016, 2, 12, 11, 41),
            ),
        ]
    )
    def test_dates_with_months_are_parsed_if_locale_is_non_english(
        self, date_string, fmt, expected
    ):
        self.given_system_locale_is("fr_FR.UTF-8")
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is(expected)

    @parameterized.expand(
        [
            param(
                "Monday 21 January 2010",
                "%A %d %B %Y",
                expected=datetime(2010, 1, 21, 0, 0),
            ),
            param("Tue 2 Mar 2010", "%a %d %b %Y", expected=datetime(2010, 3, 2, 0, 0)),
            param(
                "Friday 12 December 10 10:30",
                "%A %d %B %y %H:%M",
                expected=datetime(2010, 12, 12, 10, 30),
            ),
            param(
                "Wed 12 December 10 22:41",
                "%a %d %B %y %H:%M",
                expected=datetime(2010, 12, 12, 22, 41),
            ),
            param(
                "Thu 12 February 2016 11:41",
                "%a %d %B %Y %I:%M",
                expected=datetime(2016, 2, 12, 11, 41),
            ),
        ]
    )
    def test_dates_with_days_are_parsed_if_locale_is_non_english(
        self, date_string, fmt, expected
    ):
        self.given_system_locale_is("fr_FR.UTF-8")
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is(expected)

    def test_parsing_date_should_fail_using_datetime_strptime_if_locale_is_non_english(
        self,
    ):
        self.given_system_locale_is("fr_FR.UTF-8")
        self.when_date_string_is_parsed_using_datetime_strptime(
            "21 february 2010", "%d %B %Y"
        )
        self.then_date_object_is_instance_of(ValueError)

    @parameterized.expand(
        [
            param(
                "12 Dec 10 10:30:55.1",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 100000),
            ),
            param(
                "12 Dec 10 10:30:55.10",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 100000),
            ),
            param(
                "12 Dec 10 10:30:55.100",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 100000),
            ),
            param(
                "12 Dec 10 10:30:55.1000",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 100000),
            ),
            param(
                "12 Dec 10 10:30:55.100000",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 100000),
            ),
            param(
                "12 Dec 10 10:30:55.000001",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 1),
            ),
            param(
                "12 Dec 10 10:30:55.000011",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 11),
            ),
            param(
                "12 Dec 10 10:30:55.000111",
                "%d %b %y %H:%M:%S.%f",
                expected=datetime(2010, 12, 12, 10, 30, 55, 111),
            ),
            param(
                "12 Feb 2016 11:41:23",
                "%d %b %Y %I:%M:%S",
                expected=datetime(2016, 2, 12, 11, 41, 23),
            ),
            param(
                "11 Dec 10 10:30:2011.999999",
                "%y %b %S %H:%M:%Y.%f",
                expected=datetime(2011, 12, 1, 10, 30, 10, 999999),
            ),
        ]
    )
    def test_microseconds_are_parsed_correctly(self, date_string, fmt, expected):
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is(expected)

    @parameterized.expand(
        [
            param(date_string="oct 14", fmt=r"%m %d"),
            param(date_string="10-14", fmt=r"%b %d"),
            param(date_string="12 Dec 10:30:55.000111", fmt="%d %b %H:%M:%S.%f"),
            param(date_string="Wed 12 December 22:41", fmt="%a %d %B %H:%M"),
        ]
    )
    def test_dates_with_no_year_do_not_raise_a_deprecation_warning(
        self, date_string, fmt
    ):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.when_date_string_is_parsed(date_string, fmt)
            year_warnings = [
                warn
                for warn in w
                if "day of month without a year specified is ambiguious"
                in str(warn.message)
            ]
            self.assertEqual(len(year_warnings), 0)

    @parameterized.expand(
        [
            param(
                date_string="oct 14",
                fmt=r"%b %d",
                expected=datetime(2010, 10, 14, 0, 0),
            ),
            param(
                date_string="10 14",
                fmt=r"%m %d",
                expected=datetime(2010, 10, 14, 0, 0),
            ),
            param(
                date_string="14 Oct",
                fmt=r"%d %b",
                expected=datetime(2010, 10, 14, 0, 0),
            ),
            param(
                "Monday 21 January",
                "%A %d %B",
                expected=datetime(2010, 1, 21, 0, 0),
            ),
            param(
                "Tue 2 Mar",
                "%a %d %b",
                expected=datetime(2010, 3, 2, 0, 0),
            ),
            param(
                "Friday 12 December 10:30",
                "%A %d %B %H:%M",
                expected=datetime(2010, 12, 12, 10, 30),
            ),
        ]
    )
    def test_dates_with_no_year_use_the_current_year(
        self, date_string: str, fmt: str, expected: datetime
    ):
        self.when_date_string_is_parsed(date_string, fmt)
        current_year = datetime.today().year
        expected = expected.replace(year=current_year)
        self.assertEqual(self.result, expected)

    @parameterized.expand(
        [
            param("1999001", "%Y%j", expected=datetime(1999, 1, 1)),
            param("1999032", "%Y%j", expected=datetime(1999, 2, 1)),
            param("1999050", "%Y%j", expected=datetime(1999, 2, 19)),
            param("1999059", "%Y%j", expected=datetime(1999, 2, 28)),
            param("1999060", "%Y%j", expected=datetime(1999, 3, 1)),
            param("1999365", "%Y%j", expected=datetime(1999, 12, 31)),
            param("2000060", "%Y%j", expected=datetime(2000, 2, 29)),
            param("2000061", "%Y%j", expected=datetime(2000, 3, 1)),
            param("2000366", "%Y%j", expected=datetime(2000, 12, 31)),
            param("2400366", "%Y%j", expected=datetime(2400, 12, 31)),
            param("2023-100", "%Y-%j", expected=datetime(2023, 4, 10)),
            param("2024 366", "%Y %j", expected=datetime(2024, 12, 31)),
            param("1999001 12:30", "%Y%j %H:%M", expected=datetime(1999, 1, 1, 12, 30)),
        ]
    )
    def test_day_of_year_is_parsed(self, date_string, fmt, expected):
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is(expected)

    @parameterized.expand(
        [
            # 366 is only a valid day of year in leap years.
            param("1999366", "%Y%j"),
            param("2023-366", "%Y-%j"),
            param("1900366", "%Y%j"),  # divisible by 100 but not by 400
            param("2100366", "%Y%j"),
            param("2025366 12:30", "%Y%j %H:%M"),
            # Values that strptime itself rejects.
            param("1999000", "%Y%j"),
            param("1999367", "%Y%j"),
            param("1999777", "%Y%j"),
        ]
    )
    def test_day_of_year_out_of_range_is_not_parsed(self, date_string, fmt):
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is_instance_of(ValueError)

    @parameterized.expand(
        [
            param("%j", "%%j", expected=datetime(1900, 1, 1)),
            param("1999%j", "%Y%%j", expected=datetime(1999, 1, 1)),
            # A literal "%j" must not be taken for a day of year directive, not
            # even when another directive rolls the year over.
            param("2023 53 1 %j", "%Y %U %w %%j", expected=datetime(2024, 1, 1)),
        ]
    )
    def test_escaped_day_of_year_directive_is_a_literal(
        self, date_string, fmt, expected
    ):
        self.when_date_string_is_parsed(date_string, fmt)
        self.then_date_object_is(expected)
