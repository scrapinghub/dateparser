# coding: utf-8
from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta
from functools import wraps
from operator import attrgetter

from mock import patch, Mock
from nose_parameterized import parameterized, param

import dateparser.timezone_parser
from dateparser.date import DateDataParser, date_parser
from dateparser.date_parser import DateParser
from dateparser.languages import LanguageDataLoader
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages
from dateparser.conf import settings

from tests import BaseTestCase


class AutoDetectLanguageTest(unittest.TestCase):

    def setUp(self):
        self.parser = AutoDetectLanguage()

    def test_detect_language(self):
        self.assertItemsEqual(['es', 'pt'],
                              map(attrgetter('shortname'), self.parser.iterate_applicable_languages('11 abril 2010')))
        self.assertItemsEqual(['es'],
                              map(attrgetter('shortname'), self.parser.iterate_applicable_languages('11 junio 2010')))

    @unittest.skip('This test should only be testing detecting languages, not parsing them. Although tests '
                   'for parsing this dates should be created separately to not reduce the coverage')
    def test_should_reduce_possible_languages_and_reject_different(self):
        dates_in_spanish = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
        ]

        for date_string, correct_date in dates_in_spanish:
            parsed_date = self.parser.parse(date_string, None)
            self.assertEqual(correct_date.date(), parsed_date.date())

        with self.assertRaisesRegexp(ValueError, 'Invalid date'):
            portuguese_date = u'13 Setembro, 2014'
            self.parser.parse(portuguese_date, None)

    @unittest.skip('This test should only be testing detecting languages, not parsing them. Although tests '
                   'for parsing this dates should be created separately to not reduce the coverage')
    def test_should_accept_dates_in_different_languages(self):
        date_fixtures = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
            (u'13 Setembro, 2014', datetime(2014, 9, 13)),
        ]
        parser = AutoDetectLanguage(None, allow_redetection=True)

        for date_string, correct_date in date_fixtures:
            parsed_date = parser.parse(date_string, None)
            self.assertEqual(correct_date.date(), parsed_date.date())


class ExactLanguagesTest(unittest.TestCase):

    def test_force_setting_language(self):
        with self.assertRaisesRegexp(TypeError, 'takes exactly 2 arguments'):
            ExactLanguages()

        with self.assertRaisesRegexp(ValueError, 'cannot be None'):
            ExactLanguages(None)

    @unittest.skip('This test should only be testing detecting languages, not parsing them. Although tests '
                   'for parsing this dates should be created separatly to not reduce the coverage')
    def test_parse_date_in_exact_language(self):
        date_fixtures = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
            (u'13/03/2014', datetime(2014, 3, 13)),

            # TODO: make the following test pass
            # in this case, it should have detected spanish as the
            # language, and so it should use d/m/Y instead of d/m/Y
            # (u'11/03/2014', datetime(2014, 3, 11)),
        ]
        spanish = LanguageDataLoader().get_language('es')
        parser = ExactLanguages([spanish])

        for date_string, correct_date in date_fixtures:
            parsed_date = parser.parse(date_string, None)
            self.assertEqual(correct_date.date(), parsed_date.date())

        with self.assertRaisesRegexp(ValueError, 'Invalid date'):
            portuguese_date = u'13 Setembro, 2014'
            parser.parse(portuguese_date, None)


class TestDateParser(BaseTestCase):
    def setUp(self):
        super(TestDateParser, self).setUp()
        self.date_string = NotImplemented
        self.parser = NotImplemented
        self.result = NotImplemented
        self.date_parser = NotImplemented
        self.date_result = NotImplemented

    @parameterized.expand([
        # English dates
        param('[Sept] 04, 2014.', datetime(2014, 9, 4)),
        param('Tuesday Jul 22, 2014', datetime(2014, 7, 22)),
        param('10:04am EDT', datetime(2012, 11, 13, 14, 4)),
        param('Friday', datetime(2012, 11, 9)),
        param('November 19, 2014 at noon', datetime(2014, 11, 19, 12, 0)),
        param('December 13, 2014 at midnight', datetime(2014, 12, 13, 0, 0)),
        param('Nov 25 2014 10:17 pm EST', datetime(2014, 11, 26, 3, 17)),
        # French dates
        param('11 Mai 2014', datetime(2014, 5, 11)),
        param('dimanche, 11 Mai 2014', datetime(2014, 5, 11)),
        param('22 janvier 2015 \xe0 14h40', datetime(2015, 1, 22, 14, 40)),
        param('Dimanche 1er F\xe9vrier \xe0 21:24', datetime(2012, 2, 1, 21, 24)),
        # Spanish dates
        param('Martes 21 de Octubre de 2014', datetime(2014, 10, 21)),
        param('Miércoles 20 de Noviembre de 2013', datetime(2013, 11, 20)),
        param('12 de junio del 2012', datetime(2012, 6, 12)),
        # Dutch dates
        param('11 augustus 2014', datetime(2014, 8, 11)),
        param('14 januari 2014', datetime(2014, 1, 14)),
        param('vr jan 24, 2014 12:49', datetime(2014, 1, 24, 12, 49)),
        # Italian dates
        param('16 giu 2014', datetime(2014, 6, 16)),
        param('26 gennaio 2014', datetime(2014, 1, 26)),
        # Portuguese dates
        param('sexta-feira, 10 de junho de 2014 14:52', datetime(2014, 6, 10, 14, 52)),
        # Russian dates
        param('10 мая', datetime(2012, 5, 10)),  # forum.codenet.ru
        param('26 апреля', datetime(2012, 4, 26)),
        param('20 ноября 2013', datetime(2013, 11, 20)),
        param('28 октября 2014 в 07:54', datetime(2014, 10, 28, 7, 54)),
        param('13 января 2015 г. в 13:34', datetime(2015, 1, 13, 13, 34)),
        # Turkish dates
        param('08.Haziran.2014, 11:07', datetime(2014, 6, 8, 11, 7)),  # forum.andronova.net
        param('17.Şubat.2014, 17:51', datetime(2014, 2, 17, 17, 51)),
        param('14-Aralık-2012, 20:56', datetime(2012, 12, 14, 20, 56)),  # forum.ceviz.net
        # Romanian dates
        param('13 iunie 2013', datetime(2013, 6, 13)),
        param('14 aprilie 2014', datetime(2014, 4, 14)),
        param('18 martie 2012', datetime(2012, 3, 18)),
        # German dates
        param('21. Dezember 2013', datetime(2013, 12, 21)),
        param('19. Februar 2012', datetime(2012, 2, 19)),
        param('26. Juli 2014', datetime(2014, 7, 26)),
        param('18.10.14 um 22:56 Uhr', datetime(2014, 10, 18, 22, 56)),
        # Czech dates
        param('pon 16. čer 2014 10:07:43', datetime(2014, 6, 16, 10, 7, 43)),
        # Thai dates
        param('ธันวาคม 11, 2014, 08:55:08 PM', datetime(2014, 12, 11, 20, 55, 8)),
        param('22 พฤษภาคม 2012, 22:12', datetime(2012, 5, 22, 22, 12)),
        param('11 กุมภา 2020, 8:13 AM', datetime(2020, 2, 11, 8, 13)),
        param('1 เดือนตุลาคม 2005, 1:00 AM', datetime(2005, 10, 1, 1, 0)),
        param('11 ก.พ. 2020, 1:13 pm', datetime(2020, 2, 11, 13, 13)),
        # Vietnamese dates
        param('Thứ năm', datetime(2012, 11, 8)),  # Thursday
        param('Thứ sáu', datetime(2012, 11, 9)),  # Friday
        param('Tháng Mười Hai 29, 2013, 14:14', datetime(2013, 12, 29, 14, 14)),  # bpsosrcs.wordpress.com
        param('05 Tháng một 2015 - 03:54 AM', datetime(2015, 1, 5, 3, 54)),
        # Numeric dates
        param('06-17-2014', datetime(2014, 6, 17)),
        # Miscellaneous
        param('April 9, 2013 at 6:11 a.m.', datetime(2013, 4, 9, 6, 11)),
        param('Aug. 9, 2012 at 2:57 p.m.', datetime(2012, 8, 9, 14, 57)),
        param('December 10, 2014, 11:02:21 pm', datetime(2014, 12, 10, 23, 2, 21)),
        param('vendredi, d\xe9cembre 5 2014.', datetime(2014, 12, 5, 0, 0)),
        param('le 08 D\xe9c 2014 15:11', datetime(2014, 12, 8, 15, 11)),
        param('Le 11 D\xe9cembre 2014 \xe0 09:00', datetime(2014, 12, 11, 9, 0)),
        param('f\xe9v 15, 2013', datetime(2013, 2, 15, 0, 0)),
        param('8:25 a.m. Dec. 12, 2014', datetime(2014, 12, 12, 8, 25)),
        param('2:21 p.m., December 11, 2014', datetime(2014, 12, 11, 14, 21)),
        param('11. 12. 2014, 08:45:39', datetime(2014, 11, 12, 8, 45, 39)),
        param('Fri, 12 Dec 2014 10:55:50', datetime(2014, 12, 12, 10, 55, 50)),
        param('čtv 14. lis 2013 12:38:43', datetime(2013, 11, 14, 12, 38, 43)),
        param('09 августа 2012', datetime(2012, 8, 9, 0, 0)),
        param('20 Mar 2013 10h11', datetime(2013, 3, 20, 10, 11)),
        param('10:06am Dec 11, 2014', datetime(2014, 12, 11, 10, 6)),
        param('19 February 2013 year 09:10', datetime(2013, 2, 19, 9, 10)),
    ])
    def test_dates_parsing(self, date_string, expected):
        self.given_utcnow(datetime(2012, 11, 13))  # Tuesday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_period_is('day')
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('Sep 03 2014 | 4:32 pm EDT', datetime(2014, 9, 3, 21, 32)),
        param('17th October, 2034 @ 01:08 am PDT', datetime(2034, 10, 17, 9, 8)),
        param('15 May 2004 23:24 EDT', datetime(2004, 5, 16, 4, 24)),
        param('15 May 2004', datetime(2004, 5, 15, 0, 0)),
        ])
    def test_parsing_with_time_zones(self, date_string, expected):
        self.given_local_tz_offset(+1)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_period_is('day')
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param(''),
        param('invalid date string'),
        param('Aug 7, 2014Aug 7, 2014'),
    ])
    def test_dates_not_parsed(self, date_string):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_not_parsed()

    @parameterized.expand([
        param('10 December', datetime(2014, 12, 10)),
        param('March', datetime(2014, 3, 15)),
        param('Friday', datetime(2015, 2, 13)),
        param('Monday', datetime(2015, 2, 9)),
        param('10:00PM', datetime(2015, 2, 14, 22, 00)),
        param('16:10', datetime(2015, 2, 14, 16, 10)),
        param('14:05', datetime(2015, 2, 15, 14, 5)),
    ])
    def test_preferably_past_dates(self, date_string, expected):
        self.given_configuration('PREFER_DATES_FROM', 'past')
        self.given_utcnow(datetime(2015, 2, 15, 15, 30))  # Sunday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('10 December', datetime(2015, 12, 10)),
        param('March', datetime(2015, 3, 15)),
        param('Friday', datetime(2015, 2, 20)),
        param('Monday', datetime(2015, 2, 16)),
        param('10:00PM', datetime(2015, 2, 15, 22, 00)),
        param('16:10', datetime(2015, 2, 15, 16, 10)),
        param('14:05', datetime(2015, 2, 16, 14, 5)),
    ])
    def test_preferably_future_dates(self, date_string, expected):
        self.given_configuration('PREFER_DATES_FROM', 'future')
        self.given_utcnow(datetime(2015, 2, 15, 15, 30))  # Sunday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('10 December', datetime(2015, 12, 10)),
        param('March', datetime(2015, 3, 15)),
        param('Friday', datetime(2015, 2, 13)),
        param('10:00PM', datetime(2015, 2, 15, 22, 00)),
        param('16:10', datetime(2015, 2, 15, 16, 10)),
        param('14:05', datetime(2015, 2, 15, 14, 5)),
    ])
    def test_dates_without_preference(self, date_string, expected):
        self.given_configuration('PREFER_DATES_FROM', 'current_period')
        self.given_utcnow(datetime(2015, 2, 15, 15, 30))  # Sunday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('February 2015', today=datetime(2015, 1, 31), expected=datetime(2015, 2, 28)),
        param('February 2012', today=datetime(2015, 1, 31), expected=datetime(2012, 2, 29)),
        param('March 2015', today=datetime(2015, 1, 25), expected=datetime(2015, 3, 25)),
        param('April 2015', today=datetime(2015, 1, 31), expected=datetime(2015, 4, 30)),
        param('April 2015', today=datetime(2015, 2, 28), expected=datetime(2015, 4, 28)),
        param('December 2014', today=datetime(2015, 2, 15), expected=datetime(2014, 12, 15)),
    ])
    def test_dates_with_day_missing_prefering_current_day_of_month(self, date_string, today=None, expected=None):
        self.given_configuration('PREFER_DAY_OF_MONTH', 'current')
        self.given_utcnow(today)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('February 2015', today=datetime(2015, 1, 1), expected=datetime(2015, 2, 28)),
        param('February 2012', today=datetime(2015, 1, 1), expected=datetime(2012, 2, 29)),
        param('March 2015', today=datetime(2015, 1, 25), expected=datetime(2015, 3, 31)),
        param('April 2015', today=datetime(2015, 1, 15), expected=datetime(2015, 4, 30)),
        param('April 2015', today=datetime(2015, 2, 28), expected=datetime(2015, 4, 30)),
        param('December 2014', today=datetime(2015, 2, 15), expected=datetime(2014, 12, 31)),
    ])
    def test_dates_with_day_missing_prefering_last_day_of_month(self, date_string, today=None, expected=None):
        self.given_configuration('PREFER_DAY_OF_MONTH', 'last')
        self.given_utcnow(today)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('February 2015', today=datetime(2015, 1, 8), expected=datetime(2015, 2, 1)),
        param('February 2012', today=datetime(2015, 1, 7), expected=datetime(2012, 2, 1)),
        param('March 2015', today=datetime(2015, 1, 25), expected=datetime(2015, 3, 1)),
        param('April 2015', today=datetime(2015, 1, 15), expected=datetime(2015, 4, 1)),
        param('April 2015', today=datetime(2015, 2, 28), expected=datetime(2015, 4, 1)),
        param('December 2014', today=datetime(2015, 2, 15), expected=datetime(2014, 12, 1)),
    ])
    def test_dates_with_day_missing_prefering_first_day_of_month(self, date_string, today=None, expected=None):
        self.given_configuration('PREFER_DAY_OF_MONTH', 'first')
        self.given_utcnow(today)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param(prefer_day_of_month='current'),
        param(prefer_day_of_month='last'),
        param(prefer_day_of_month='first'),
    ])
    def test_that_day_preference_does_not_affect_dates_with_explicit_day(self, prefer_day_of_month=None):
        self.given_configuration('PREFER_DAY_OF_MONTH', prefer_day_of_month)
        self.given_utcnow(datetime(2015, 2, 12))
        self.given_parser()
        self.given_date_string('24 April 2012')
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(datetime(2012, 4, 24))

    @parameterized.expand([
        param('29 February 2015'),
        param('32 January 2015'),
        param('31 April 2015'),
        param('31 June 2015'),
        param('31 September 2015'),
    ])
    def test_error_should_be_raised_for_invalid_dates_with_too_large_day_number(self, date_string):
        with self.assertRaisesRegexp(ValueError, 'Day not in range for month'):
            DateParser().parse(date_string)

    @parameterized.expand([
        param('10 December', expected=datetime(2015, 12, 10), period='day'),
        param('March', expected=datetime(2015, 3, 15), period='month'),
        param('April', expected=datetime(2015, 4, 15), period='month'),
        param('December', expected=datetime(2015, 12, 15), period='month'),
        param('Friday', expected=datetime(2015, 2, 13), period='day'),
        param('Monday', expected=datetime(2015, 2, 9), period='day'),
        param('10:00PM', expected=datetime(2015, 2, 15, 22, 00), period='day'),
        param('16:10', expected=datetime(2015, 2, 15, 16, 10), period='day'),
        param('2014', expected=datetime(2014, 2, 15), period='year'),
        param('2008', expected=datetime(2008, 2, 15), period='year'),
    ])
    def test_extracted_period(self, date_string, expected=None, period=None):
        self.given_utcnow(datetime(2015, 2, 15, 15, 30))  # Sunday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)
        self.then_period_is(period)

    def given_utcnow(self, now):
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=now)
        self.add_patch(patch('dateparser.date_parser.datetime', new=datetime_mock))

    def given_local_tz_offset(self, offset):
        self.add_patch(
            patch.object(dateparser.timezone_parser,
                         'local_tz_offset',
                         new=timedelta(seconds=3600 * offset))
        )

    def given_date_string(self, date_string):
        self.date_string = date_string

    def given_parser(self):
        def collecting_get_date_data(parse):
            @wraps(parse)
            def wrapped(date_string):
                self.date_result = parse(date_string)
                return self.date_result
            return wrapped
        self.add_patch(patch.object(date_parser,
                                    'parse',
                                    collecting_get_date_data(date_parser.parse)))

        self.date_parser = Mock(wraps=date_parser)
        self.add_patch(patch('dateparser.date.date_parser', new=self.date_parser))
        self.parser = DateDataParser()

    def given_configuration(self, key, value):
        self.add_patch(patch.object(settings, key, new=value))

    def when_date_is_parsed(self):
        self.result = self.parser.get_date_data(self.date_string)

    def then_period_is(self, period):
        self.assertEqual(period, self.result['period'])

    def then_date_obj_exactly_is(self, expected):
        self.assertEqual(expected, self.result['date_obj'])

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result['date_obj'], '"%s" should not be parsed' % self.date_string)

    def then_date_was_parsed_by_date_parser(self):
        self.assertEqual(self.result['date_obj'], self.date_result[0])


@unittest.skip('There are mostly old language detection tests left. New tests should be written.')
class TestDateParser_(BaseTestCase):

    @unittest.skip('DateParser not using formats anymore. Should be tested separately.')
    def test_it_dates_with_format(self):
        parser = DateParser()
        date = parser.parse('14 giu 13', date_format='%y %B %d')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 13)

        date = parser.parse('14_luglio_15', date_format='%y_%b_%d')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 7)
        self.assertEqual(date.day, 15)

        date = parser.parse('14_LUGLIO_15', date_format='%y_%b_%d')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 7)
        self.assertEqual(date.day, 15)

    def test_premature_detection(self):
        invalid_date_string = '24h ago'  # 'ago' is shortened august in some languages
        with self.assertRaisesRegexp(ValueError, 'Invalid date: {}'.format(invalid_date_string)):
            DateParser().parse(invalid_date_string)

    def test_should_not_assume_language_prematurely(self):
        dp = DateParser()
        date_fixtures = [
            (u'07/07/2014', datetime(2014, 7, 7)),
            (u'07.ago.2014 | 12:52', datetime(2014, 8, 7)),
            (u'07.jul.2014 | 12:52', datetime(2014, 7, 7)),
            (u'07.feb.2014 | 12:52', datetime(2014, 2, 7)),
            (u'07.ene.2014 | 12:52', datetime(2014, 1, 7)),
        ]

        for date_string, correct_date in date_fixtures:
            self.assertEqual(correct_date.date(), dp.parse(date_string).date())

    def test_should_not_allow_multiple_languages_by_default(self):
        dates_in_spanish = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'11 Marzo, 2014', datetime(2014, 3, 11)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
        ]
        dp = DateParser()

        for date_string, correct_date in dates_in_spanish:
            parsed_date = dp.parse(date_string)
            self.assertEqual(correct_date.date(), parsed_date.date())

        with self.assertRaisesRegexp(ValueError, 'Invalid date'):
            portuguese_date = u'13 Setembro, 2014'
            dp.parse(portuguese_date)

    def test_should_enable_redetection_for_multiple_languages(self):
        dates_fixture = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'11 Marzo, 2014', datetime(2014, 3, 11)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
            (u'13 Setembro, 2014', datetime(2014, 9, 13)),
            (u'13 Março, 2014', datetime(2014, 3, 13)),
        ]
        dp = DateParser(allow_redetect_language=True)

        for date_string, correct_date in dates_fixture:
            parsed_date = dp.parse(date_string)
            self.assertEqual(correct_date.date(), parsed_date.date())

    def test_finding_no_language_when_not_seen_before_should_raise_error(self):
        """ This test depends on the defined order of the languages and needs to be rewritten """
        dp = DateParser()
        self.assertEqual(datetime(2014, 8, 13).date(),
                         dp.parse("13 Srpen, 2014").date())

        with self.assertRaises(ValueError):
            dp.parse('11 Ağustos, 2014')

    def test_finding_no_language_when_enabled_should_redetect(self):
        dp = DateParser(allow_redetect_language=True)
        self.assertEqual(datetime(2014, 8, 13).date(),
                         dp.parse('13 Ago, 2014').date())

        self.assertEqual(datetime(2014, 8, 11).date(),
                         dp.parse(u'11 Ağustos, 2014').date())

    def test_finding_no_language_should_work_for_numeric_dates(self):
        dp = DateParser()
        self.assertEqual(datetime(2014, 8, 13).date(),
                         dp.parse('13 Ago, 2014').date())

        parsed_date = dp.parse(u'13/08/2014')
        self.assertEqual(datetime(2014, 8, 13).date(), parsed_date.date())


if __name__ == '__main__':
    unittest.main()
