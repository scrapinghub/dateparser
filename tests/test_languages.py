# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose_parameterized import parameterized, param

from dateparser.languages import default_language_loader, Language
from dateparser.languages.detection import AutoDetectLanguage, ExactLanguages
from dateparser.conf import settings
from dateparser.utils import normalize_unicode
from dateparser.languages.validation import LanguageValidator

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
        param('zh', "1年11个月", "1 year 11 month"),
        param('zh', "1年11個月", "1 year 11 month"),
        param('zh', "2015年04月08日10点05", "2015-04-08 10:05"),
        param('zh', "2015年04月08日10:05", "2015-04-08 10:05"),
        param('zh', "2013年04月08日", "2013-04-08"),
        param('zh', "周一", "monday"),
        param('zh', "礼拜一", "monday"),
        param('zh', "周二", "tuesday"),
        param('zh', "礼拜二", "tuesday"),
        param('zh', "周三", "wednesday"),
        param('zh', "礼拜三", "wednesday"),
        param('zh', "星期日 2015年04月08日10:05", "sunday 2015-04-08 10:05"),
        param('zh', "周六 2013年04月08日", "saturday 2013-04-08"),
        param('zh', "下午3:30", "3:30 pm"),
        param('zh', "凌晨3:30", "3:30 am"),
        param('zh', "中午", "12:00"),
        # French
        param('fr', "20 Février 2012", "20 february 2012"),
        param('fr', "Mercredi 19 Novembre 2013", "wednesday 19 november 2013"),
        param('fr', "18 octobre 2012 à 19 h 21 min", "18 october 2012  19:21"),
        # German
        param('de', "29. Juni 2007", "29. june 2007"),
        param('de', "Montag 5 Januar, 2015", "monday 5 january 2015"),
        # Hungarian
        param('hu', '2016 augusztus 11.', '2016 august 11.'),
        param('hu', '2016-08-13 szombat 10:21', '2016-08-13 saturday 10:21'),
        param('hu', '2016. augusztus 14. vasárnap 10:21', '2016. august 14. sunday 10:21'),
        param('hu', 'hétfő', 'monday'),
        param('hu', 'tegnapelőtt', '2 day ago'),
        param('hu', 'ma', "0 day ago"),
        param('hu', '2 hónappal ezelőtt', "2 month ago"),
        param('hu', '2016-08-13 szombat 10:21 GMT', '2016-08-13 saturday 10:21 GMT'),
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
        param('cs', "22. prosinec 2014 v 2:38", "22. december 2014  2:38"),
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
        param('be', "5 снежня 2015 г. у 12:00", "5 december 2015 year  12:00"),
        param('be', "11 верасня 2015 г. у 12:11", "11 september 2015 year  12:11"),
        param('be', "3 стд 2015 г. у 10:33", "3 january 2015 year  10:33"),
        # Arabic
        param('ar', "6 يناير، 2015، الساعة 05:16 مساءً", "6 january 2015 05:16 pm"),
        param('ar', "7 يناير، 2015، الساعة 11:00 صباحاً", "7 january 2015 11:00 am"),
        # Vietnamese
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015", "thursday 8 january 2015"),
        param('vi', "Thứ Tư, 07/01/2015 | 22:34", "wednesday 07/01/2015  22:34"),
        param('vi', "9 Tháng 1 2015 lúc 15:08", "9 january 2015  15:08"),
        # Thai
        param('th', "เมื่อ กุมภาพันธ์ 09, 2015, 09:27:57 AM", "february 09 2015 09:27:57 am"),
        param('th', "เมื่อ กรกฎาคม 05, 2012, 01:18:06 AM", "july 05 2012 01:18:06 am"),

        # Tagalog
        param('tl', "Biyernes Hulyo 3, 2015", "friday july 3 2015"),
        param('tl', "Pebrero 5, 2015 7:00 pm", "february 5 2015 7:00 pm"),
        # Indonesian
        param('id', "06 Sep 2015", "06 september 2015"),
        param('id', "07 Feb 2015 20:15", "07 february 2015 20:15"),

        # Miscellaneous
        param('en', "2014-12-12T12:33:39-08:00", "2014-12-12 12:33:39-08:00"),
        param('en', "2014-10-15T16:12:20+00:00", "2014-10-15 16:12:20+00:00"),
        param('en', "28 Oct 2014 16:39:01 +0000", "28 october 2014 16:39:01 +0000"),
        param('es', "13 Febrero 2015 a las 23:00", "13 february 2015  23:00"),

        # Danish
        param('da', "Sep 03 2014", "september 03 2014"),
        param('da', "fredag, 03 september 2014", "friday 03 september 2014"),
        param('da', "fredag d. 3 september 2014", "friday  3 september 2014"),

        # Finnish
        param('fi', "maanantai tammikuu 16, 2015", "monday january 16 2015"),
        param('fi', "ma tammi 16, 2015", "monday january 16 2015"),
        param('fi', "tiistai helmikuu 16, 2015", "tuesday february 16 2015"),
        param('fi', "ti helmi 16, 2015", "tuesday february 16 2015"),
        param('fi', "keskiviikko maaliskuu 16, 2015", "wednesday march 16 2015"),
        param('fi', "ke maalis 16, 2015", "wednesday march 16 2015"),
        param('fi', "torstai huhtikuu 16, 2015", "thursday april 16 2015"),
        param('fi', "to huhti 16, 2015", "thursday april 16 2015"),
        param('fi', "perjantai toukokuu 16, 2015", "friday may 16 2015"),
        param('fi', "pe touko 16, 2015", "friday may 16 2015"),
        param('fi', "lauantai kesäkuu 16, 2015", "saturday june 16 2015"),
        param('fi', "la kesä 16, 2015", "saturday june 16 2015"),
        param('fi', "sunnuntai heinäkuu 16, 2015", "sunday july 16 2015"),
        param('fi', "su heinä 16, 2015", "sunday july 16 2015"),
        param('fi', "su elokuu 16, 2015", "sunday august 16 2015"),
        param('fi', "su elo 16, 2015", "sunday august 16 2015"),
        param('fi', "su syyskuu 16, 2015", "sunday september 16 2015"),
        param('fi', "su syys 16, 2015", "sunday september 16 2015"),
        param('fi', "su lokakuu 16, 2015", "sunday october 16 2015"),
        param('fi', "su loka 16, 2015", "sunday october 16 2015"),
        param('fi', "su marraskuu 16, 2015", "sunday november 16 2015"),
        param('fi', "su marras 16, 2015", "sunday november 16 2015"),
        param('fi', "su joulukuu 16, 2015", "sunday december 16 2015"),
        param('fi', "su joulu 16, 2015", "sunday december 16 2015"),
        param('fi', "1. tammikuuta, 2016", "1. january 2016"),
        param('fi', "tiistaina, 27. lokakuuta 2015", "tuesday 27. october 2015"),

        # Japanese
        param('ja', "午後3時", "pm 3:00"),
        param('ja', "2時", "2:00"),
        param('ja', "11時42分", "11:42"),
        param('ja', "3ヶ月", "3 month"),
        param('ja', "約53か月前", "53 month ago"),
        param('ja', "3月", "march"),
        param('ja', "十二月", "december"),
        param('ja', "2月10日", "2-10"),
        param('ja', "2013年2月", "2013 year february"),
        param('ja', "2013年04月08日", "2013-04-08"),
        param('ja', "2016年03月24日 木曜日 10時05分", "2016-03-24 thursday 10:05"),
        param('ja', "2016年3月20日 21時40分", "2016-3-20 21:40"),
        param('ja', "2016年03月21日 23時05分11秒", "2016-03-21 23:05:11"),
        param('ja', "2016年3月21日(月) 14時48分", "2016-3-21 monday 14:48"),
        param('ja', "2016年3月20日(日) 21時40分", "2016-3-20 sunday 21:40"),
        param('ja', "2016年3月20日 (日) 21時40分", "2016-3-20 sunday 21:40"),

        # Hebrew
        param('he', "20 לאפריל 2012", "20 april 2012"),
        param('he', "יום רביעי ה-19 בנובמבר 2013", "wednesday 19 november 2013"),
        param('he', "18 לאוקטובר 2012 בשעה 19:21", "18 october 2012  19:21"),
        param('he', "יום ה' 6/10/2016", "thursday 6/10/2016"),
        param('he', "חצות", "12 am"),
        param('he', "1 אחר חצות", "1 am"),
        param('he', "3 לפנות בוקר", "3 am"),
        param('he', "3 בבוקר", "3 am"),
        param('he', "3 בצהריים", "3 pm"),
        param('he', "6 לפנות ערב", "6 pm"),
        param('he', "6 אחרי הצהריים", "6 pm"),
        param('he', "6 אחרי הצהרים", "6 pm"),

        # Bangla
        param('bn', "সেপ্টেম্বর 03 2014", "september 03 2014"),
        param('bn', "শুক্রবার, 03 সেপ্টেম্বর 2014", "friday 03 september 2014"),

        # Hindi
        param('hi', 'सोमवार 13 जून 1998', 'monday 13 june 1998'),
        param('hi', 'मंगल 16 1786 12:18', 'tuesday 16 1786 12:18'),
        param('hi', 'शनि 11 अप्रैल 2002 03:09', 'saturday 11 april 2002 03:09'),

        # Swedish
        param('sv', "Sept 03 2014", "september 03 2014"),
        param('sv', "fredag, 03 september 2014", "friday 03 september 2014"),
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
        param('de', "vor 2 Monaten", "ago 2 month"),
        param('de', "vor 2 Monaten, 2 Wochen", "ago 2 month 2 week"),
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
        param('ru', "позавчера", "2 day"),
        param('ru', "сейчас", "now"),
        param('ru', "спустя 2 дня", "in 2 day"),
        param('ru', "вчера", "1 day"),
        param('ru', "сегодня", "0 day"),
        param('ru', "завтра", "in 1 day"),
        param('ru', "послезавтра", "in 2 day"),
        param('ru', "несколько секунд", "44 second"),
        # Turkish
        param('tr', "dün", "1 day"),
        param('tr', "22 dakika", "22 minute"),
        param('tr', "12 hafta", "12 week"),
        param('tr', "13 yıl", "13 year"),
        # Czech
        param('cs', "40 sekunda", "40 second"),
        param('cs', "4 týden", "4 week"),
        param('cs', "14 roků", "14 year"),
        # Chinese
        param('zh', "昨天", "1 day"),
        param('zh', "前天", "2 day"),
        param('zh', "50 秒", "50 second"),
        param('zh', "7 周", "7 week"),
        param('zh', "12 年", "12 year"),
        param('zh', "半小时前", "30 minute ago"),
        # Danish
        param('da', "i går", "1 day"),
        param('da', "i dag", "0 day"),
        param('da', "sidste måned", "1 month"),
        param('da', "mindre end et minut siden", "45  seconds"),
        # Dutch
        param('nl', "17 uur geleden", "17 hour ago"),
        param('nl', "27 jaar geleden", "27 year ago"),
        param('nl', "45 minuten", "45 minute"),
        param('nl', "nu", "0 second"),
        param('nl', "eergisteren", "2 day"),
        param('nl', "volgende maand", "in 1 month"),
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
        param('ar', "اليوم السابق", "1 day"),
        param('ar', "اليوم", "0 day"),
        # Polish
        param('pl', "2 godz.", "2 hour"),
        param('pl', "Wczoraj o 07:40", "1 day  07:40"),
        param('pl', "Poniedziałek 8:10 pm", "monday 8:10 pm"),
        # Vietnamese
        param('vi', "2 tuần 3 ngày", "2 week 3 day"),
        param('vi', "21 giờ trước", "21 hour ago"),
        param('vi', "Hôm qua 08:16", "1 day 08:16"),
        param('vi', "Hôm nay 15:39", "0 day 15:39"),
        # French
        param('fr', "maintenant", "0 second"),
        param('fr', "demain", "in 1 day"),
        param('fr', u"Il y a moins d'une minute", "ago 1  minute"),
        param('fr', u"Il y a moins de 30s", "ago 30 second"),
        # Tagalog
        param('tl', "kahapon", "1 day"),
        param('tl', "ngayon", "0 second"),
        # Ukrainian
        param('uk', "позавчора", "2 day"),
        # Belarusian
        param('be', "9 месяцаў", "9 month"),
        param('be', "8 тыдняў", "8 week"),
        param('be', "1 тыдзень", "1 week"),
        param('be', "2 года", "2 year"),
        param('be', "3 гады", "3 year"),
        param('be', "11 секунд", "11 second"),
        param('be', "учора", "1 day"),
        param('be', "пазаўчора", "2 day"),
        param('be', "сёння", "0 day"),
        param('be', "некалькі хвілін", "2 minute"),
        # Indonesian
        param('id', "baru saja", "0 second"),
        param('id', "hari ini", "0 day"),
        param('id', "kemarin", "1 day"),
        param('id', "kemarin lusa", "2 day"),
        param('id', "sehari yang lalu", "1 day  ago"),
        param('id', "seminggu yang lalu", "1 week  ago"),
        param('id', "sebulan yang lalu", "1 month  ago"),
        param('id', "setahun yang lalu", "1 year  ago"),
        # Finnish
        param('fi', "1 vuosi sitten", "1 year ago"),
        param('fi', "2 vuotta sitten", "2 year ago"),
        param('fi', "3 v sitten", "3 year ago"),
        param('fi', "4 v. sitten", "4 year ago"),
        param('fi', "5 vv. sitten", "5 year ago"),
        param('fi', "1 kuukausi sitten", "1 month ago"),
        param('fi', "2 kuukautta sitten", "2 month ago"),
        param('fi', "3 kk sitten", "3 month ago"),
        param('fi', "1 viikko sitten", "1 week ago"),
        param('fi', "2 viikkoa sitten", "2 week ago"),
        param('fi', "3 vk sitten", "3 week ago"),
        param('fi', "4 vko sitten", "4 week ago"),
        param('fi', "1 päivä sitten", "1 day ago"),
        param('fi', "2 päivää sitten", "2 day ago"),
        param('fi', "8 pvää sitten", "8 day ago"),
        param('fi', "3 pv sitten", "3 day ago"),
        param('fi', "4 p. sitten", "4 day ago"),
        param('fi', "5 pvä sitten", "5 day ago"),
        param('fi', "1 tunti sitten", "1 hour ago"),
        param('fi', "2 tuntia sitten", "2 hour ago"),
        param('fi', "3 t sitten", "3 hour ago"),
        param('fi', "1 minuutti sitten", "1 minute ago"),
        param('fi', "2 minuuttia sitten", "2 minute ago"),
        param('fi', "3 min sitten", "3 minute ago"),
        param('fi', "1 sekunti sitten", "1 second ago"),
        param('fi', "2 sekuntia sitten", "2 second ago"),
        param('fi', "1 sekuntti sitten", "1 second ago"),
        param('fi', "2 sekunttia sitten", "2 second ago"),
        param('fi', "3 s sitten", "3 second ago"),
        param('fi', "eilen", "1 day ago"),
        param('fi', "tänään", "0 day ago"),
        param('fi', "huomenna", "in 1 day"),
        param('fi', "nyt", "0 second"),
        param('fi', "ensi viikolla", "in 1 week"),
        param('fi', "viime viikolla", "1 week ago"),
        param('fi', "toissa vuonna", "2 year ago"),
        param('fi', "9 kuukautta sitten", "9 month ago"),
        param('fi', "3 viikon päästä", "in 3 week"),
        param('fi', "10 tunnin kuluttua", "in 10 hour"),
        # Japanese
        param('ja', "今年", "0 year"),
        param('ja', "去年", "1 year"),
        param('ja', "17年前", "17 year ago"),
        param('ja', "今月", "0 month"),
        param('ja', "先月", "1 month"),
        param('ja', "1ヶ月前", "1 month ago"),
        param('ja', "2ヶ月前", "2 month ago"),
        param('ja', "今週", "0 week"),
        param('ja', "先週", "1 week"),
        param('ja', "先々週", "2 week"),
        param('ja', "2週間前", "2 week ago"),
        param('ja', "3週間", "3 week"),
        param('ja', "今日", "0 day"),
        param('ja', "昨日", "1 day"),
        param('ja', "一昨日", "2 day"),
        param('ja', "3日前", "3 day ago"),
        param('ja', "1時間", "1 hour"),
        param('ja', "23時間前", "23 hour ago"),
        param('ja', "30分", "30 minute"),
        param('ja', "3分間", "3 minute"),
        param('ja', "60秒", "60 second"),
        param('ja', "3秒前", "3 second ago"),
        param('ja', "現在", "now"),
        # Hebrew
        param('he', "אתמול", "1 day"),
        param('he', "אתמול בשעה 3", "1 day  3"),
        param('he', "היום", "0 day"),
        param('he', "לפני יומיים", "ago 2 day"),
        param('he', "לפני שבועיים", "ago 2 week"),
        # Bulgarian
        param("bg", "вдругиден", "in 2 day"),
        param("bg", "утре", "in 1 day"),
        param("bg", "след 5 дни", "in 5 day"),
        param("bg", "вчера", "ago 1 day"),
        param("bg", "преди 9 дни", "ago 9 day"),
        param("bg", "преди 10 минути", "ago 10 minute"),
        param("bg", "преди час", "ago 1 hour"),
        param("bg", "преди 4 години", "ago 4 year"),
        param("bg", "преди десетилетие", "ago 10 year"),
        # Bangla
        param('bn', "গতকাল", "1 day"),
        param('bn', "আজ", "0 days"),
        param('bn', "গত মাস", "1 month"),
        param('bn', "আগামী সপ্তাহ", "in 1 week"),
        # Hindi
        param('hi', "१ सप्ताह", "1 week"),
        param('hi', "२४ मिनट पहले", "24 minute ago"),
        param('hi', "पांच वर्ष", "5 year"),
        param('hi', "५३ सप्ताह बाद", "53 week in"),
        param('hi', "सन् १९२०", " 1920"),
        param('hi', "आठ पूर्वाह्न", "8 am"),
        param('hi', "बारह सेकंड पूर्व", "12 second ago"),
        # Swedish
        param('sv', "igår", "1 day"),
        param('sv', "idag", "0 day"),
        param('sv', "förrgår", "2 day"),
        param('sv', "förra månaden", "1 month"),
        param('sv', "nästa månad", "in 1 month"),
        # Georgian
        param('ka', 'გუშინ', '1 day'),
        param('ka', 'დღეს', '0 day'),
        param('ka', 'ერთ თვე', '1 month'),
        param('ka', 'დღეიდან ერთ კვირა', 'in 1 week'),
    ])
    def test_freshness_translation(self, shortname, datetime_string, expected_translation):
        # Finnish language use "t" as hour, so empty SKIP_TOKENS.
        if shortname == 'fi':
            skip_tokens = settings.SKIP_TOKENS
            settings.SKIP_TOKENS = []
        settings.NORMALIZE = False
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

        # Return the default SKIP_TOKENS.
        if shortname == 'fi':
            settings.SKIP_TOKENS = skip_tokens

    @parameterized.expand([
        param('pt', "sexta-feira, 10 de junho de 2014 14:52",
              ["sexta-feira", " ", "10", " ", "de", " ", "junho", " ", "de", " ", "2014", " ", "14", ":", "52"]),
        param('it', "14_luglio_15", ["14", "luglio", "15"]),
        param('zh', "1年11个月", ["1", "年", "11", "个月"]),
        param('zh', "1年11個月", ["1", "年", "11", "個月"]),
        param('tr', "2 saat önce", ["2", " ", "saat", " ", "önce"]),
        param('fr', "il ya environ 23 heures'", ["il ya", " ", "environ", " ", "23", " ", "heures"]),
        param('de', "Gestern um 04:41", ['Gestern ', 'um', ' ', '04', ':', '41']),
        param('de', "Donnerstag, 8. Januar 2015 um 07:17",
              ['Donnerstag', ' ', '8', '.', ' ', 'Januar', ' ', '2015', ' ', 'um', ' ', '07', ':', '17']),
        param('ru', "8 января 2015 г. в 9:10",
              ['8', ' ', 'января', ' ', '2015', ' ', 'г.', ' ', 'в', ' ', '9', ':', '10']),
        param('cs', "6. leden 2015 v 22:29", ['6', '.', ' ', 'leden', ' ', '2015', ' ', 'v', ' ', '22', ':', '29']),
        param('nl', "woensdag 7 januari 2015 om 21:32",
              ['woensdag', ' ', '7', ' ', 'januari', ' ', '2015', ' ', 'om', ' ', '21', ':', '32']),
        param('ro', "8 Ianuarie 2015 la 13:33", ['8', ' ', 'Ianuarie', ' ', '2015', ' ', 'la', ' ', '13', ':', '33']),
        param('ar', "8 يناير، 2015، الساعة 10:01 صباحاً",
              ['8', ' ', 'يناير', ' ', '2015', 'الساعة', ' ', '10', ':', '01', ' صباحاً']),
        param('th', "8 มกราคม 2015 เวลา 12:22 น.",
              ['8', ' ', 'มกราคม', ' ', '2015', ' ', 'เวลา', ' ', '12', ':', '22', ' ', 'น.']),
        param('pl', "8 stycznia 2015 o 10:19", ['8', ' ', 'stycznia', ' ', '2015', ' ', 'o', ' ', '10', ':', '19']),
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015",
              ["Thứ Năm", " ", "ngày", " ", "8", " tháng ", "1", " ", "năm", " ", "2015"]),
        param('tl', "Biyernes Hulyo 3 2015", ["Biyernes", " ", "Hulyo", " ", "3", " ", "2015"]),
        param('be', "3 верасня 2015 г. у 11:10",
              ['3', ' ', 'верасня', ' ', '2015', ' ', 'г.', ' ', 'у', ' ', '11', ':', '10']),
        param('id', "3 Juni 2015 13:05:46", ['3', ' ', 'Juni', ' ', '2015', ' ', '13', ':', '05', ':', '46']),
        param('he', "ה-21 לאוקטובר 2016 ב-15:00",
              ['ה-', '21', ' ', 'לאוקטובר', ' ', '2016', ' ', 'ב-', '15', ':', '00']),
        param('bn', "3 জুন 2015 13:05:46", ['3', ' ', 'জুন', ' ', '2015', ' ', '13', ':', '05', ':', '46']),
        param('hi', "13 मार्च 2013 11:15:09", ['13', ' ', 'मार्च', ' ', '2013', ' ', '11', ':', '15', ':', '09']),
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
        param('da', "Torsdag, 8. januar 2015 kl. 07:17", strip_timezone=False),
        param('ru', "8 января 2015 г. в 9:10", strip_timezone=False),
        param('cs', "Pondělí v 22:29", strip_timezone=False),
        param('nl', "woensdag 7 januari om 21:32", strip_timezone=False),
        param('ro', "8 Ianuarie 2015 la 13:33", strip_timezone=False),
        param('ar', "ساعتين", strip_timezone=False),
        param('tr', "3 hafta", strip_timezone=False),
        param('th', "17 เดือนมิถุนายน", strip_timezone=False),
        param('pl', "przedwczoraj", strip_timezone=False),
        param('fa', "ژانویه 8, 2015، ساعت 15:46", strip_timezone=False),
        param('vi', "2 tuần 3 ngày", strip_timezone=False),
        param('tl', "Hulyo 3, 2015 7:00 pm", strip_timezone=False),
        param('be', "3 верасня 2015 г. у 11:10", strip_timezone=False),
        param('id', "01 Agustus 2015 18:23", strip_timezone=False),
        param('he', "6 לדצמבר 1973", strip_timezone=False),
        param('bn', "3 সপ্তাহ", strip_timezone=False),
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
        param('cs', "3 hafta", strip_timezone=False),
    ])
    def test_not_applicable_languages(self, shortname, datetime_string, strip_timezone):
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_not_applicable()

    def given_string(self, datetime_string):
        if settings.NORMALIZE:
            datetime_string = normalize_unicode(datetime_string)
        self.datetime_string = datetime_string

    def given_bundled_language(self, shorname):
        self.language = default_language_loader.get_language(shorname)

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(self.datetime_string, settings=settings)

    def when_datetime_string_splitted(self, keep_formatting=False):
        self.tokens = self.language._split(self.datetime_string, keep_formatting, settings=settings)

    def when_datetime_string_checked_if_applicable(self, strip_timezone):
        self.result = self.language.is_applicable(self.datetime_string, strip_timezone, settings=settings)

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
        for _ in self.detector.iterate_applicable_languages(datetime_string, modify=True, settings=settings):
            break

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def given_detector(self):
        raise NotImplementedError

    def when_searching_for_first_applicable_language(self):
        for language in self.detector.iterate_applicable_languages(self.datetime_string, modify=True,
                                                                   settings=settings):
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
        self.exact_languages = self.detector.iterate_applicable_languages(self.datetime_string, modify=True,
                                                                          settings=settings)

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


class TestLanguageValidatorWhenInvalid(BaseTestCase):
    def setUp(self):
        super(TestLanguageValidatorWhenInvalid, self).setUp()
        self.validator = LanguageValidator

    @parameterized.expand([
        param('en', 'string instead of dict'),
    ])
    def test_validate_info_when_invalid_tipe(self, lang_id, lang_info):
        result = self.validator.validate_info(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),
        param('en', {'name': 22}),
        param('en', {'name': ''}),
    ])
    def test_validate_name_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_name(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {'no_word_spacing': 'string instead of bool'}),
    ])
    def test_validate_word_spacing_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_word_spacing(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {'skip': 'string instead of list'}),
        param('en', {'skip': ['']}),
    ])
    def test_validate_skip_list_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_skip_list(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),

    ])
    def test_validate_skip_list_when_abscent(self, lang_id, lang_info):
        result = self.validator._validate_skip_list(lang_id, lang_info)
        self.assertTrue(result)

    # @parameterized.expand([
    #     param('en', {'pertain': 'string instead of list'}),
    #     param('en', {'pertain': ['']}),
    # ])
    # def test_validate_pertain_list_when_invalid(self, lang_id, lang_info):
    #     result = self.validator._validate_pertain_list(lang_id, lang_info)
    #     self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),
        param('en',
              {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 7}),
        param('en', {'monday': [1], 'tuesday': [2], 'wednesday': [3], 'thursday': [4], 'friday': [5],
                     'saturday': [6], 'sunday': [7]}),
    ])
    def test_validate_weekdays_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_weekdays(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),
        param('en',
              {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7,
               'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12}),
        param('en',
              {'january': [1], 'february': [2], 'march': [3], 'april': [4], 'may': [5], 'june': [6], 'july': [7],
               'august': [8], 'september': [9], 'october': [10], 'november': [11], 'december': [12]}),
    ])
    def test_validate_months_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_months(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),
        param('en',
              {'year': 1, 'month': 2, 'week': 3, 'day': 4, 'hour': 5, 'minute': 6, 'second': 7}),
        param('en',
              {'year': [1], 'month': [2], 'week': [3], 'day': [4], 'hour': [5], 'minute': [6], 'second': [7]}),
    ])
    def test_validate_units_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_units(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),
        param('en',
              {'ago': 1}),
        param('en',
              {'ago': []}),
        param('en',
              {'ago': ['']}),
    ])
    def test_validate_other_words_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_other_words(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {}),

    ])
    def test_validate_simplifications_when_abscent(self, lang_id, lang_info):
        result = self.validator._validate_simplifications(lang_id, lang_info)
        self.assertTrue(result)

    @parameterized.expand([
        param('en',
              {'simplifications': 'string instead of list'}),
        param('en',
              {'simplifications': [{}]}),
        param('en',
              {'simplifications': [{28: []}]}),
        param('en',
              {'simplifications': [{'simplification': []}]}),
        # groups were not used
        param('en',
              {'simplifications': [{'(\d+)\s*hr(s?)\g<(.+?)>': r'\1 hour\2'}]}),
        #
        param('en',
              {'simplifications': [{'(one)(two)(three)': r'\1\3\2\4'}]}),
        param('en',
              {'simplifications': [{r'(?P<A>\w+)(?P<B>\w+)': '\\g<A>'}]}),
        param('en',
              {'simplifications': [{r'(?P<A>\w+)': '\\g<B>(.*?)'}]}),

    ])
    def test_validate_simplifications_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_simplifications(lang_id, lang_info)
        self.assertFalse(result)

    @parameterized.expand([
        param('en', {'invalid_key': ''}),

    ])
    def test_validate_extra_keys_when_invalid(self, lang_id, lang_info):
        result = self.validator._validate_extra_keys(lang_id, lang_info)
        self.assertFalse(result)
