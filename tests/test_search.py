from nose_parameterized import parameterized, param
from tests import BaseTestCase
from dateparser.search import ExactLanguageSearch


class TestTranslateSearch(BaseTestCase):

    def setUp(self):
        super(TestTranslateSearch, self).setUp()
        self.els = ExactLanguageSearch()

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
        param('hu', '2016 augusztus 11', '2016 august 11.'),
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
        param('cs', "22. prosinec 2014 v 2:38", "22. december 2014  2:38""22. prosinec 2014 v 2:38", "22. december 2014  2:38"),
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
    def test_search_date_string(self, shortname, datetime_string, expected_translation):
        result2 = self.els.search(shortname, datetime_string)[1][0]
        self.assertEqual(result2, datetime_string)

    @parameterized.expand([
        param('en', 'Game 1 is July 12, 2017. Game 2 on July 13th. Game 3 on July 15th',
              (['july 12, 2017', 'july 13th', 'july 15th'],
               ['July 12, 2017', 'on July 13th', 'on July 15th'])),
        param('en', 'I will meet you tomorrow at noon',
              (['in 1 day 12:00'], ['tomorrow at noon'])),
        param('en', 'January 3, 2017 - February 1st',
              (['january 3, 2017', 'february 1st'], ['January 3, 2017', 'February 1st'])),
        param('en', 'in a minute',
              (['in 1 minute'], ['in a minute'])),
        param('en', 'July 13th.\r\n July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        param('en', 'July 13th, July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        param('en', 'July 13th July 14th',
              (['july 13th', 'july 14th'], ['July 13th', 'July 14th'])),
        ])
    def test_search_text(self, shortname, string, expected):
        result = self.els.search(shortname, string)
        self.assertEqual(result, expected)



