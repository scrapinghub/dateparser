#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from mock import Mock, patch
from nose_parameterized import parameterized, param

from dateparser import date
from tests import BaseTestCase


class DateRangeTest(unittest.TestCase):

    def test_should_render_10_days_range(self):
        begin = datetime(2014, 6, 15)
        end = datetime(2014, 6, 25)
        dates = list(date.date_range(begin, end))
        self.assertEquals(10, len(dates))
        self.assertEquals(begin, dates[0])
        self.assertEquals(end - timedelta(days=1), dates[-1])

    def test_should_one_date_for_each_month(self):
        fixtures = [
            (datetime(2014, 4, 15), datetime(2014, 6, 25),
             [(2014, 4), (2014, 5), (2014, 6)]),

            (datetime(2014, 4, 25), datetime(2014, 5, 5),
             [(2014, 4), (2014, 5)]),

            (datetime(2014, 4, 5), datetime(2014, 4, 25),
             [(2014, 4)]),

            (datetime(2014, 4, 25), datetime(2014, 6, 5),
             [(2014, 4), (2014, 5), (2014, 6)]),
        ]

        for begin, end, expected in fixtures:
            result = list(date.date_range(begin, end, months=1))
            self.assertEquals(expected,
                              [(d.year, d.month) for d in result])

    def test_should_reject_easily_mistaken_dateutil_arguments(self):
        begin = datetime(2014, 6, 15)
        end = datetime(2014, 6, 25)

        with self.assertRaisesRegexp(ValueError, "Invalid argument"):
            date.date_range(begin, end, month=1).next()

        with self.assertRaisesRegexp(ValueError, "Invalid argument"):
            date.date_range(begin, end, day=1).next()


class GetIntersectingPeriodsTest(BaseTestCase):

    def test_date_arguments_and_date_range_with_default_post_days(self):
        low = datetime(2014, 6, 15)
        high = datetime(2014, 6, 16)
        dates = list(date.get_intersecting_periods(low, high))
        self.assertEquals(1, len(dates))
        self.assertEquals(low, dates[0])

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
        results = list(date.get_intersecting_periods(low, high, period='month'))
        self.assertEquals(expected_results, results)

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
        results = list(date.get_intersecting_periods(low, high, period=period))
        self.assertEquals(expected_results, results)

    @parameterized.expand([
        'years',
        'months',
        'days',
        'hours',
        'minutes',
        'seconds',
        'microseconds',
        'some_period',
    ])
    def test_should_reject_easily_mistaken_dateutil_arguments(self, invalid_period):
        low = datetime(2014, 6, 15)
        period = datetime(2014, 6, 25)

        with self.assertRaisesRegexp(ValueError, "Invalid period: {}".format(invalid_period)):
            date.get_intersecting_periods(low, period, period=invalid_period).next()

    @parameterized.expand([
        param(low=datetime(2014, 4, 15), high=datetime(2014, 4, 14)),
        param(low=datetime(2014, 4, 25), high=datetime(2014, 4, 25)),
    ])
    def test_empty_period(self, low, high):
        results = list(date.get_intersecting_periods(low, high, period='month'))
        self.assertEquals([], results)


class ParseDateWithFormats(unittest.TestCase):

    def test_shouldnt_parse_invalid_date(self):
        self.assertIsNone(date.parse_with_formats('yesterday', ['%Y-%m-%d'])['date_obj'])

    def test_should_parse_date(self):
        result = date.parse_with_formats('25-03-14', ['%d-%m-%y'])
        self.assertEquals(datetime(2014, 3, 25).date(), result['date_obj'].date())

    def test_should_use_current_year_for_dates_without_year(self):
        today = datetime.today()

        result = date.parse_with_formats('09.16', ["%m.%d"])
        self.assertEquals(datetime(today.year, 9, 16).date(), result['date_obj'].date())

    def test_should_use_current_date_for_dates_without_day(self):
        twelfth = datetime(2014, 8, 12)
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=twelfth)

        with patch('dateparser.date_parser.datetime', new=datetime_mock):
            dt_data = date.parse_with_formats('August 2014', ['%B %Y'])

        self.assertIsNotNone(dt_data)
        self.assertEquals('month', dt_data['period'])
        self.assertEquals(datetime(2014, 8, 31).date(), dt_data['date_obj'].date())

        twelfth = datetime(2014, 2, 12)
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=twelfth)

        with patch('dateparser.date_parser.datetime', new=datetime_mock):
            dt_data = date.parse_with_formats('February 2014', ['%B %Y'])

        self.assertIsNotNone(dt_data)
        self.assertEquals('month', dt_data['period'])
        self.assertEquals(datetime(2014, 2, 28).date(), dt_data['date_obj'].date())


class DateDataParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = date.DateDataParser()

    def check_equal(self, first, second, date_string):
        self.assertEqual(first, second, "%s != %s for date_string:  '%s'" %
                         (repr(first), repr(second), date_string))

    def test_time_in_today_should_return_today(self):
        date_string = '10:04am EDT'
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        date_data = self.parser.get_date_data(date_string)
        self.assertIsNotNone(date_data['date_obj'])
        self.assertEqual(today.date(), date_data['date_obj'].date())

    @parameterized.expand([
        param('today'),
        param('Today'),
        param('TODAY'),
        param('Сегодня'),
        param('Hoje'),
        param('Oggi'),
    ])
    def test_should_return_today(self, date_string):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        date_data = self.parser.get_date_data(date_string)
        self.assertIsNotNone(date_data['date_obj'])
        self.assertEqual(today.date(), date_data['date_obj'].date())

    @parameterized.expand([
        param('yesterday'),
        param(' Yesterday \n'),
        param('Ontem'),
        param('Ieri'),
    ])
    def test_should_return_yesterday(self, date_string):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - relativedelta(days=1)
        date_data = self.parser.get_date_data(date_string)
        self.assertIsNotNone(date_data['date_obj'],
                             "could not parse date from: %s" % date_string)
        self.check_equal(yesterday.date(),
                         date_data['date_obj'].date(), date_string)

    @parameterized.expand([
        param('the day before yesterday'),
        param('The DAY before Yesterday'),
        param('Anteontem'),
        param('Avant-hier'),
    ])
    def test_should_return_day_before_yesterday(self, date_string):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        day_before_yesterday = today - relativedelta(days=2)
        date_data = self.parser.get_date_data(date_string)
        self.assertIsNotNone(date_data['date_obj'])
        self.check_equal(day_before_yesterday.date(),
                         date_data['date_obj'].date(), date_string)

    def test_should_not_assume_language_too_early(self):
        date_fixtures = [
            (u'07/07/2014', datetime(2014, 7, 7)),
            (u'07.jul.2014 | 12:52', datetime(2014, 7, 7)),
            (u'07.ago.2014 | 12:52', datetime(2014, 8, 7)),
            (u'07.feb.2014 | 12:52', datetime(2014, 2, 7)),
            (u'07.ene.2014 | 12:52', datetime(2014, 1, 7)),
        ]

        for date_string, correct_date in date_fixtures:
            date_data = self.parser.get_date_data(date_string)
            self.assertIsNotNone(date_data['date_obj'],
                                 "Could not get date for: %s" % date_string)
            self.check_equal(correct_date.date(),
                             date_data['date_obj'].date(), date_string)

    def test_should_enable_redetection_for_multiple_languages(self):
        date_fixtures = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'11 Marzo, 2014', datetime(2014, 3, 11)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
            (u'13 Setembro, 2014', datetime(2014, 9, 13)),
            (u'13 Março, 2014', datetime(2014, 3, 13)),
        ]
        parser = date.DateDataParser(allow_redetect_language=True)

        for date_string, correct_date in date_fixtures:
            date_data = parser.get_date_data(date_string)
            self.assertEqual(correct_date.date(), date_data['date_obj'].date())

    def test_should_parse_date_with_timezones_using_format(self):
        date_string = "2014/11/17 14:56 EDT"
        date_format = "%Y/%m/%d %H:%M EDT"
        expected = datetime(2014, 11, 17, 14, 56)
        date_data = self.parser.get_date_data(date_string, date_formats=[date_format])
        self.assertEqual('day', date_data['period'])
        self.assertEqual(expected, date_data['date_obj'])

    def test_should_parse_with_no_break_space_in_dates(self):
        date_string = "08-08-2014 18:29"
        expected = datetime(2014, 8, 8, 18, 29)
        date_data = self.parser.get_date_data(date_string)
        self.assertEqual(expected, date_data['date_obj'])

    @parameterized.expand([
        param(['ur', 'li']),
        param(['pk',]),
    ])
    def test_should_raise_error_when_unknown_language_given(self, shortnames):
        with self.assertRaisesRegexp(ValueError, '%r' % ', '.join(shortnames)):
            date.DateDataParser(languages=shortnames)


if __name__ == '__main__':
    unittest.main()
