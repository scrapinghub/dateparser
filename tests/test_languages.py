# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose_parameterized import parameterized, param

from dateparser.languages import default_language_loader, Language
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages
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
        # Chinese
        param('cn', "1年11个月", "1 year 11 month"),
        # French
        param('fr', "20 Février 2012", "20 february 2012"),
        param('fr', "Mercredi 19 Novembre 2013", "wednesday 19 november 2013"),
        param('fr', "18 octobre 2012 à 19 h 21 min", "18 october 2012  19:21"),
        # German
        param('de', "29. Juni 2007", "29. june 2007"),
        param('de', "Montag 5 Januar, 2015", "monday 5 january 2015"),
        # Spanish
        param('es', "Miércoles 31 Diciembre 2014", "wednesday 31 december 2014"),
        # Italian
        param('it', "Giovedi Maggio 29 2013", "thursday may 29 2013"),
        param('it', "19 Luglio 2013", "19 july 2013"),
        # Portuguese
        param('pt', "22 de dezembro de 2014 às 02:38", "22  december  2014  02:38"),
        # Russian
        param('ru', "5 августа 2014 г. в 12:00", "5 august 2014 year  12:00"),
        # Turkish
        param('tr', "2 Ocak 2015 Cuma, 16:49", "2 january 2015 friday 16:49"),
        # Czech
        param('cz', "22. prosinec 2014 v 2:38", "22. december 2014  2:38"),
        # Dutch
        param('nl', "maandag 22 december 2014 om 2:38", "monday 22 december 2014  2:38"),
        # Romanian
        param('ro', "22 Decembrie 2014 la 02:38", "22 december 2014  02:38"),
        # Polish
        param('pl', "4 stycznia o 13:50", "4 january  13:50"),
        param('pl', "29 listopada 2014 o 08:40", "29 november 2014  08:40"),
        # Ukrainian
        param('uk', "30 листопада 2013 о 04:27", "30 november 2013  04:27"),
        # Belarusian
        param('by', "5 снежня 2015 г. у 12:00", "5 december 2015 year  12:00"),
        param('by', "11 верасня 2015 г. у 12:11", "11 september 2015 year  12:11"),
        param('by', "3 стд 2015 г. у 10:33", "3 january 2015 year  10:33"),
        # Arabic
        param('ar', "6 يناير، 2015، الساعة 05:16 مساءً", "6 january 2015 05:16 pm"),
        param('ar', "7 يناير، 2015، الساعة 11:00 صباحاً", "7 january 2015 11:00 am"),
        # Vietnamese
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015", "thursday 8  january  2015"),
        param('vi', "Thứ Tư, 07/01/2015 | 22:34", "wednesday 07/01/2015  22:34"),
        param('vi', "9 Tháng 1 2015 lúc 15:08", "9  january  2015  15:08"),
        # Thai
        param('th', "เมื่อ กุมภาพันธ์ 09, 2015, 09:27:57 AM", "february 09 2015 09:27:57 am"),
        param('th', "เมื่อ กรกฎาคม 05, 2012, 01:18:06 AM", "july 05 2012 01:18:06 am"),

        # Filipino
        param('ph', "Biyernes Hulyo 3, 2015", "friday july 3 2015"),
        param('ph', "Pebrero 5, 2015 7:00 pm", "february 5 2015 7:00 pm"),
        # Indonesian
        param('id', "06 Sep 2015", "06 september 2015"),
        param('id', "07 Feb 2015 20:15", "07 february 2015 20:15"),

        # Miscellaneous
        param('en', "2014-12-12T12:33:39-08:00", "2014-12-12 12:33:39-08:00"),
        param('en', "2014-10-15T16:12:20+00:00", "2014-10-15 16:12:20+00:00"),
        param('en', "28 Oct 2014 16:39:01 +0000", "28 october 2014 16:39:01 +0000"),
        param('es', "13 Febrero 2015 a las 23:00", "13 february 2015  23:00")
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
        param('en', "less than a minute ago", "45 second"),
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
        param('es', "ayer a las", "1 day "),
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
        param('pt', "há 14 min.", "ago 14 minute."),
        param('pt', "1 segundo atrás", "1 second ago"),
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
        param('ar', "أمس", "1 day"),
        param('ar', "4 عام", "4 year"),
        param('ar', "منذ 2 ساعات", "ago 2 hour"),
        param('ar', "منذ ساعتين", "ago 2 hour"),
        # Polish
        param('pl', "2 godz.", "2 hour"),
        param('pl', "Wczoraj o 07:40", "1 day  07:40"),
        param('pl', "Poniedziałek 8:10 pm", "monday 8:10 pm"),
        # Vietnamese
        param('vi', "2 tuần 3 ngày", "2 week 3 day"),
        param('vi', "21 giờ trước", "21 hour ago"),
        param('vi', "Hôm qua 08:16", "1 day 08:16"),
        param('vi', "Hôm nay 15:39", "0 day 15:39"),
        #French
        param('fr', u"Il y a moins d'une minute", "ago 1 minute"),
        param('fr', u"Il y a moins de 30s", "ago 30 s"),
        #Filipino
        param('ph', "kahapon", "1 day"),
        param('ph', "ngayon", "0 second"),
        # Belarusian
        param('by', "9 месяцаў", "9 month"),
        param('by', "8 тыдняў", "8 week"),
        param('by', "1 тыдзень", "1 week"),
        param('by', "2 года", "2 year"),
        param('by', "3 гады", "3 year"),
        param('by', "11 секунд", "11 second"),
        param('by', "учора", "1 day"),
        param('by', "пазаўчора", "2 day"),
        param('by', "сёння", "0 day"),
        param('by', "некалькі хвілін", "2 minute"),
        # Indonesian
        param('id', "baru saja", "0 second"),
        param('id', "hari ini", "0 day"),
        param('id', "kemarin", "1 day"),
        param('id', "kemarin lusa", "2 day"),
        param('id', "sehari yang lalu", "1 day  ago"),
        param('id', "seminggu yang lalu", "1 week  ago"),
        param('id', "sebulan yang lalu", "1 month  ago"),
        param('id', "setahun yang lalu", "1 year  ago"),
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
        param('de', "Gestern um 04:41", ['Gestern ', 'um', ' ', '04', ':', '41']),
        param('de', "Donnerstag, 8. Januar 2015 um 07:17", ['Donnerstag', ' ', '8', '.', ' ', 'Januar', ' ', '2015', ' ', 'um', ' ', '07', ':', '17']),
        param('ru', "8 января 2015 г. в 9:10", ['8', ' ', 'января', ' ', '2015', ' ', 'г.', ' ', 'в', ' ', '9', ':', '10']),
        param('cz', "6. leden 2015 v 22:29", ['6', '.', ' ', 'leden', ' ', '2015', ' ', 'v', ' ', '22', ':', '29']),
        param('nl', "woensdag 7 januari 2015 om 21:32", ['woensdag', ' ', '7', ' ', 'januari', ' ', '2015', ' ', 'om', ' ', '21', ':', '32']),
        param('ro', "8 Ianuarie 2015 la 13:33", ['8', ' ', 'Ianuarie', ' ', '2015', ' ', 'la', ' ', '13', ':', '33']),
        param('ar', "8 يناير، 2015، الساعة 10:01 صباحاً", ['8', ' ', 'يناير', ' ', '2015', 'الساعة', ' ', '10', ':', '01', ' صباحاً']),
        param('th', "8 มกราคม 2015 เวลา 12:22 น.", ['8', ' ', 'มกราคม', ' ', '2015', ' ', 'เวลา', ' ', '12', ':', '22', ' ', 'น.']),
        param('pl', "8 stycznia 2015 o 10:19", ['8', ' ', 'stycznia', ' ', '2015', ' ', 'o', ' ', '10', ':', '19']),
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015", ["Thứ Năm", " ", "ngày", " ", "8", " tháng ", "1", " ", "năm", " ", "2015"]),
        param('ph', "Biyernes Hulyo 3 2015", ["Biyernes", " ", "Hulyo", " ", "3", " ", "2015"]),
        param('by', "3 верасня 2015 г. у 11:10", ['3', ' ', 'верасня', ' ', '2015', ' ', 'г.', ' ', 'у', ' ', '11', ':', '10']),
        param('id', "3 Juni 2015 13:05:46", ['3', ' ', 'Juni', ' ', '2015', ' ', '13', ':', '05', ':', '46']),
    ])
    def test_split(self, shortname, datetime_string, expected_tokens):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_splitted()
        self.then_tokens_are(expected_tokens)

    @parameterized.expand([
        param('en', "17th October, 2034 @ 01:08 am PDT", strip_timezone=True),
        param('en', "#@Sept#04#2014", strip_timezone=False),
        param('en', "2014-12-13T00:11:00Z", strip_timezone=False),
        param('de', "Donnerstag, 8. Januar 2015 um 07:17", strip_timezone=False),
        param('ru', "8 января 2015 г. в 9:10", strip_timezone=False),
        param('cz', "Pondělí v 22:29", strip_timezone=False),
        param('nl', "woensdag 7 januari om 21:32", strip_timezone=False),
        param('ro', "8 Ianuarie 2015 la 13:33", strip_timezone=False),
        param('ar', "ساعتين", strip_timezone=False),
        param('tr', "3 hafta", strip_timezone=False),
        param('th', "17 เดือนมิถุนายน", strip_timezone=False),
        param('pl', "przedwczoraj", strip_timezone=False),
        param('fa', "ژانویه 8, 2015، ساعت 15:46", strip_timezone=False),
        param('vi', "2 tuần 3 ngày", strip_timezone=False),
        param('ph', "Hulyo 3, 2015 7:00 pm", strip_timezone=False),
        param('by', "3 верасня 2015 г. у 11:10", strip_timezone=False),
        param('id', "01 Agustus 2015 18:23", strip_timezone=False),
    ])
    def test_applicable_languages(self, shortname, datetime_string, strip_timezone):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_applicable()

    @parameterized.expand([
        param('ru', "08.haziran.2014, 11:07", strip_timezone=False),
        param('ar', "6 دقیقه", strip_timezone=False),
        param('fa', "ساعتين", strip_timezone=False),
        param('cz', "3 hafta", strip_timezone=False),
    ])
    def test_not_applicable_languages(self, shortname, datetime_string, strip_timezone):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_not_applicable()

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def given_bundled_language(self, shorname):
        self.language = default_language_loader.get_language(shorname)

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


class BaseLanguageDetectorTestCase(BaseTestCase):
    __test__ = False

    NOT_DETECTED = object()

    def setUp(self):
        super(BaseLanguageDetectorTestCase, self).setUp()
        self.datetime_string = NotImplemented
        self.detector = NotImplemented
        self.detected_language = NotImplemented
        self.known_languages = None

    @parameterized.expand([
        param("1 january 2015", 'en'),
        ])
    def test_valid_dates_detected(self, datetime_string, expected_language):
        self.given_languages(expected_language)
        self.given_detector()
        self.given_string(datetime_string)
        self.when_searching_for_first_applicable_language()
        self.then_language_was_detected(expected_language)

    @parameterized.expand([
        param("foo"),
    ])
    def test_invalid_dates_not_detected(self, datetime_string):
        self.given_languages('en')
        self.given_detector()
        self.given_string(datetime_string)
        self.when_searching_for_first_applicable_language()
        self.then_no_language_was_detected()

    def test_invalid_date_after_valid_date_not_detected(self):
        self.given_languages('en')
        self.given_detector()
        self.given_previosly_detected_string("1 january 2015")
        self.given_string("foo")
        self.when_searching_for_first_applicable_language()
        self.then_no_language_was_detected()

    def test_valid_date_after_invalid_date_detected(self):
        self.given_languages('en')
        self.given_detector()
        self.given_previosly_detected_string("foo")
        self.given_string("1 january 2015")
        self.when_searching_for_first_applicable_language()
        self.then_language_was_detected('en')

    def given_languages(self, *shortnames):
        self.known_languages = [default_language_loader.get_language(shortname)
                                for shortname in shortnames]

    def given_previosly_detected_string(self, datetime_string):
        for _ in self.detector.iterate_applicable_languages(datetime_string, modify=True):
            break

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def given_detector(self):
        raise NotImplementedError

    def when_searching_for_first_applicable_language(self):
        for language in self.detector.iterate_applicable_languages(self.datetime_string, modify=True):
            self.detected_language = language
            break
        else:
            self.detected_language = self.NOT_DETECTED

    def then_language_was_detected(self, shortname):
        self.assertIsInstance(self.detected_language, Language, "Language was not properly detected")
        self.assertEqual(shortname, self.detected_language.shortname)

    def then_no_language_was_detected(self):
        self.assertIs(self.detected_language, self.NOT_DETECTED)


class TestExactLanguages(BaseLanguageDetectorTestCase):
    __test__ = True

    @parameterized.expand([
        param("01-01-12", ['en', 'fr']),
        param("01-01-12", ['tr', 'ar']),
        param("01-01-12", ['ru', 'fr', 'en', 'pl']),
        param("01-01-12", ['en']),
    ])
    def test_exact_languages(self, datetime_string, shortnames):
        self.given_string(datetime_string)
        self.given_known_languages(shortnames)
        self.given_detector()
        self.when_using_exact_languages()
        self.then_exact_languages_were_filtered(shortnames)

    def given_known_languages(self, shortnames):
        self.known_languages = [default_language_loader.get_language(shortname)
                                for shortname in shortnames]

    def given_detector(self):
        self.assertIsInstance(self.known_languages, list, "Require a list of languages to initialize")
        self.assertGreaterEqual(len(self.known_languages), 1, "Could only be initialized with one or more languages")
        self.detector = ExactLanguages(languages=self.known_languages)

    def when_using_exact_languages(self):
        self.exact_languages = self.detector.iterate_applicable_languages(self.datetime_string, modify=True)

    def then_exact_languages_were_filtered(self, shortnames):
        self.assertEqual(set(shortnames), set([lang.shortname for lang in self.exact_languages]))


class BaseAutoDetectLanguageDetectorTestCase(BaseLanguageDetectorTestCase):
    allow_redetection = NotImplemented

    def given_detector(self):
        self.detector = AutoDetectLanguage(languages=self.known_languages, allow_redetection=self.allow_redetection)


class TestAutoDetectLanguageDetectorWithoutRedetection(BaseAutoDetectLanguageDetectorTestCase):
    __test__ = True
    allow_redetection = False


class TestAutoDetectLanguageDetectorWithRedetection(BaseAutoDetectLanguageDetectorTestCase):
    __test__ = True
    allow_redetection = True
