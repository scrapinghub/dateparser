# coding: utf-8
from __future__ import unicode_literals

import unittest
from datetime import datetime

from mock import patch, Mock

from dateparser.date_parser import DateParser, translate_words
from dateparser.date_parser import AutoDetectLanguage, ExactLanguage
from dateparser.date_parser import LanguageWasNotSeenBeforeError


class AutoDetectLanguageTest(unittest.TestCase):

    def setUp(self):
        self.parser = AutoDetectLanguage(None)

    def test_detect_language(self):
        self.assertEqual(['es', 'pt'], self.parser.detect_language('11 abril 2010'))
        self.assertEqual(['es'], self.parser.detect_language('11 junio 2010'))

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


class ExactLanguageTest(unittest.TestCase):

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
        parser = ExactLanguage('es')

        for date_string, correct_date in date_fixtures:
            parsed_date = parser.parse(date_string, None)
            self.assertEqual(correct_date.date(), parsed_date.date())

        with self.assertRaisesRegexp(ValueError, 'Invalid date'):
            portuguese_date = u'13 Setembro, 2014'
            parser.parse(portuguese_date, None)


class TestDateParser(unittest.TestCase):

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

    def test_weekdays(self):
        tuesday = datetime(2014, 8, 12, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        datetime_mock = Mock(wraps=datetime)
        datetime_mock.utcnow = Mock(return_value=tuesday)
        with patch('dateparser.date_parser.datetime', new=datetime_mock):
            date = DateParser(language='en').parse('Friday')
        self.assertEqual(date.year, 2014)
        self.assertEqual(date.month, 8)
        self.assertEqual(date.day, 8)
        self.assertEqual(date.hour, 0)
        self.assertEqual(date.minute, 0)
        self.assertEqual(date.second, 0)

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

    def test_should_reject_empty_string(self):
        dp = DateParser()
        with self.assertRaisesRegexp(ValueError, 'Empty string'):
            dp.parse('')

    def test_should_not_allow_multiple_languages_by_default(self):
        dates_in_spanish = [
            (u'13 Ago, 2014', datetime(2014, 8, 13)),
            (u'11 Marzo, 2014', datetime(2014, 3, 11)),
            (u'13 Septiembre, 2014', datetime(2014, 9, 13)),
        ]
        dp = DateParser()

        for date_string, correct_date in dates_in_spanish:
            parsed_date = dp.parse(date_string, None)
            self.assertEqual(correct_date.date(), parsed_date.date())

        with self.assertRaisesRegexp(ValueError, 'Invalid date'):
            portuguese_date = u'13 Setembro, 2014'
            dp.parse(portuguese_date, None)

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

    def test_finding_no_language_after_detecting_several(self):
        # when:
        dp = DateParser()
        # then:
        self.assertEqual(datetime(2014, 8, 13).date(),
                         dp.parse('13 Ago, 2014').date())

        with self.assertRaises(LanguageWasNotSeenBeforeError):
            dp.parse(u'11 Ağustos, 2014')

        # when:
        dp = DateParser(allow_redetect_language=True)
        # then:
        self.assertEqual(datetime(2014, 8, 13).date(),
                         dp.parse('13 Ago, 2014').date())

        self.assertEqual(datetime(2014, 8, 11).date(),
                         dp.parse(u'11 Ağustos, 2014').date())

    def test_fail(self):
        parser = DateParser()
        self.assertRaises(ValueError, parser.parse, 'invalid date string')


class DateutilHelpersTest(unittest.TestCase):

    def test_translate_words(self):
        self.assertEqual('14 06 13', translate_words('14 giu 13', 'it'))
        self.assertEqual('14 06 13', translate_words('14 giugno 13', 'it'))
        self.assertEqual('14 06 13', translate_words('14 junho 13', 'pt'))


if __name__ == '__main__':
    unittest.main()
