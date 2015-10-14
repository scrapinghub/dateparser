# coding: utf-8
from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta
from functools import wraps
from operator import attrgetter

from mock import patch, Mock
from nose_parameterized import parameterized, param

import dateparser.timezone_parser
import six
from dateparser.date import DateDataParser, date_parser
from dateparser.date_parser import DateParser
from dateparser.languages import default_language_loader
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages
from dateparser.conf import settings

from tests import BaseTestCase


class AutoDetectLanguageTest(BaseTestCase):
    def setUp(self):
        super(AutoDetectLanguageTest, self).setUp()

        # Just a known subset so we can rely on test outcomes. Feel free to add, but not exclude or change order.
        self.known_languages = ['en', 'fr', 'es', 'pt', 'ru', 'tr', 'cz']

        self.parser = NotImplemented
        self.detected_languages = NotImplemented

    @parameterized.expand([
        param(date_strings=["11 abril 2010"], expected_languages=['es', 'pt']),
        param(date_strings=["11 junio 2010"], expected_languages=['es']),
        param(date_strings=["13 Ago, 2014", "13 Septiembre, 2014"], expected_languages=['es']),
    ])
    def test_detect_languages(self, date_strings, expected_languages):
        self.given_parser(languages=self.known_languages)
        self.when_all_languages_are_detected(date_strings)
        self.then_detected_languages_are(expected_languages)

    @parameterized.expand([
        param(date_strings=["11 abril 2010"], expected_language='es'),
        param(date_strings=["11 junio 2010"], expected_language='es'),
        param(date_strings=["13 Ago, 2014", "13 Septiembre, 2014"], expected_language='es'),
    ])
    def test_exclude_ineligible_languages_with_modify(self, date_strings, expected_language):
        self.given_parser(languages=self.known_languages)
        self.when_one_language_is_detected(date_strings, modify=True)
        self.then_detected_languages_are([expected_language])
        self.then_parser_languages_are(self.known_languages[self.known_languages.index(expected_language):])

    @parameterized.expand([
        param(date_strings=["11 abril 2010"], expected_language='es'),
        param(date_strings=["11 junio 2010"], expected_language='es'),
        param(date_strings=["13 Ago, 2014", "13 Septiembre, 2014"], expected_language='es'),
    ])
    def test_do_not_exclude_ineligible_languages_without_modify(self, date_strings, expected_language):
        self.given_parser(languages=self.known_languages)
        self.when_one_language_is_detected(date_strings, modify=False)
        self.then_detected_languages_are([expected_language])
        self.then_parser_languages_are(self.known_languages)

    @parameterized.expand([
        param(date_strings=["11 abril 2010"], expected_languages=['es', 'pt']),
        param(date_strings=["11 junio 2010"], expected_languages=['es']),
        param(date_strings=["13 Ago, 2014", "13 Septiembre, 2014"], expected_languages=['es']),
        param(date_strings=["13 Srpen, 2014"], expected_languages=['cz']),
    ])
    def test_do_not_exclude_ineligible_languages_when_all_ineligible(self, date_strings, expected_languages):
        self.given_parser(languages=self.known_languages)
        self.when_all_languages_are_detected(date_strings, modify=True)
        self.then_detected_languages_are(expected_languages)
        self.then_parser_languages_are(self.known_languages)

    @parameterized.expand([
        param(language='es', date_strings=["13 Setembro, 2014"]),
        param(language='cz', date_strings=["'11 Ağustos, 2014'"]),
    ])
    def test_reject_dates_in_other_languages_without_redetection(self, language, date_strings):
        self.given_parser(languages=self.known_languages)
        self.given_parser_languages_are([language])
        self.when_all_languages_are_detected(date_strings)
        self.then_detected_languages_are([])

    @parameterized.expand([
        param(detected_languages=['es'], date_strings=['13 Juillet, 2014'], expected_languages=['fr']),
        param(detected_languages=['es'], date_strings=['11 Ağustos, 2014'], expected_languages=['tr']),
    ])
    def test_accept_dates_in_other_languages_with_redetection_enabled(
        self, detected_languages, date_strings, expected_languages
    ):
        self.given_parser(languages=self.known_languages, allow_redetection=True)
        self.given_parser_languages_are(detected_languages)
        self.when_all_languages_are_detected(date_strings)
        self.then_detected_languages_are(expected_languages)

    def test_accept_numeric_dates_without_redetection(self,):
        self.given_parser(languages=self.known_languages)
        self.given_parser_languages_are(['es'])
        self.when_all_languages_are_detected(['13/08/2014'])
        self.then_detected_languages_are(['es'])

    def given_parser(self, languages=None, allow_redetection=False):
        if languages is not None:
            language_map = default_language_loader.get_language_map()
            languages = [language_map[language]
                         for language in languages]
        self.parser = AutoDetectLanguage(languages, allow_redetection=allow_redetection)

    def given_parser_languages_are(self, languages):
        language_map = default_language_loader.get_language_map()
        self.parser.languages = [language_map[language]
                                 for language in languages]

    def when_all_languages_are_detected(self, date_strings, modify=False):
        assert not isinstance(date_strings, six.string_types)
        for date_string in date_strings:
            detected_languages = list(self.parser.iterate_applicable_languages(date_string, modify=modify))
        self.detected_languages = detected_languages

    def when_one_language_is_detected(self, date_strings, modify=False):
        for date_string in date_strings:
            detected_language = next(self.parser.iterate_applicable_languages(date_string, modify=modify))
        self.detected_languages = [detected_language]

    def then_detected_languages_are(self, expected_languages):
        shortnames = map(attrgetter('shortname'), self.detected_languages)
        six.assertCountEqual(self, expected_languages, shortnames)

    def then_parser_languages_are(self, expected_languages):
        shortnames = map(attrgetter('shortname'), self.parser.languages)
        six.assertCountEqual(self, expected_languages, shortnames)


class ExactLanguagesTest(BaseTestCase):
    def setUp(self):
        super(ExactLanguagesTest, self).setUp()
        self.parser = NotImplemented
        self.detected_languages = NotImplemented

    def test_languages_passed_in_constructor_should_not_be_none(self):
        self.when_parser_is_constructed(languages=None)
        self.then_error_was_raised(ValueError, ['language cannot be None for ExactLanguages'])

    @parameterized.expand([
        param(languages=['es'], date_strings=["13 Ago, 2014"]),
        param(languages=['es'], date_strings=["13 Septiembre, 2014"]),
        param(languages=['es'], date_strings=["13/03/2014"]),
        param(languages=['es'], date_strings=["11/03/2014"]),
    ])
    def test_parse_date_in_exact_language(self, languages, date_strings):
        self.given_parser(languages)
        self.when_languages_are_detected(date_strings)
        self.then_detected_languages_are(languages)

    @parameterized.expand([
        param(languages=['es'], date_strings=["13 Setembro, 2014"]),
    ])
    def test_reject_dates_in_other_languages(self, languages, date_strings):
        self.given_parser(languages=languages)
        self.when_languages_are_detected(date_strings)
        self.then_detected_languages_are([])

    def given_parser(self, languages):
        language_map = default_language_loader.get_language_map()
        languages = [language_map[language]
                     for language in languages]
        self.parser = ExactLanguages(languages)

    def when_languages_are_detected(self, date_strings, modify=False):
        assert not isinstance(date_strings, six.string_types)
        for date_string in date_strings:
            detected_languages = list(self.parser.iterate_applicable_languages(date_string, modify=modify))
        self.detected_languages = detected_languages

    def when_parser_is_constructed(self, languages):
        try:
            ExactLanguages(languages)
        except Exception as error:
            self.error = error

    def then_detected_languages_are(self, expected_languages):
        shortnames = map(attrgetter('shortname'), self.detected_languages)
        six.assertCountEqual(self, expected_languages, shortnames)


class TestDateParser(BaseTestCase):
    def setUp(self):
        super(TestDateParser, self).setUp()
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
        param('Wed Aug 05 12:00:00 EDT 2015', datetime(2015, 8, 5, 16, 0)),
        param('April 9, 2013 at 6:11 a.m.', datetime(2013, 4, 9, 6, 11)),
        param('Aug. 9, 2012 at 2:57 p.m.', datetime(2012, 8, 9, 14, 57)),
        param('December 10, 2014, 11:02:21 pm', datetime(2014, 12, 10, 23, 2, 21)),
        param('8:25 a.m. Dec. 12, 2014', datetime(2014, 12, 12, 8, 25)),
        param('2:21 p.m., December 11, 2014', datetime(2014, 12, 11, 14, 21)),
        param('Fri, 12 Dec 2014 10:55:50', datetime(2014, 12, 12, 10, 55, 50)),
        param('20 Mar 2013 10h11', datetime(2013, 3, 20, 10, 11)),
        param('10:06am Dec 11, 2014', datetime(2014, 12, 11, 10, 6)),
        param('19 February 2013 year 09:10', datetime(2013, 2, 19, 9, 10)),
        # French dates
        param('11 Mai 2014', datetime(2014, 5, 11)),
        param('dimanche, 11 Mai 2014', datetime(2014, 5, 11)),
        param('22 janvier 2015 à 14h40', datetime(2015, 1, 22, 14, 40)),
        param('Dimanche 1er Février à 21:24', datetime(2012, 2, 1, 21, 24)),
        param('vendredi, décembre 5 2014.', datetime(2014, 12, 5, 0, 0)),
        param('le 08 Déc 2014 15:11', datetime(2014, 12, 8, 15, 11)),
        param('Le 11 Décembre 2014 à 09:00', datetime(2014, 12, 11, 9, 0)),
        param('fév 15, 2013', datetime(2013, 2, 15, 0, 0)),
        # Spanish dates
        param('Martes 21 de Octubre de 2014', datetime(2014, 10, 21)),
        param('Miércoles 20 de Noviembre de 2013', datetime(2013, 11, 20)),
        param('12 de junio del 2012', datetime(2012, 6, 12)),
        param('13 Ago, 2014', datetime(2014, 8, 13)),
        param('13 Septiembre, 2014', datetime(2014, 9, 13)),
        param('11 Marzo, 2014', datetime(2014, 3, 11)),
        param('julio 5, 2015 en 1:04 pm', datetime(2015, 7, 5, 13, 4)),
        # Dutch dates
        param('11 augustus 2014', datetime(2014, 8, 11)),
        param('14 januari 2014', datetime(2014, 1, 14)),
        param('vr jan 24, 2014 12:49', datetime(2014, 1, 24, 12, 49)),
        # Italian dates
        param('16 giu 2014', datetime(2014, 6, 16)),
        param('26 gennaio 2014', datetime(2014, 1, 26)),
        # Portuguese dates
        param('sexta-feira, 10 de junho de 2014 14:52', datetime(2014, 6, 10, 14, 52)),
        param('13 Setembro, 2014', datetime(2014, 9, 13)),
        # Russian dates
        param('10 мая', datetime(2012, 5, 10)),  # forum.codenet.ru
        param('26 апреля', datetime(2012, 4, 26)),
        param('20 ноября 2013', datetime(2013, 11, 20)),
        param('28 октября 2014 в 07:54', datetime(2014, 10, 28, 7, 54)),
        param('13 января 2015 г. в 13:34', datetime(2015, 1, 13, 13, 34)),
        param('09 августа 2012', datetime(2012, 8, 9, 0, 0)),
        param('Авг 26, 2015 15:12', datetime(2015, 8, 26, 15, 12)),
        param('2 Декабрь 95 11:15', datetime(1995, 12, 2, 11, 15)),
        # Turkish dates
        param('11 Ağustos, 2014', datetime(2014, 8, 11)),
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
        param('13 Srpen, 2014', datetime(2014, 8, 13)),
        param('čtv 14. lis 2013 12:38:43', datetime(2013, 11, 14, 12, 38, 43)),
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
        # Belarusian dates
        param('11 траўня', datetime(2012, 5, 11)),
        param('4 мая', datetime(2012, 5, 4)),
        param('Чацвер 06 жніўня 2015', datetime(2015, 8, 6)),
        param('Нд 14 сакавіка 2015 у 7 гадзін 10 хвілін', datetime(2015, 3, 14, 7, 10)),
        param('5 жніўня 2015 года у 13:34', datetime(2015, 8, 5, 13, 34)),
        # Polish dates
        param('14 sierpnia 2015 roku o 12:13', datetime(2015, 8, 14, 12, 13)),
        param('2012, wrz 13, 15:05', datetime(2012, 9, 13, 15, 5)),
        # Numeric dates
        param('06-17-2014', datetime(2014, 6, 17)),
        param('13/03/2014', datetime(2014, 3, 13)),
        param('11. 12. 2014, 08:45:39', datetime(2014, 11, 12, 8, 45, 39)),
    ])
    def test_dates_parsing(self, date_string, expected):
        self.given_utcnow(datetime(2012, 11, 13))  # Tuesday
        self.given_local_tz_offset(0)
        self.given_parser()
        self.when_date_is_parsed(date_string)
        self.then_date_was_parsed_by_date_parser()
        self.then_period_is('day')
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('Sep 03 2014 | 4:32 pm EDT', datetime(2014, 9, 3, 21, 32)),
        param('17th October, 2034 @ 01:08 am PDT', datetime(2034, 10, 17, 9, 8)),
        param('15 May 2004 23:24 EDT', datetime(2004, 5, 16, 4, 24)),
        param('15 May 2004', datetime(2004, 5, 15, 0, 0)),
        param('08/17/14 17:00 (PDT)', datetime(2014, 8, 18, 1, 0)),
    ])
    def test_parsing_with_time_zones(self, date_string, expected):
        self.given_local_tz_offset(+1)
        self.given_parser()
        self.when_date_is_parsed(date_string)
        self.then_date_was_parsed_by_date_parser()
        self.then_period_is('day')
        self.then_date_obj_exactly_is(expected)

    @parameterized.expand([
        param('15 May 2004 16:10 -0400', datetime(2004, 5, 15, 20, 10)),
        param('1999-12-31 19:00:00 -0500', datetime(2000, 1, 1, 0, 0)),
        param('1999-12-31 19:00:00 +0500', datetime(1999, 12, 31, 14, 0)),
        param('Fri, 09 Sep 2005 13:51:39 -0700', datetime(2005, 9, 9, 20, 51, 39)),
        param('Fri, 09 Sep 2005 13:51:39 +0000', datetime(2005, 9, 9, 13, 51, 39)),
    ])
    def test_parsing_with_utc_offsets(self, date_string, expected):
        self.given_local_tz_offset(0)
        self.given_parser()
        self.when_date_is_parsed(date_string)
        self.then_date_was_parsed_by_date_parser()
        self.then_period_is('day')
        self.then_date_obj_exactly_is(expected)

    def test_empty_dates_string_is_not_parsed(self):
        self.when_date_is_parsed_by_date_parser('')
        self.then_error_was_raised(ValueError, ["Empty string"])

    @parameterized.expand([
        param('invalid date string'),
        param('Aug 7, 2014Aug 7, 2014'),
        param('24h ago'),
    ])
    def test_dates_not_parsed(self, date_string):
        self.when_date_is_parsed_by_date_parser(date_string)
        self.then_error_was_raised(ValueError, ["unknown string format"])

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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed(date_string)
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
        self.when_date_is_parsed('24 April 2012')
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
        self.when_date_is_parsed_by_date_parser(date_string)
        self.then_error_was_raised(ValueError, ['Day not in range for month'])

    @parameterized.expand([
        param('2015-05-02T10:20:19+0000', languages=['fr'], expected=datetime(2015, 5, 2, 10, 20, 19)),
        param('2015-05-02T10:20:19+0000', languages=['en'], expected=datetime(2015, 5, 2, 10, 20, 19)),
        param('2015-05-02T10:20:19+0000', languages=[], expected=datetime(2015, 5, 2, 10, 20, 19)),
    ])
    def test_iso_datestamp_format_should_always_parse(self, date_string, languages, expected):
        self.given_local_tz_offset(0)
        self.given_parser(languages=languages)
        self.when_date_is_parsed(date_string)
        self.then_date_was_parsed_by_date_parser()
        self.then_date_obj_exactly_is(expected)

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
        self.when_date_is_parsed(date_string)
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

    def given_parser(self, *args, **kwds):
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
        self.parser = DateDataParser(*args, **kwds)

    def given_configuration(self, key, value):
        self.add_patch(patch.object(settings, key, new=value))

    def when_date_is_parsed(self, date_string):
        self.result = self.parser.get_date_data(date_string)

    def when_date_is_parsed_by_date_parser(self, date_string):
        try:
            self.result = DateParser().parse(date_string)
        except Exception as error:
            self.error = error

    def then_period_is(self, period):
        self.assertEqual(period, self.result['period'])

    def then_date_obj_exactly_is(self, expected):
        self.assertEqual(expected, self.result['date_obj'])

    def then_date_was_parsed_by_date_parser(self):
        self.assertNotEqual(NotImplemented, self.date_result, "Date was not parsed")
        self.assertEqual(self.result['date_obj'], self.date_result[0])


if __name__ == '__main__':
    unittest.main()
