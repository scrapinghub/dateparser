# coding: utf-8
from __future__ import unicode_literals

import unittest

from dateparser.date_parser import DateParser
from datetime import datetime

class TestDateParser(unittest.TestCase):

    def test_detect_language(self):
        d = DateParser()

        languages = d.detect_language('11 abril 2010')
        self.assertEqual(languages, ['es', 'pt'])

        languages = d.detect_language('11 junio 2010')
        self.assertEqual(languages, ['es'])

    def test_fr_dates(self):
        date = DateParser().parse('11 Mai 2014')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 5)
        self.assertEqual(date.day, 11)

    def test_it_dates(self):
        date = DateParser().parse('16 giu 2014')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 16)

        date = DateParser().parse('26 gennaio 2014')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 26)

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

    def test_translate_words(self):
        parser = DateParser()
        self.assertEqual('14 06 13', parser.translate_words('14 giu 13', 'it'))
        self.assertEqual('14 06 13', parser.translate_words('14 giugno 13', 'it'))
        self.assertEqual('14 06 13', parser.translate_words('14 junho 13', 'pt'))

    def test_pt_dates(self):
        date = DateParser().parse('sexta-feira, 10 de junho de 2014 14:52')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 10)
        self.assertEqual(date.hour, 14)
        self.assertEqual(date.minute, 52)

    def test_ru_dates(self):
        # forum.codenet.ru
        date = DateParser().parse('10 мая')
        self.assertEqual(date.month, 5)
        self.assertEqual(date.day, 10)

        date = DateParser().parse('26 апреля')
        self.assertEqual(date.month, 4)
        self.assertEqual(date.day, 26)

        date = DateParser().parse('20 ноября 2013')
        self.assertEqual(date.year, 2013)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.day, 20)

    def test_tr_dates(self):
        # forum.andronova.net
        date = DateParser().parse('08.Haziran.2014, 11:07')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 8)
        self.assertEqual(date.hour, 11)
        self.assertEqual(date.minute, 07)

        date = DateParser().parse('17.Şubat.2014, 17:51')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.day, 17)
        self.assertEqual(date.hour, 17)
        self.assertEqual(date.minute, 51)

        # forum.ceviz.net
        date = DateParser().parse('14-Aralık-2012, 20:56')
        self.assertEqual(date.year, 2012)
        self.assertEqual(date.month, 12)
        self.assertEqual(date.day, 14)
        self.assertEqual(date.hour, 20)
        self.assertEqual(date.minute, 56)

    def test_should_parse_a_plain_string_date(self):
        date = DateParser().parse(str('06-17-2014'))
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 17)

    def test_cz_dates(self):
        # androidforum.cz
        date = DateParser(language='cz').parse('pon 16. čer 2014 10:07:43')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 6)
        self.assertEqual(date.day, 16)
        self.assertEqual(date.hour, 10)
        self.assertEqual(date.minute, 07)
        self.assertEqual(date.second, 43)

    def test_parse_common_date(self):
        date = DateParser().parse('Tuesday Jul 22, 2014')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 7)
        self.assertEqual(date.day, 22)

    def test_parse_only_hours_date(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = DateParser().parse('10:04am EDT')
        self.assertEqual(today.date(), result.date())

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

    def test_fail(self):
        parser = DateParser()
        self.assertRaises(ValueError, parser.parse, 'invalid date string')


if __name__ == '__main__':
    unittest.main()
