#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from dateparser import date
from mock import Mock, patch
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import unittest


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


class ParseDateWithFormats(unittest.TestCase):

    def test_shouldnt_parse_invalid_date(self):
        self.assertIsNone(date.parse_with_formats('yesterday', ['%Y-%m-%d']))

    def test_should_parse_date(self):
        result = date.parse_with_formats('25-03-14', ['%d-%m-%y'])
        self.assertEquals(datetime(2014, 3, 25).date(), result.date())

    def test_should_use_current_date_for_dates_without_day(self):
        twelfth = datetime(2014, 8, 12)
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=twelfth)

        with patch('dateparser.date_parser.datetime', new=datetime_mock):
            dt_data = date.parse_with_formats('August 2014', ['%B %Y'], final_call=True)

        self.assertIsNotNone(dt_data)
        self.assertEquals('month', dt_data['period'])
        self.assertEquals(datetime(2014, 8, 31).date(), dt_data['date_obj'].date())

        twelfth = datetime(2014, 2, 12)
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=twelfth)

        with patch('dateparser.date_parser.datetime', new=datetime_mock):
            dt_data = date.parse_with_formats('February 2014', ['%B %Y'], final_call=True)

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

    def test_should_return_today(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        for date_string in ['today', 'Today', 'TODAY', 'Сегодня', 'Hoje', 'Oggi']:
            date_data = self.parser.get_date_data(date_string)
            self.assertIsNotNone(date_data['date_obj'])
            self.assertEqual(today.date(), date_data['date_obj'].date())

    def test_should_return_yesterday(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - relativedelta(days=1)

        for date_string in ['yesterday', ' Yesterday \n', 'Ontem', 'Ieri']:
            date_data = self.parser.get_date_data(date_string)
            self.assertIsNotNone(date_data['date_obj'],
                                 "could not parse date from: %s" % date_string)
            self.check_equal(yesterday.date(),
                             date_data['date_obj'].date(), date_string)

    def test_should_return_day_before_yesterday(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        day_before_yesterday = today - relativedelta(days=2)

        for date_string in ['the day before yesterday', 'The DAY before Yesterday',
                            'Anteontem', 'Avant-hier']:
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


if __name__ == '__main__':
    unittest.main()
