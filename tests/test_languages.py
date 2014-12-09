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
    ])
    def test_translation(self, shortname, datetime_string, expected_translation):
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
        param('ru', "08.haziran.2014, 11:07"),
    ])
    def test_not_applicable_languages(self, shortname, datetime_string):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable()
        self.then_language_is_not_applicable()

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def given_bundled_language(self, shorname):
        self.language = LanguageDataLoader().get_language(shorname)

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(self.datetime_string)

    def when_datetime_string_splitted(self, keep_formatting=False):
        self.tokens = self.language._split(self.datetime_string, keep_formatting)

    def when_datetime_string_checked_if_applicable(self):
        self.result = self.language.is_applicable(self.datetime_string)

    def then_string_translated_to(self, expected_string):
        self.assertEqual(expected_string, self.translation)

    def then_tokens_are(self, expected_tokens):
        self.assertEqual(expected_tokens, self.tokens)

    def then_language_is_applicable(self):
        self.assertTrue(self.result)

    def then_language_is_not_applicable(self):
        self.assertFalse(self.result)
