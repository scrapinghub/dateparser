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


class DateRangeTest(BaseTestCase):
    def setUp(self):
        super(DateRangeTest, self).setUp()

    @parameterized.expand([
        param(begin=datetime(2014, 6, 15), end=datetime(2014, 6, 25), expected_length=10)
    ])
    def test_date_range(self, begin, end, expected_length):
        self.given_period_start(begin)
        self.given_period_end(end)
        self.when_date_range_generated()
        self.then_range_length_is(expected_length)
        self.then_all_dates_from_beginning_to_end_are_present_in_range()
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
        self.given_period_start(begin)
        self.given_period_end(end)
        self.given_period_size(months=1)
        self.when_month_range_generated()
        self.then_month_expected(expected_months)

    @parameterized.expand([
        param(begin=datetime(2014, 6, 15), end=datetime(2014, 6, 25))
    ])
    def test_should_reject_easily_mistaken_dateutil_arguments(self, begin, end):
        self.given_period_start(begin)
        self.given_period_end(end)
        self.then_should_reject_easily_mistaken_dateutil_arguments()

    def given_period_start(self, begin):
        self.period_start = begin

    def given_period_end(self, end):
        self.period_end = end

    def when_date_range_generated(self):
        self.range = list(date.date_range(self.period_start, self.period_end))

    def given_period_size(self, **params):
        self.period_size = params

    def when_month_range_generated(self):
        self.generated_months = list(date.date_range(self.period_start, self.period_end, **self.period_size))

    def then_month_expected(self, expected):
        self.assertEqual(expected,
                         [(d.year, d.month) for d in self.generated_months])

    def then_range_length_is(self, expected_length):
        self.assertEqual(expected_length, len(self.range))

    def then_all_dates_from_beginning_to_end_are_present_in_range(self):
        date_under_test = self.period_start
        while date_under_test < self.period_end:
            self.assertIn(date_under_test, self.range)
            date_under_test += timedelta(days=1)

    def then_range_is_in_ascending_order(self):
        for i in xrange(len(self.range) - 1):
            self.assertLess(self.range[i], self.range[i + 1])

    def then_should_reject_easily_mistaken_dateutil_arguments(self):
        with self.assertRaisesRegexp(ValueError, "Invalid argument"):
            date.date_range(self.period_start, self.period_end, month=1).next()

        with self.assertRaisesRegexp(ValueError, "Invalid argument"):
            date.date_range(self.period_start, self.period_end, day=1).next()


class GetIntersectingPeriodsTest(BaseTestCase):
    def setUp(self):
        super(GetIntersectingPeriodsTest, self).setUp()
        self.intersected_dates = NotImplemented
        self.expected_results = NotImplemented

    @parameterized.expand([
        param(low=datetime(2014, 6, 15), high=datetime(2014, 6, 16),
              dates=list(date.get_intersecting_periods(datetime(2014, 6, 15), datetime(2014, 6, 16))))
    ])
    def test_date_arguments_and_date_range_with_default_post_days(self, low, high, dates):
        self.given_period_low(low)
        self.given_period_high(high)
        self.when_date_intersecting_generated(dates)
        self.then_date_period_and_intersected_dates_should_equal()
        self.then_date_arguments_and_date_range_length_should_equal()

    @parameterized.expand([
        param(low=datetime(2014, 4, 15),
              high=datetime(2014, 6, 25),
              period='month',
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1), datetime(2014, 6, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 5, 5),
              period='month',
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1)]),
        param(low=datetime(2014, 4, 5),
              high=datetime(2014, 4, 25),
              period='month',
              expected_results=[datetime(2014, 4, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 6, 5),
              period='month',
              expected_results=[datetime(2014, 4, 1), datetime(2014, 5, 1), datetime(2014, 6, 1)]),
        param(low=datetime(2014, 4, 25),
              high=datetime(2014, 4, 25),
              period='month',
              expected_results=[]),
        param(low=datetime(2014, 12, 31),
              high=datetime(2015, 1, 1),
              period='month',
              expected_results=[datetime(2014, 12, 1)]),
    ])
    def test_should_one_date_for_each_month(self, low, high, expected_results, period):
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period(period)
        self.given_expected_results(expected_results)
        self.when_should_one_date_for_each_month()
        self.then_should_one_date_for_each_month()

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
        self.when_should_one_date_for_each_month()
        self.then_should_one_date_for_each_month()

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
        self.given_period_low(datetime(2014, 6, 15))
        self.given_period(datetime(2014, 6, 25))
        self.given_invalid_period(invalid_period)
        self.then_should_reject_easily_mistaken_dateutil_arguments()

    @parameterized.expand([
        param(low=datetime(2014, 4, 15), high=datetime(2014, 4, 14), period='month'),
        param(low=datetime(2014, 4, 25), high=datetime(2014, 4, 25), period='month'),
    ])
    def test_empty_period(self, low, high, period):
        self.given_period_low(low)
        self.given_period_high(high)
        self.given_period(period)
        self.when_empty_period()

    def given_expected_results(self, expected_results):
        self.expected_results = expected_results

    def given_period_low(self, low):
        self.period_low = low

    def given_invalid_period(self, invalid_period):
        self.invalid_period = invalid_period

    def given_period_high(self, high):
        self.period_high = high

    def given_period(self, period):
        self.period = period

    def when_date_intersecting_generated(self, dates):
        self.intersected_dates = dates

    def then_date_arguments_and_date_range_length_should_equal(self):
        self.assertEquals(1, len(self.intersected_dates))

    def then_date_period_and_intersected_dates_should_equal(self):
        self.assertEquals(self.period_low, self.intersected_dates[0])

    def when_should_one_date_for_each_month(self):
        self.intersected_dates = list(date.get_intersecting_periods(
            self.period_low, self.period_high, period=self.period))

    def when_empty_period(self):
        self.intersected_dates = list(date.get_intersecting_periods(
            self.period_low, self.period_high, period=self.period))

    def then_should_one_date_for_each_month(self):
        self.assertEquals(self.expected_results, self.intersected_dates)

    def then_empty_period(self):
        self.assertEquals([], self.intersected_dates)

    def then_should_reject_easily_mistaken_dateutil_arguments(self):
        with self.assertRaisesRegexp(ValueError, "Invalid period: {}".format(self.invalid_period)):
            date.get_intersecting_periods(self.period_low, self.period, period=self.invalid_period).next()


class ParseDateWithFormats(BaseTestCase):
    def setUp(self):
        super(ParseDateWithFormats, self).setUp()
        self.dt_data = NotImplemented

    def test_shouldnt_parse_invalid_date(self):
        self.then_shouldnt_parse_invalid_date()

    def test_should_parse_date(self):
        self.when_should_parse_date()
        self.then_should_parse_date()

    def test_should_use_current_year_for_dates_without_year(self):
        self.given_current_year()
        self.when_should_use_current_year_for_dates_without_year()
        self.then_should_use_current_year_for_dates_without_year()

    def test_should_use_current_date_for_dates_without_day(self):
        self.given_date(datetime(2014, 8, 31).date())
        self.given_twelfth_first()
        self.given_datetime_mock_first()
        self.when_patch_first()
        self.then_current_year_for_dates_without_year_is_not_none()
        self.then_period_for_current_year_is_equal()
        self.then_check_if_dates_are_equal()
        self.given_date(datetime(2014, 2, 28).date())
        self.given_twelfth_second()
        self.given_datetime_mock_second()
        self.when_patch_second()
        self.then_current_year_for_dates_without_year_is_not_none()
        self.then_period_for_current_year_is_equal()
        self.then_check_if_dates_are_equal()

    def given_current_year(self):
        self.current_year = datetime.today().year

    def given_date(self, date_obj):
        self.date_obj = date_obj

    def when_should_use_current_year_for_dates_without_year(self):
        self.result = date.parse_with_formats('09.16', ["%m.%d"])

    def then_should_use_current_year_for_dates_without_year(self):
        self.assertEquals(datetime(self.current_year, 9, 16).date(), self.result['date_obj'].date())

    def when_should_parse_date(self):
        self.result = date.parse_with_formats('25-03-14', ['%d-%m-%y'])

    def then_should_parse_date(self):
        self.assertEquals(datetime(2014, 3, 25).date(), self.result['date_obj'].date())

    def then_shouldnt_parse_invalid_date(self):
        self.assertIsNone(date.parse_with_formats('yesterday', ['%Y-%m-%d'])['date_obj'])

    def given_twelfth_first(self):
        self.twelfth_first = datetime(2014, 8, 12)

    def given_twelfth_second(self):
        self.twelfth_second = datetime(2014, 2, 12)

    def given_datetime_mock_first(self):
        self.datetime_mock = Mock(wraps=datetime)
        self.datetime_mock.utcnow = Mock(return_value=self.twelfth_first)

    def given_datetime_mock_second(self):
        self.datetime_mock = Mock(wraps=datetime)
        self.datetime_mock.utcnow = Mock(return_value=self.twelfth_second)

    def when_patch_first(self):
        with patch('dateparser.date_parser.datetime', new=self.datetime_mock):
            self.dt_data = date.parse_with_formats('August 2014', ['%B %Y'])

    def when_patch_second(self):
        with patch('dateparser.date_parser.datetime', new=self.datetime_mock):
            self.dt_data = date.parse_with_formats('February 2014', ['%B %Y'])

    def then_current_year_for_dates_without_year_is_not_none(self):
        self.assertIsNotNone(self.dt_data)

    def then_period_for_current_year_is_equal(self):
        self.assertEquals('month', self.dt_data['period'])

    def then_check_if_dates_are_equal(self):
        self.assertEquals(self.date_obj, self.dt_data['date_obj'].date())


class DateDataParserTest(BaseTestCase):
    def setUp(self):
        super(DateDataParserTest, self).setUp()
        self.parser = date.DateDataParser()
        self.date_format = NotImplemented

    def check_equal(self, first, second, date_string):
        self.assertEqual(first, second, "%s != %s for date_string:  '%s'" %
                         (repr(first), repr(second), date_string))

    @parameterized.expand([
        param(date_string='10:04am EDT',
              today=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    ])
    def test_time_in_today_should_return_today(self, date_string, today):
        self.given_date_string(date_string)
        self.given_today(today)
        self.when_date_data()
        self.then_time_in_today_should_return_today_is_not_none()
        self.then_time_in_today_should_return_today_is_equal()

    @parameterized.expand([
        param('today'),
        param('Today'),
        param('TODAY'),
        param('Сегодня'),
        param('Hoje'),
        param('Oggi'),
    ])
    def test_should_return_today(self, date_string):
        self.given_today(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
        self.given_date_string(date_string)
        self.when_date_data()
        self.then_should_return_today_is_not_none()
        self.then_should_return_today_is_equal()

    @parameterized.expand([
        param('yesterday'),
        param(' Yesterday \n'),
        param('Ontem'),
        param('Ieri'),
    ])
    def test_should_return_yesterday(self, date_string):
        self.given_today(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
        self.given_date_string(date_string)
        self.given_yesterday()
        self.when_date_data()
        self.then_should_return_yesterday_is_not_none()
        self.then_should_return_yesterday_is_equal()

    @parameterized.expand([
        param('the day before yesterday'),
        param('The DAY before Yesterday'),
        param('Anteontem'),
        param('Avant-hier'),
    ])
    def test_should_return_day_before_yesterday(self, date_string):
        self.given_date_string(date_string)
        self.given_today(datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
        self.given_day_before_yesterday()
        self.when_date_data()
        self.then_should_return_day_before_yesterday_is_not_none()
        self.then_should_return_day_before_yesterday_is_equal()

    @parameterized.expand([
        param(u'07/07/2014', datetime(2014, 7, 7)),
        param(u'07.jul.2014 | 12:52', datetime(2014, 7, 7)),
        param(u'07.ago.2014 | 12:52', datetime(2014, 8, 7)),
        param(u'07.feb.2014 | 12:52', datetime(2014, 2, 7)),
        param(u'07.ene.2014 | 12:52', datetime(2014, 1, 7)),
    ])
    def test_should_not_assume_language_too_early(self, date_string, correct_date):
        self.given_date_string(date_string)
        self.given_correct_date(correct_date)
        self.when_date_data()
        self.then_should_not_assume_language_too_early_is_not_none()
        self.then_should_not_assume_language_too_early_is_equal()

    @parameterized.expand([
        param(u'13 Ago, 2014', datetime(2014, 8, 13)),
        param(u'11 Marzo, 2014', datetime(2014, 3, 11)),
        param(u'13 Septiembre, 2014', datetime(2014, 9, 13)),
        param(u'13 Setembro, 2014', datetime(2014, 9, 13)),
        param(u'13 Março, 2014', datetime(2014, 3, 13)),
    ])
    def test_should_enable_redetection_for_multiple_languages(self, date_string, correct_date):
        self.given_different_parser()
        self.given_date_string(date_string)
        self.given_correct_date(correct_date)
        self.when_date_data()
        self.then_should_enable_redetection_for_multiple_languages()

    def test_should_parse_date_with_timezones_using_format(self):
        self.given_date_string("2014/11/17 14:56 EDT")
        self.given_date_format("%Y/%m/%d %H:%M EDT")
        self.given_expected_date(datetime(2014, 11, 17, 14, 56))
        self.when_should_parse_date_with_timezones_using_format()
        self.then_should_parse_date_with_period()
        self.then_should_parse_date_with_expected_date()

    @parameterized.expand([
        param(['ur', 'li']),
        param(['pk', ]),
    ])
    def test_should_raise_error_when_unknown_language_given(self, shortnames):
        with self.assertRaisesRegexp(ValueError, '%r' % ', '.join(shortnames)):
            date.DateDataParser(languages=shortnames)

    def given_different_parser(self):
        self.parser = date.DateDataParser(allow_redetect_language=True)

    def given_date_string(self, date_string):
        self.date_string = date_string

    def given_date_format(self, date_format):
        self.date_format = date_format

    def given_correct_date(self, correct_date):
        self.correct_date = correct_date

    def when_date_data(self):
        self.date_data = self.parser.get_date_data(self.date_string)

    def given_expected_date(self, expected_date):
        self.expected_date = expected_date

    def given_today(self, today):
        self.today = today

    def given_yesterday(self):
        self.yesterday = self.today - relativedelta(days=1)

    def given_day_before_yesterday(self):
        self.day_before_yesterday = self.today - relativedelta(days=2)

    def then_time_in_today_should_return_today_is_not_none(self):
        self.assertIsNotNone(self.date_data['date_obj'])

    def then_time_in_today_should_return_today_is_equal(self):
        self.assertEqual(self.today.date(), self.date_data['date_obj'].date())

    def then_should_return_today_is_not_none(self):
        self.assertIsNotNone(self.date_data['date_obj'])

    def then_should_return_today_is_equal(self):
        self.assertEqual(self.today.date(), self.date_data['date_obj'].date())

    def then_should_return_yesterday_is_not_none(self):
        self.assertIsNotNone(self.date_data['date_obj'],
                             "could not parse date from: %s" % self.date_string)

    def then_should_return_yesterday_is_equal(self):
        self.check_equal(self.yesterday.date(),
                         self.date_data['date_obj'].date(), self.date_string)

    def then_should_return_day_before_yesterday_is_not_none(self):
        self.assertIsNotNone(self.date_data['date_obj'])

    def then_should_return_day_before_yesterday_is_equal(self):
        self.check_equal(self.day_before_yesterday.date(),
                         self.date_data['date_obj'].date(), self.date_string)

    def then_should_not_assume_language_too_early_is_not_none(self):
        self.assertIsNotNone(self.date_data['date_obj'],
                             "Could not get date for: %s" % self.date_string)

    def then_should_not_assume_language_too_early_is_equal(self):
        self.check_equal(self.correct_date.date(),
                         self.date_data['date_obj'].date(), self.date_string)

    def then_should_enable_redetection_for_multiple_languages(self):
        self.assertEqual(self.correct_date.date(), self.date_data['date_obj'].date())

    def when_should_parse_date_with_timezones_using_format(self):
        self.date_data = self.parser.get_date_data(self.date_string, date_formats=[self.date_format])

    def then_should_parse_date_with_period(self):
        self.assertEqual('day', self.date_data['period'])

    def then_should_parse_date_with_expected_date(self):
        self.assertEqual(self.expected_date, self.date_data['date_obj'])


if __name__ == '__main__':
    unittest.main()
