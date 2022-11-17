from datetime import date, datetime
from pytz import utc

from parameterized import parameterized, param

import dateparser
from tests import BaseTestCase


class TestParseFunction(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.result = NotImplemented

    @parameterized.expand([
        param(date_string="24 de Janeiro de 2014", expected_date=date(2014, 1, 24)),
        param(date_string="2 de Enero de 2013", expected_date=date(2013, 1, 2)),
        param(date_string="January 25, 2014", expected_date=date(2014, 1, 25)),
    ])
    def test_parse_dates_in_different_languages(self, date_string, expected_date):
        self.when_date_is_parsed_with_defaults(date_string)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand([
        param(date_string="May 5, 2000 13:00",
              expected_date=datetime(2000, 5, 5, 13, 0)),
        param(date_string="August 8, 2018 5 PM",
              expected_date=datetime(2018, 8, 8, 17, 0)),
        param(date_string="February 26, 1981 5 am UTC",
              expected_date=datetime(1981, 2, 26, 5, 0, tzinfo=utc)),
    ])
    def test_parse_dates_with_specific_time(self, date_string, expected_date):
        self.when_date_is_parsed_with_defaults(date_string)
        self.then_parsed_date_and_time_is(expected_date)

    @parameterized.expand([
        param(date_string="May 5, 2000 13:00",
              expected_date=datetime(2000, 5, 5, 13, 0),
              relative=datetime(2000, 1, 1, 0, 0, tzinfo=utc)),
        param(date_string="August 8, 2018 5 PM",
              expected_date=datetime(2018, 8, 8, 17, 0),
              relative=datetime(1900, 5, 5, 0, 0, tzinfo=utc)),
        param(date_string="February 26, 1981 5 am UTC",
              expected_date=datetime(1981, 2, 26, 5, 0, tzinfo=utc),
              relative=datetime(1981, 2, 26, 5, 0, tzinfo=utc)),
    ])
    def test_parse_dates_with_specific_time_and_settings(self, date_string, expected_date, relative):
        self.when_date_is_parsed_with_settings(date_string, settings={'RELATIVE_BASE': relative})
        self.then_parsed_date_and_time_is(expected_date)

    @parameterized.expand([
        param(date_string="24 de Janeiro de 2014", languages=['pt'], expected_date=date(2014, 1, 24)),
    ])
    def test_dates_which_match_languages_are_parsed(self, date_string, languages, expected_date):
        self.when_date_is_parsed(date_string, languages=languages)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand([
        param(date_string="January 24, 2014", languages=['pt']),
    ])
    def test_dates_which_do_not_match_languages_are_not_parsed(self, date_string, languages):
        self.when_date_is_parsed(date_string, languages=languages)
        self.then_date_was_not_parsed()

    @parameterized.expand([
        param(date_string="24 de Janeiro de 2014", locales=['pt-TL'], expected_date=date(2014, 1, 24)),
    ])
    def test_dates_which_match_locales_are_parsed(self, date_string, locales, expected_date):
        self.when_date_is_parsed(date_string, locales=locales)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand([
        param(date_string="January 24, 2014", locales=['pt-AO']),
    ])
    def test_dates_which_do_not_match_locales_are_not_parsed(self, date_string, locales):
        self.when_date_is_parsed(date_string, locales=locales)
        self.then_date_was_not_parsed()

    def when_date_is_parsed_with_defaults(self, date_string):
        self.result = dateparser.parse(date_string)

    def when_date_is_parsed(self, date_string, languages=None, locales=None):
        self.result = dateparser.parse(date_string, languages=languages, locales=locales)

    def when_date_is_parsed_with_settings(self, date_string, settings=None):
        self.result = dateparser.parse(date_string, settings=settings)

    def then_parsed_date_is(self, expected_date):
        self.assertEqual(self.result, datetime.combine(expected_date, datetime.min.time()))

    def then_parsed_date_and_time_is(self, expected_date):
        self.assertEqual(self.result, expected_date)

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result)
