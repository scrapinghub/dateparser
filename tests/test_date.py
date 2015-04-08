#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import izip
from types import MethodType

from mock import Mock, patch
from nose_parameterized import parameterized, param

from dateparser import date
from dateparser.date import get_last_day_of_month
from dateparser.languages import LanguageDataLoader
from tests import BaseTestCase


class DateRangeTest(BaseTestCase):
    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.result = NotImplemented
        self.error = NotImplemented

    @parameterized.expand([
        param(begin=datetime(2014, 6, 15), end=datetime(2014, 6, 25), expected_length=10)
    ])
    def test_date_range(self, begin, end, expected_length):
        self.when_date_range_generated(begin, end)
        self.then_range_length_is(expected_length)
        self.then_all_dates_in_range_are_present(begin, end)
        self.then_range_is_in_ascending_order()

    @parameterized.expand([
        param(begin=datetime(2014, 4, 15),
              end=datetime(2014, 6, 25),
              expected_months=[(2014, 4), (2014, 5), (2014, 6)]),
        param(begin=datetime(2014, 4, 25),
              end=datetime(2014, 5, 5),
              expected_months=[(2014, 4), (2014, 5)]),
        param(begin=datetime(2014, 4, 5),
              end=datetime(2014, 4, 25),
              expected_months=[(2014, 4)]),
        param(begin=datetime(2014, 4, 25),
              end=datetime(2014, 6, 5),
              expected_months=[(2014, 4), (2014, 5), (2014, 6)]),
    ])
    def test_one_date_for_each_month(self, begin, end, expected_months):
        self.when_date_range_generated(begin, end, months=1)
        self.then_expected_months_are(expected_months)

    @parameterized.expand([
        'year',
        'month',
        'week',
        'day',
        'hour',
        'minute',
        'second',
    ])
    def test_should_reject_easily_mistaken_dateutil_arguments(self, invalid_period):
        self.when_date_range_generated(begin=datetime(2014, 6, 15),
                                       end=datetime(2014, 6, 25),
                                       **{invalid_period: 1})
        self.then_period_was_rejected(invalid_period)

    def when_date_range_generated(self, begin, end, **size):
        try:
            self.result = list(date.date_range(begin, end, **size))
        except Exception as error:
            self.error = error

    def then_expected_months_are(self, expected):
        self.assertEqual(expected,
                         [(d.year, d.month) for d in self.result])

    def then_range_length_is(self, expected_length):
        self.assertEqual(expected_length, len(self.result))

    def then_all_dates_in_range_are_present(self, begin, end):
        date_under_test = begin
        while date_under_test < end:
            self.assertIn(date_under_test, self.result)
            date_under_test += timedelta(days=1)

    def then_range_is_in_ascending_order(self):
        for i in xrange(len(self.result) - 1):
            self.assertLess(self.result[i], self.result[i + 1])

    def then_period_was_rejected(self, period):
        self.assertIsInstance(self.error, ValueError)
        self.assertEqual('Invalid argument: {}'.format(period), str(self.error))


class GetIntersectingPeriodsTest(BaseTestCase):
    def setUp(self):
        super(GetIntersectingPeriodsTest, self).setUp()
        self.result = NotImplemented
        self.error = NotImplemented

    @parameterized.expand([
        param(low=datetime(2014, 6, 15), high=datetime(2014, 6, 16), length=1)])
    def test_date_arguments_and_date_range_with_default_post_days(self, low, high, length):
        self.when_intersecting_period_calculated(low, high, period_size='day')
        self.then_all_dates_in_range_are_present(begin=low, end=high)
        self.then_date_range_length_is(length)

    @parameterized.expand([
        param(low=datetime(2014, 4, 15),
              high=datetime(2014, 6, 25),
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1), datetime(2014, 6, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 5, 5),
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1)]),
        param(low=datetime(2014, 4, 5),
              high=datetime(2014, 4, 25),
              expected_results=[datetime(2014, 4, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 6, 5),
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1), datetime(2014, 6, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 4, 25),
              expected_results=[]),
        param(low=datetime(2014, 12, 31),
              high=datetime(2015, 1, 1),
              expected_results=[datetime(2014, 12, 1)]),
    ])
    def test_should_one_date_for_each_month(self, low, high, expected_results):
        self.when_intersecting_period_calculated(low, high, period_size='month')
        self.then_results_are(expected_results)

    @parameterized.expand([
        param(low=datetime(2014, 4, 15),
              high=datetime(2014, 5, 15),
              period_size='month',
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1)]),
        param(low=datetime(2014, 10, 30, 4, 30),
              high=datetime(2014, 11, 7, 5, 20),
              period_size='week',
              expected_results=[datetime(2014, 10, 27), datetime(2014, 11, 3)]),
        param(low=datetime(2014, 8, 13, 13, 21),
              high=datetime(2014, 8, 14, 14, 7),
              period_size='day',
              expected_results=[datetime(2014, 8, 13), datetime(2014, 8, 14)]),
        param(low=datetime(2014, 5, 11, 22, 4),
              high=datetime(2014, 5, 12, 0, 5),
              period_size='hour',
              expected_results=[datetime(2014, 5, 11, 22, 0),
                                datetime(2014, 5, 11, 23, 0),
                                datetime(2014, 5, 12, 0, 0)]),
        param(low=datetime(2014, 4, 25, 11, 11, 11),
              high=datetime(2014, 4, 25, 11, 12, 11),
              period_size='minute',
              expected_results=[datetime(2014, 4, 25, 11, 11, 0),
                                datetime(2014, 4, 25, 11, 12, 0)]),
        param(low=datetime(2014, 12, 31, 23, 59, 58, 500),
              high=datetime(2014, 12, 31, 23, 59, 59, 600),
              period_size='second',
              expected_results=[datetime(2014, 12, 31, 23, 59, 58, 0),
                                datetime(2014, 12, 31, 23, 59, 59, 0)]),
    ])
    def test_periods(self, low, high, period_size, expected_results):
        self.when_intersecting_period_calculated(low, high, period_size=period_size)
        self.then_results_are(expected_results)

    @parameterized.expand([
        param('years'),
        param('months'),
        param('days'),
        param('hours'),
        param('minutes'),
        param('seconds'),
        param('microseconds'),
        param('some_period'),
    ])
    def test_should_reject_easily_mistaken_dateutil_arguments(self, period_size):
        self.when_intersecting_period_calculated(low=datetime(2014, 6, 15),
                                                 high=datetime(2014, 6, 25),
                                                 period_size=period_size)
        self.then_should_reject_easily_mistaken_dateutil_argument(period_size)

    @parameterized.expand([
        param(low=datetime(2014, 4, 15), high=datetime(2014, 4, 14), period_size='month'),
        param(low=datetime(2014, 4, 25), high=datetime(2014, 4, 25), period_size='month'),
    ])
    def test_empty_period(self, low, high, period_size):
        self.when_intersecting_period_calculated(low, high, period_size)
        self.then_period_is_empty()

    def when_intersecting_period_calculated(self, low, high, period_size):
        try:
            self.result = list(date.get_intersecting_periods(low, high, period=period_size))
        except Exception as error:
            self.error = error

    def then_results_are(self, expected_results):
        self.assertEquals(expected_results, self.result)

    def then_date_range_length_is(self, size):
        self.assertEquals(size, len(self.result))

    def then_all_dates_in_range_are_present(self, begin, end):
        date_under_test = begin
        while date_under_test < end:
            self.assertIn(date_under_test, self.result)
            date_under_test += timedelta(days=1)

    def then_period_is_empty(self):
        self.assertEquals([], self.result)

    def then_should_reject_easily_mistaken_dateutil_argument(self, period_size):
        self.assertIsInstance(self.error, ValueError)
        self.assertEqual('Invalid period: {}'.format(period_size), str(self.error))


class ParseDateWithFormats(BaseTestCase):
    def setUp(self):
        super(ParseDateWithFormats, self).setUp()
        self.result = NotImplemented

    @parameterized.expand([
        param(date_string='yesterday', date_formats=['%Y-%m-%d']),
    ])
    def test_date_with_not_matching_format_is_not_parsed(self, date_string, date_formats):
        self.when_date_is_parsed_with_formats(date_string, date_formats)
        self.then_date_was_not_parsed()

    @parameterized.expand([
        param(date_string='25-03-14', date_formats=['%d-%m-%y'], expected_result=datetime(2014, 3, 25)),
    ])
    def test_should_parse_date(self, date_string, date_formats, expected_result):
        self.when_date_is_parsed_with_formats(date_string, date_formats)
        self.then_date_was_parsed()
        self.then_parsed_period_is('day')
        self.then_parsed_date_is(expected_result)

    @parameterized.expand([
        param(date_string='09.16', date_formats=['%m.%d'], expected_month=9, expected_day=16),
    ])
    def test_should_use_current_year_for_dates_without_year(
        self, date_string, date_formats, expected_month, expected_day
    ):
        self.given_now(2015, 2, 4)
        self.when_date_is_parsed_with_formats(date_string, date_formats)
        self.then_date_was_parsed()
        self.then_parsed_period_is('day')
        self.then_parsed_date_is(datetime(2015, expected_month, expected_day))

    @parameterized.expand([
        param(date_string='August 2014', date_formats=['%B %Y'], expected_year=2014, expected_month=8),
    ])
    def test_should_use_date_for_dates_without_day(self, date_string, date_formats, expected_year, expected_month):
        self.given_now(2014, 8, 12)
        self.when_date_is_parsed_with_formats(date_string, date_formats)
        self.then_date_was_parsed()
        self.then_parsed_period_is('month')
        self.then_parsed_date_is(datetime(year=expected_year,
                                          month=expected_month,
                                          day=get_last_day_of_month(expected_year, expected_month)))

    def given_now(self, year, month, day, **time):
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=datetime(year, month, day, **time))
        self.add_patch(
            patch('dateparser.date_parser.datetime', new=datetime_mock)
        )

    def when_date_is_parsed_with_formats(self, date_string, date_formats):
        self.result = date.parse_with_formats(date_string, date_formats)

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result['date_obj'])

    def then_date_was_parsed(self):
        self.assertIsNotNone(self.result)
        self.assertIsNotNone(self.result['date_obj'])

    def then_parsed_date_is(self, date_obj):
        self.assertEquals(date_obj.date(), self.result['date_obj'].date())

    def then_parsed_period_is(self, period):
        self.assertEquals(period, self.result['period'])


class DateDataParserTest(BaseTestCase):
    def setUp(self):
        super(DateDataParserTest, self).setUp()
        self.parser = date.DateDataParser()
        self.date_strings = NotImplemented
        self.date_data = NotImplemented
        self.results = NotImplemented
        self.dates = NotImplemented
        self.known_languages = NotImplemented
        self.language_loader = NotImplemented
        self.language_map = NotImplemented
        self.ordered_languages = NotImplemented
        self._data = NotImplemented

    def check_equal(self, first, second, date_string):
        self.assertEqual(first, second, "%s != %s for date_string:  '%s'" %
                         (repr(first), repr(second), date_string))

    @parameterized.expand([
        param('10:04am EDT'),
    ])
    def test_time_in_today_should_return_today(self, date_string):
        self.when_date_string_is_parsed(date_string)
        self.then_date_was_parsed()

    @parameterized.expand([
        # Today
        param('today', days_ago=0),
        param('Today', days_ago=0),
        param('TODAY', days_ago=0),
        param('Сегодня', days_ago=0),
        param('Hoje', days_ago=0),
        param('Oggi', days_ago=0),
        # Yesterday
        param('yesterday', days_ago=1),
        param(' Yesterday \n', days_ago=1),
        param('Ontem', days_ago=1),
        param('Ieri', days_ago=1),
        # Day before yesterday
        param('the day before yesterday', days_ago=2),
        param('The DAY before Yesterday', days_ago=2),
        param('Anteontem', days_ago=2),
        param('Avant-hier', days_ago=2),
    ])
    def test_temporal_nouns_are_parsed(self, date_string, days_ago):
        self.when_date_string_is_parsed(date_string)
        self.then_date_was_parsed()
        self.then_date_is_n_days_ago(days=days_ago)

    def test_should_not_assume_language_too_early(self):
        dates_to_parse = OrderedDict([(u'07.ene.2014 | 12:52', datetime(2014, 1, 7)),
                                      (u'07.feb.2014 | 12:52', datetime(2014, 2, 7)),
                                      (u'07/07/2014', datetime(2014, 7, 7)),
                                      (u'07.jul.2014 | 12:52', datetime(2014, 7, 7)),
                                      (u'07.ago.2014 | 12:52', datetime(2014, 8, 7))])

        self.given_multiple_dates(dates_to_parse)
        self.when_multiple_dates_are_parsed()
        self.then_check_language_too_early()
        self.then_language_too_early_was_parsed()

    def test_should_enable_redetection_for_multiple_languages(self):
        dates_to_parse = OrderedDict([(u'11 Marzo, 2014', datetime(2014, 3, 11)),
                                      (u'13 Março, 2014', datetime(2014, 3, 13)),
                                      (u'13 Ago, 2014', datetime(2014, 8, 13)),
                                      (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
                                      (u'13 Setembro, 2014', datetime(2014, 9, 13))])

        self.given_empty_languages_parser()
        self.given_known_languages('it', 'es', 'pt')
        self.given_multiple_dates(dates_to_parse)
        self.when_multiple_dates_are_parsed()
        self.then_should_enable_redetection_for_multiple_languages()

    @parameterized.expand([
        param("2014-10-09T17:57:39+00:00"),
    ])
    def test_get_date_data_should_not_strip_timezone_info(self, date_string):
        self.when_should_parse_date_with_timezones_using_format(date_string)
        self.then_parsed_date_has_timezone()

    @parameterized.expand([
        param(date_string="2014/11/17 14:56 EDT",
              date_formats=["%Y/%m/%d %H:%M EDT"],
              expected_result=datetime(2014, 11, 17, 14, 56)),
    ])
    def test_should_parse_date_with_timezones_using_format(self, date_string, date_formats, expected_result):
        self.when_should_parse_date_with_timezones_using_format(date_string, date_formats)
        self.then_period_is('day')
        self.then_should_parse_date_with_expected_date(expected_result)

    @parameterized.expand([
        param(date_string="08-08-2014\xa018:29", expected_result=datetime(2014, 8, 8, 18, 29)),
    ])
    def test_should_parse_with_no_break_space_in_dates(self, date_string, expected_result):
        self.when_should_parse_date_with_timezones_using_format(date_string)
        self.then_period_is('day')
        self.then_should_parse_date_with_expected_date(expected_result)

    @parameterized.expand([
        param(['ur', 'li']),
        param(['pk', ]),
    ])
    def test_should_raise_error_when_unknown_language_given(self, shortnames):
        with self.assertRaisesRegexp(ValueError, '%r' % ', '.join(shortnames)):
            date.DateDataParser(languages=shortnames)

    def when_multiple_dates_are_parsed(self):
        self.results = []
        for date_string in self.date_strings:
            try:
                result = self.parser.get_date_data(date_string)
            except Exception as error:
                result = error
            finally:
                self.results.append(result)

    def given_multiple_dates(self, date_to_parse):
        self.date_strings = date_to_parse.keys()
        self.dates = list(date_to_parse.values())

    def given_known_languages(self, *shortnames):
        self.ordered_languages = OrderedDict()

        self.known_languages = [self.language_map.get(shortname)
                                for shortname in shortnames]

        for language in self.known_languages:
            self.ordered_languages[language.shortname] = language

        self.language_loader._data = self.ordered_languages

    def given_empty_languages_parser(self):
        self._data = {}
        self.parser = date.DateDataParser(allow_redetect_language=True)

        language_loader = LanguageDataLoader()
        self.language_map = date.default_language_loader.get_language_map()
        self.language_loader = language_loader
        language_loader._load_data = MethodType(self.given_empty_languages_parser, language_loader)
        self.add_patch(patch('dateparser.date.default_language_loader', new=language_loader))

    def when_date_string_is_parsed(self, date_string):
        self.date_data = self.parser.get_date_data(date_string)

    def when_should_parse_date_with_timezones_using_format(self, date_string, date_formats=None):
        self.date_data = self.parser.get_date_data(date_string, date_formats)

    def then_date_was_parsed(self):
        self.assertIsNotNone(self.date_data['date_obj'])

    def then_date_is_n_days_ago(self, days):
        today = datetime.utcnow().date()
        expected_date = today - timedelta(days=days)
        self.assertEqual(expected_date, self.date_data['date_obj'].date())

    def then_check_language_too_early(self):
        self.assertIsNotNone(self.results)

    def then_language_too_early_was_parsed(self):
        for d in izip(self.results, self.dates, self.date_strings):
            self.assertEqual(d[0]['date_obj'].date(), d[1].date(), d[2])

    def then_should_enable_redetection_for_multiple_languages(self):
        for d in izip(self.results, self.dates):
            self.assertEqual(d[0]['date_obj'].date(), d[1].date())

    def then_period_is(self, day):
        self.assertEqual(day, self.date_data['period'])

    def then_should_parse_date_with_expected_date(self, expected_date):
        self.assertEqual(expected_date, self.date_data['date_obj'])

    def then_parsed_date_has_timezone(self):
        self.assertTrue(hasattr(self.date_data['date_obj'], 'tzinfo'))


if __name__ == '__main__':
    unittest.main()
