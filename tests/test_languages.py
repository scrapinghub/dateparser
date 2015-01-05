# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose_parameterized import parameterized, param

from dateparser.languages import LanguageDataLoader
from tests import BaseTestCase


class TestBundledLanguages(BaseTestCase):
    def setUp(self):
        super(TestBundledLanguages, self).setUp()
        self.language = NotImplemented
        self.datetime_string = NotImplemented
        self.translation = NotImplemented
        self.tokens = NotImplemented
        self.result = NotImplemented

    @parameterized.expand([
        param('en', "Sep 03 2014", "september 03 2014"),
        param('en', "friday, 03 september 2014", "friday 03 september 2014"),
        param('cn', "1年11个月", "1 year 11 month"),
        # French
        param('fr', "20 Février 2012", "20 february 2012"),
        param('fr', "Mercredi 19 Novembre 2013", "wednesday 19 november 2013"),
    ])
    def test_translation(self, shortname, datetime_string, expected_translation):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

    @parameterized.expand([
        # English
        param('en', "yesterday", "1 day"),
        param('en', "today", "0 day"),
        param('en', "day before yesterday", "2 day"),
        param('en', "last month", "1 month"),
        # German
        param('de', "vorgestern", "2 day"),
        param('de', "heute", "0 day"),
        param('de', "vor 3 Stunden", "ago 3 hour"),
        # French
        param('fr', "avant-hier", "2 day"),
        param('fr', "hier", "1 day"),
        param('fr', "aujourd'hui", "0 day"),
        # Spanish
        param('es', "anteayer", "2 day"),
        param('es', "ayer", "1 day"),
        param('es', "hoy", "0 day"),
        param('es', "hace un horas", "ago 1 hour"),
        param('es', "2 semanas", "2 week"),
        param('es', "2 año", "2 year"),
        # Italian
        param('it', "altro ieri", "2 day"),
        param('it', "ieri", "1 day"),
        param('it', "oggi", "0 day"),
        param('it', "2 settimana fa", "2 week ago"),
        param('it', "2 anno fa", "2 year ago"),
        # Portuguese
        param('pt', "anteontem", "2 day"),
        param('pt', "ontem", "1 day"),
        param('pt', "hoje", "0 day"),
        param('pt', "56 minutos", "56 minute"),
        param('pt', "12 dias", "12 day"),
        # Russian
        param('ru', "9 месяцев", "9 month"),
        param('ru', "8 недели", "8 week"),
        param('ru', "7 года", "7 year"),
        param('ru', "вчера", "1 day"),
        param('ru', "сегодня", "0 day"),
        param('ru', "несколько секунд", "44 second"),
        # Turkish
        param('tr', "dün", "1 day"),
        param('tr', "22 dakika", "22 minute"),
        param('tr', "12 hafta", "12 week"),
        param('tr', "13 yıl", "13 year"),
        # Czech
        param('cz', "40 sekunda", "40 second"),
        param('cz', "4 týden", "4 week"),
        param('cz', "14 roků", "14 year"),
        # Chinese
        param('cn', "昨天", "1 day"),
        param('cn', "前天", "2 day"),
        param('cn', "50 秒", "50 second"),
        param('cn', "7 周", "7 week"),
        param('cn', "12 年", "12 year"),
        # Dutch
        param('nl', "17 uur geleden", "17 hour ago"),
        param('nl', "27 jaar geleden", "27 year ago"),
        param('nl', "45 minuten", "45 minute"),
        # Romanian
        param('ro', "23 săptămâni în urmă", "23 week ago"),
        param('ro', "23 săptămâni", "23 week"),
        param('ro', "13 oră", "13 hour"),
        # Arabic
        param('ar', "يومين", "2 day"),
        param('ar', "يوم أمس", "1 day"),
        param('ar', "4 عام", "4 year"),
        param('ar', "منذ 2 ساعات", "ago 2 hour"),
        # Vietnamese
        param('vi', "2 tuần 3 ngày", "2 week 3 day")
    ])
    def test_freshness_translation(self, shortname, datetime_string, expected_translation):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

    @parameterized.expand([
        param('pt', "sexta-feira, 10 de junho de 2014 14:52",
              ["sexta-feira", " ", "10", " ", "de", " ", "junho", " ", "de", " ", "2014", " ", "14", ":", "52"]),
        param('it', "14_luglio_15", ["14", "luglio", "15"]),
        param('cn', "1年11个月", ["1", "年", "11", "个月"]),
        param('tr', "2 saat önce", ["2", " ", "saat", " ", "önce"]),
        param('fr', "il ya environ 23 heures'", ["il ya", " ", "environ", " ", "23", " ", "heures"]),
    ])
    def test_split(self, shortname, datetime_string, expected_tokens):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_splitted()
        self.then_tokens_are(expected_tokens)

    @parameterized.expand([
        param('en', "17th October, 2034 @ 01:08 am PDT", strip_timezone=True),
        param('en', "#@Sept#04#2014", strip_timezone=False),
        param('vi', "2 tuần 3 ngày", strip_timezone=False),
    ])
    def test_applicable_languages(self, shortname, datetime_string, strip_timezone):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_applicable()

    @parameterized.expand([
        param('ru', "08.haziran.2014, 11:07", strip_timezone=False),
    ])
    def test_not_applicable_languages(self, shortname, datetime_string, strip_timezone):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_not_applicable()

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def given_bundled_language(self, shorname):
        self.language = LanguageDataLoader().get_language(shorname)

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(self.datetime_string)

    def when_datetime_string_splitted(self, keep_formatting=False):
        self.tokens = self.language._split(self.datetime_string, keep_formatting)

    def when_datetime_string_checked_if_applicable(self, strip_timezone):
        self.result = self.language.is_applicable(self.datetime_string, strip_timezone)

    def then_string_translated_to(self, expected_string):
        self.assertEqual(expected_string, self.translation)

    def then_tokens_are(self, expected_tokens):
        self.assertEqual(expected_tokens, self.tokens)

    def then_language_is_applicable(self):
        self.assertTrue(self.result)

    def then_language_is_not_applicable(self):
        self.assertFalse(self.result)
