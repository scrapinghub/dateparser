from __future__ import unicode_literals
import unittest
import dateparser
from datetime import date


class TestCleanApi(unittest.TestCase):
    def test_parse_dates_in_different_languages(self):
        result = dateparser.parse('24 de Janeiro de 2014')
        self.assertEquals(date(2014, 1, 24), result.date())

        result = dateparser.parse('2 de Enero de 2013')
        self.assertEquals(date(2013, 1, 2), result.date())

        result = dateparser.parse('January 25, 2014')
        self.assertEquals(date(2014, 1, 25), result.date())

    def test_parse_date_only_in_given_language(self):
        result = dateparser.parse('24 de Janeiro de 2014', language='pt')
        self.assertEquals(date(2014, 1, 24), result.date())

        self.assertIsNone(dateparser.parse('January 24, 2014', language='pt'))
