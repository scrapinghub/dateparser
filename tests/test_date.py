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
from dateparser.languages import LanguageDataLoader
from tests import BaseTestCase


class DateRangeTest(BaseTestCase):
    def setUp(self):
        super(DateRangeTest, self).setUp()
        self.result = NotImplemented

    @parameterized.expand([
        param(begin=datetime(2014, 6, 15), end=datetime(2014, 6, 25), expected_length=10)
    ])
    def test_date_range(self, begin, end, expected_length):
        self.when_date_range_generated(begin, end)
        self.then_range_length_is(expected_length)
        self.then_all_dates_are_present_in_range(begin, end)
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
            self.result = error

    def then_expected_months_are(self, expected):
        self.assertEqual(expected,
                         [(d.year, d.month) for d in self.result])

    def then_range_length_is(self, expected_length):
        self.assertEqual(expected_length, len(self.result))

    def then_all_dates_are_present_in_range(self, begin, end):
        date_under_test = begin
        while date_under_test < end:
            self.assertIn(date_under_test, self.result)
            date_under_test += timedelta(days=1)

    def then_range_is_in_ascending_order(self):
        for i in xrange(len(self.result) - 1):
            self.assertLess(self.result[i], self.result[i + 1])

    def then_period_was_rejected(self, period):
        self.assertIsInstance(self.result, ValueError)
        self.assertEqual('Invalid argument: {}'.format(period), self.result.message)


class GetIntersectingPeriodsTest(BaseTestCase):
    def setUp(self):
        super(GetIntersectingPeriodsTest, self).setUp()
        self.intersected_dates = NotImplemented
        self.expected_results = NotImplemented
        self.period = NotImplemented
        self.period_high = NotImplemented
        self.period_low = NotImplemented
        self.results = NotImplemented
        self.results = NotImplemented

    @parameterized.expand([
        param(low=datetime(2014, 6, 15), high=datetime(2014, 6, 16), length=1)])
    def test_date_arguments_and_date_range_with_default_post_days(self, low, high, length):
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period('day')
        self.when_intersecting_period_calculated()
        self.then_all_dates_are_present_in_range()
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
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period('month')
        self.given_expected_results(expected_results)
        self.when_intersecting_period_calculated()
        self.then_should_one_date_for_each_date(expected_results)

    @parameterized.expand([
        param(low=datetime(2014, 4, 15),
              high=datetime(2014, 5, 15),
              period='month',
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1)]),
        param(low=datetime(2014, 10, 30, 4, 30),
              high=datetime(2014, 11, 7, 5, 20),
              period='week',
              expected_results=[datetime(2014, 10, 27), datetime(2014, 11, 3)]),
        param(low=datetime(2014, 8, 13, 13, 21),
              high=datetime(2014, 8, 14, 14, 7),
              period='day',
              expected_results=[datetime(2014, 8, 13), datetime(2014, 8, 14)]),
        param(low=datetime(2014, 5, 11, 22, 4),
              high=datetime(2014, 5, 12, 0, 5),
              period='hour',
              expected_results=[datetime(2014, 5, 11, 22, 0),
                                datetime(2014, 5, 11, 23, 0),
                                datetime(2014, 5, 12, 0, 0)]),
        param(low=datetime(2014, 4, 25, 11, 11, 11),
              high=datetime(2014, 4, 25, 11, 12, 11),
              period='minute',
              expected_results=[datetime(2014, 4, 25, 11, 11, 0),
                                datetime(2014, 4, 25, 11, 12, 0)]),
        param(low=datetime(2014, 12, 31, 23, 59, 58, 500),
              high=datetime(2014, 12, 31, 23, 59, 59, 600),
              period='second',
              expected_results=[datetime(2014, 12, 31, 23, 59, 58, 0),
                                datetime(2014, 12, 31, 23, 59, 59, 0)]),
    ])
    def test_periods(self, low, high, period, expected_results):
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period(period)
        self.given_expected_results(expected_results)
        self.when_intersecting_period_calculated()
        self.then_should_one_date_for_each_date(expected_results)

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
    def test_should_reject_easily_mistaken_dateutil_arguments(self, periods):
        self.given_period_low(datetime(2014, 6, 15))
        self.given_period_high(datetime(2014, 6, 25))
        self.when_multiple_periods_are_parsed(periods)
        self.then_should_reject_easily_mistaken_dateutil_arguments(periods)

    @parameterized.expand([
        param(low=datetime(2014, 4, 15), high=datetime(2014, 4, 14), period='month'),
        param(low=datetime(2014, 4, 25), high=datetime(2014, 4, 25), period='month'),
    ])
    def test_empty_period(self, low, high, period):
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period(period)
        self.when_intersecting_period_calculated()
        self.then_period_is_empty()

    def given_expected_results(self, expected_results):
        self.expected_results = expected_results

    def given_period_low(self, low):
        self.period_low = low

    def given_period_high(self, high):
        self.period_high = high

    def given_period(self, period):
        self.period = period

    def when_intersecting_period_calculated(self):
        self.intersected_dates = list(date.get_intersecting_periods(
            self.period_low, self.period_high, period=self.period))

    def then_should_one_date_for_each_date(self, expected_results):
        self.assertEquals(expected_results, self.intersected_dates)

    def then_date_range_length_is(self, size):
        self.assertEquals(size, len(self.intersected_dates))

    def then_all_dates_are_present_in_range(self):
        date_under_test = self.period_low
        while date_under_test < self.period_high:
            self.assertIn(date_under_test, self.intersected_dates)
            date_under_test += timedelta(days=1)

    def then_period_is_empty(self):
        self.assertEquals([], self.intersected_dates)

    def when_multiple_periods_are_parsed(self, periods):
        self.results = []
        for period in periods:
            try:
                result = date.get_intersecting_periods(self.period_low, self.period_high, period=period).next()
            except Exception as error:
                result = error
            finally:
                self.results.append(result)

    def then_should_reject_easily_mistaken_dateutil_arguments(self, periods):
        for p in izip(self.results, periods):
            self.assertIsInstance(p[0], ValueError)
            self.assertEqual('Invalid period: {}'.format(p[1]), p[0].message)


class ParseDateWithFormats(BaseTestCase):
    def setUp(self):
        super(ParseDateWithFormats, self).setUp()
        self.dt_data = NotImplemented
        self.day = NotImplemented
        self.month = NotImplemented
        self.invalid_date = NotImplemented
        self.year = NotImplemented
        self.date_obj = NotImplemented
        self.datetime_mock = NotImplemented
        self.parsed_invalid_date = NotImplemented

    def test_date_with_not_matching_format_is_not_parsed(self):
        self.given_invalid_date('yesterday')
        self.when_shouldnt_parse_invalid_date()
        self.then_shouldnt_parse_invalid_date()

    def test_should_parse_date(self):
        self.when_date_is_parsed_with_format('25-03-14', '%d-%m-%y')
        self.then_parsed_date_is(datetime(2014, 3, 25))

    def test_should_use_current_year_for_dates_without_year(self):
        self.given_today(datetime(2015, 2, 4))
        self.when_date_is_parsed_with_format('09.16', "%m.%d")
        self.then_parsed_date_is(datetime(2015, 9, 16))

    def test_should_use_date_for_dates_without_day(self):
        self.given_now(datetime(2014, 8, 12))
        self.when_date_is_parsed_with_format('August 2014', '%B %Y')
        self.then_dates_are_parsed()
        self.then_period_equal('month')
        self.then_parsed_date_is(datetime(2014, 8, 31))

    def given_today(self, date_obj):
        self.date_obj = date_obj

    def given_invalid_date(self, date_str):
        self.invalid_date = date_str

    def given_now(self, given_date):
        self.datetime_mock = Mock(wraps=datetime)
        self.datetime_mock.utcnow = Mock(return_value=given_date)
        self.add_patch(patch('dateparser.date_parser.datetime', new=self.datetime_mock))

    def when_date_is_parsed_with_format(self, some_date, some_format):
        self.dt_data = date.parse_with_formats(some_date, [some_format])

    def when_shouldnt_parse_invalid_date(self):
        self.parsed_invalid_date = date.parse_with_formats(self.invalid_date,
                                                           ['%Y-%m-%d'])['date_obj']

    def then_parsed_date_is(self, date_obj):
        self.assertEquals(date_obj.date(), self.dt_data['date_obj'].date())

    def then_shouldnt_parse_invalid_date(self):
        self.assertIsNone(self.parsed_invalid_date)

    def then_dates_are_parsed(self):
        self.assertIsNotNone(self.dt_data)

    def then_period_equal(self, period):
        self.assertEquals(period, self.dt_data['period'])


class DateDataParserTest(BaseTestCase):
    def setUp(self):
        super(DateDataParserTest, self).setUp()
        self.parser = date.DateDataParser()
        self.date_format = NotImplemented
        self.date_strings = NotImplemented
        self.date_string = NotImplemented
        self.date_data = NotImplemented
        self.results = NotImplemented
        self.date_format = NotImplemented
        self.dates = NotImplemented
        self.known_languages = NotImplemented
        self.language_loader = NotImplemented
        self.language_map = NotImplemented
        self.ordered_languages = NotImplemented
        self.today = NotImplemented
        self._data = NotImplemented

    def check_equal(self, first, second, date_string):
        self.assertEqual(first, second, "%s != %s for date_string:  '%s'" %
                         (repr(first), repr(second), date_string))

    def test_time_in_today_should_return_today(self):
        self.given_date_string('10:04am EDT')
        self.given_today()
        self.when_date_data_is_parsed()
        self.then_date_was_parsed()

    # Today
    # Yesterday
    # Day before yesterday
    @parameterized.expand([
        param('today', days_ago=0),
        param('Today', days_ago=0),
        param('TODAY', days_ago=0),
        param('Сегодня', days_ago=0),
        param('Hoje', days_ago=0),
        param('Oggi', days_ago=0),
        param('yesterday', days_ago=1),
        param(' Yesterday \n', days_ago=1),
        param('Ontem', days_ago=1),
        param('Ieri', days_ago=1),
        param('the day before yesterday', days_ago=2),
        param('The DAY before Yesterday', days_ago=2),
        param('Anteontem', days_ago=2),
        param('Avant-hier', days_ago=2),
    ])
    def test_temporal_nouns_are_parsed(self, date_string, days_ago):
        self.given_date_string(date_string)
        self.given_today()
        self.when_date_string_is_parsed()
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

    def test_get_date_data_should_not_strip_timezone_info(self):
        date_string_with_tz_info = '2014-10-09T17:57:39+00:00'
        date_data = self.parser.get_date_data(date_string_with_tz_info)
        self.assertTrue(hasattr(date_data['date_obj'], 'tzinfo'))

    def test_should_parse_date_with_timezones_using_format(self):
        self.given_date_string("2014/11/17 14:56 EDT")
        self.given_date_format("%Y/%m/%d %H:%M EDT")
        self.when_should_parse_date_with_timezones_using_format()
        self.then_period_is('day')
        self.then_should_parse_date_with_expected_date(datetime(2014, 11, 17, 14, 56))

    def test_should_parse_with_no_break_space_in_dates(self):
        date_string = "08-08-2014\xa018:29"
        expected = datetime(2014, 8, 8, 18, 29)
        date_data = self.parser.get_date_data(date_string)
        self.assertEqual(expected, date_data['date_obj'])

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

    def given_date_string(self, date_string):
        self.date_string = date_string

    def given_date_format(self, date_format):
        self.date_format = date_format

    def given_today(self):
        self.today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    def when_date_string_is_parsed(self):
        self.date_data = self.parser.get_date_data(self.date_string)

    def when_date_data_is_parsed(self):
        self.date_data = self.parser.get_date_data(self.date_string)

    def when_should_parse_date_with_timezones_using_format(self):
        self.date_data = self.parser.get_date_data(self.date_string, date_formats=[self.date_format])

    def then_date_was_parsed(self):
        self.assertIsNotNone(self.date_data['date_obj'])

    def then_date_is_n_days_ago(self, days):
        self.assertIsNotNone(self.date_data['date_obj'])
        expected_days = self.today.date() - self.date_data['date_obj'].date()
        self.assertEqual(expected_days.days, days)

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


if __name__ == '__main__':
    unittest.main()
