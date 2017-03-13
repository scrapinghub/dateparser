import itertools

from datetime import datetime
from tests import BaseTestCase
from nose_parameterized import parameterized, param
from dateparser.utils import (
    find_date_separator, localize_timezone, apply_timezone,
    apply_timezone_from_settings
)

from dateparser.conf import settings


class TestUtils(BaseTestCase):
    def setUp(self):
        super(TestUtils, self).setUp()
        self.date_format = None
        self.result = None

    def given_date_format(self, date_format):
        self.date_format = date_format

    def when_date_seperator_is_parsed(self):
        self.result = find_date_separator(self.date_format)

    def then_date_seperator_is(self, sep):
        self.assertEqual(self.result, sep)

    @parameterized.expand([
        param(date_format=fmt.format(sep=sep), expected_sep=sep)
        for (fmt, sep) in itertools.product(
            ['%d{sep}%m{sep}%Y', '%d{sep}%m{sep}%Y %H:%M'],
            ['/', '.', '-', ':'])
    ])
    def test_separator_extraction(self, date_format, expected_sep):
        self.given_date_format(date_format)
        self.when_date_seperator_is_parsed()
        self.then_date_seperator_is(expected_sep)

    @parameterized.expand([
        param(datetime(2015, 12, 12), timezone='UTC', zone='UTC'),
        param(datetime(2015, 12, 12), timezone='Asia/Karachi', zone='Asia/Karachi'),
    ])
    def test_localize_timezone_function(self, date, timezone, zone):
        tzaware_dt = localize_timezone(date, timezone)
        self.assertEqual(tzaware_dt.tzinfo.zone, zone)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12), timezone='Asia/Karachi', expected=datetime(2015, 12, 12, 15, 12)),
        param(datetime(2015, 12, 12, 10, 12), timezone='-0500', expected=datetime(2015, 12, 12, 5, 12)),
    ])
    def test_apply_timezone_function(self, date, timezone, expected):
        result = apply_timezone(date, timezone)
        result = result.replace(tzinfo=None)
        self.assertEqual(expected, result)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12), timezone='Asia/Karachi', expected=datetime(2015, 12, 12, 15, 12)),
        param(datetime(2015, 12, 12, 10, 12), timezone='-0500', expected=datetime(2015, 12, 12, 5, 12)),
    ])
    def test_apply_timezone_from_settings_function(self, date, timezone, expected):
        result = apply_timezone_from_settings(date, settings.replace(**{'TO_TIMEZONE': timezone, 'TIMEZONE': 'UTC'}))
        self.assertEqual(expected, result)

    @parameterized.expand([
        param(datetime(2015, 12, 12, 10, 12),),
        param(datetime(2015, 12, 12, 10, 12),),
    ])
    def test_apply_timezone_from_settings_function_should_return_tz(self, date):
        result = apply_timezone_from_settings(date, settings.replace(**{'RETURN_AS_TIMEZONE_AWARE': True}))
        self.assertTrue(bool(result.tzinfo))
