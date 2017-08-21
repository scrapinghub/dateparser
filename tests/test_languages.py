# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nose_parameterized import parameterized, param

from dateparser.languages import default_loader
from dateparser.conf import apply_settings
from dateparser.utils import normalize_unicode

from tests import BaseTestCase


class TestBundledLanguages(BaseTestCase):
    def setUp(self):
        super(TestBundledLanguages, self).setUp()
        self.language = NotImplemented
        self.datetime_string = NotImplemented
        self.translation = NotImplemented
        self.tokens = NotImplemented
        self.result = NotImplemented
        self.settings = NotImplemented

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
        param('ru', "5 августа 2014 г. в 12:00", "5 august 2014 year.  12:00"),
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
        param('be', "5 снежня 2015 г. у 12:00", "5 december 2015 year.  12:00"),
        param('be', "11 верасня 2015 г. у 12:11", "11 september 2015 year.  12:11"),
        param('be', "3 стд 2015 г. у 10:33", "3 january 2015 year.  10:33"),
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

        # af
        param('af', '5 Mei 2017', '5 may 2017'),
        param('af', 'maandag, Augustus 15 2005 10 vm', 'monday august 15 2005 10 am'),

        # agq
        param('agq', '12 ndzɔ̀ŋɔ̀tɨ̀fʉ̀ghàdzughù 1999', '12 september 1999'),
        param('agq', 'tsuʔndzɨkɔʔɔ 14 see 10 ak', 'saturday 14 may 10 pm'),

        # ak
        param('ak', 'esusow aketseaba-kɔtɔnimba', 'may'),
        param('ak', '8 mumu-ɔpɛnimba ben', '8 december tuesday'),

        # am
        param('am', 'ፌብሩወሪ 22 8:00 ጥዋት', 'february 22 8:00 am'),
        param('am', 'ኖቬም 10', 'november 10'),

        # as
        param('as', '17 জানুৱাৰী 1885', '17 january 1885'),
        param('as', 'বৃহষ্পতিবাৰ 1 জুলাই 2009', 'thursday 1 july 2009'),

        # asa
        param('asa', '12 julai 1879 08:00 ichamthi', '12 july 1879 08:00 pm'),
        param('asa', 'jpi 2 desemba 2007 01:00 icheheavo', 'sunday 2 december 2007 01:00 am'),

        # ast
        param('ast', "d'ochobre 11, 11:00 de la mañana", 'october 11 11:00 am'),
        param('ast', "vienres 19 payares 1 tarde", 'friday 19 november 1 pm'),

        # az-Cyrl
        param('az-Cyrl', "7 феврал 1788 05:30 пм", '7 february 1788 05:30 pm'),
        param('az-Cyrl', "чәршәнбә ахшамы ијл 14", 'tuesday july 14'),

        # az-Latn
        param('az-Latn', 'yanvar 13 şənbə', 'january 13 saturday'),
        param('az-Latn', 'b noy 12', 'sunday november 12'),

        # az
        param('az', "17 iyn 2000 cümə axşamı", '17 june 2000 thursday'),
        param('az', "22 sentyabr 2003 bazar ertəsi", '22 september 2003 monday'),

        # bas
        param('bas', '1906 6 hìlòndɛ̀ ŋgwà njaŋgumba', '1906 6 june monday'),
        param('bas', 'ŋgwà kɔɔ, 11 màtùmb 5 i ɓugajɔp', 'friday 11 march 5 pm'),

        # be
        param('be', '13 лютага 1913', '13 february 1913'),
        param('be', 'жнівень 12, чацвер', 'august 12 thursday'),

        # bem
        param('bem', 'palichimo 12 machi 2015 11:00 uluchelo', 'monday 12 march 2015 11:00 am'),
        param('bem', '5 epreo 2000 pa mulungu', '5 april 2000 sunday'),

        # bez
        param('bez', '1 pa mwedzi gwa hutala 1889 10:00 pamilau', '1 january 1889 10:00 am'),
        param('bez', '31 pa mwedzi gwa kumi na mbili hit', '31 december thursday'),

        # bm
        param('bm', '12 ɔkutɔburu 2001 araba', '12 october 2001 wednesday'),
        param('bm', 'alamisa 15 uti 1998', 'thursday 15 august 1998'),

        # bo
        param('bo', "ཟླ་བ་བཅུ་གཅིག་པ་ 18", 'november 18'),
        param('bo', "གཟའ་ཕུར་བུ་ 12 ཟླ་བ་བཅུ་པ་ 1879 10:15 ཕྱི་དྲོ་", 'thursday 12 october 1879 10:15 pm'),

        # br
        param('br', "merc'her c'hwevrer 12 07:32 gm", "wednesday february 12 07:32 pm"),
        param('br', "10 gwengolo 2002 sadorn", "10 september 2002 saturday"),

        # brx
        param('brx', "6 अखथबर 2019 10:00 बेलासे", "6 october 2019 10:00 pm"),
        param('brx', "बिसथि 8 फेब्रुवारी", "thursday 8 february"),

        # bs-Cyrl
        param('bs-Cyrl', "2 септембар 2000, четвртак", "2 september 2000 thursday"),
        param('bs-Cyrl', "1 јули 1987 9:25 поподне", "1 july 1987 9:25 pm"),

        # bs-Latn
        param('bs-Latn', "23 septembar 1879, petak 02:27 popodne", "23 september 1879 friday 02:27 pm"),
        param('bs-Latn', "subota 1 avg 2009", "saturday 1 august 2009"),

        # bs
        param('bs', "10 maj 2020 utorak", "10 may 2020 tuesday"),
        param('bs', "ponedjeljak, 1989 2 januar", "monday 1989 2 january"),

        # ca
        param('ca', "14 d'abril 1980 diumenge", "14 april 1980 sunday"),
        param('ca', "3 de novembre 2004 dj", "3 november 2004 thursday"),

        # ce
        param('ce', "6 январь 1987 пӏераскан де", "6 january 1987 friday"),
        param('ce', "оршотан де 3 июль 1890", "monday 3 july 1890"),

        # cgg
        param('cgg', "20 okwakataana 2027 orwamukaaga", "20 may 2027 saturday"),
        param('cgg', "okwaikumi na ibiri 12 oks", "december 12 wednesday"),

        # chr
        param('chr', "ᎤᎾᏙᏓᏉᏅᎯ 16 ᏕᎭᎷᏱ 1562 11:16 ᏒᎯᏱᎢᏗᏢ", "monday 16 june 1562 11:16 pm"),
        param('chr', "13 ᎠᏂᏍᎬᏘ ᎤᎾᏙᏓᏈᏕᎾ 8:00 ᏌᎾᎴ", "13 may saturday 8:00 am"),

        # cy
        param('cy', "dydd sadwrn 27 chwefror 1990 9 yb", "saturday 27 february 1990 9 am"),
        param('cy', "19 gorff 2000 dydd gwener", "19 july 2000 friday"),

        # dav
        param('dav', "mori ghwa kawi 24 kuramuka kana", "february 24 thursday"),
        param('dav', "11 ike 4 luma lwa p", "11 september 4 pm"),

        # dje
        param('dje', "2 žuweŋ 2030 alz 11 zaarikay b", "2 june 2030 friday 11 pm"),
        param('dje', "sektanbur 12 alarba", "september 12 wednesday"),

        # dsb
        param('dsb', "njeźela julija 15 2 wótpołdnja", "sunday july 15 2 pm"),
        param('dsb', "awgusta 10 sob", "august 10 saturday"),

        # dua
        param('dua', "madiɓɛ́díɓɛ́ 15 ɗónɛsú 7 idiɓa", "july 15 friday 7 am"),
        param('dua', "éti 12 tiníní", "sunday 12 november"),

        # dyo
        param('dyo', "mee 1 2000 talata", "may 1 2000 tuesday"),
        param('dyo', "arjuma de 10", "friday december 10"),

        # dz
        param('dz', "ཟླ་བཅུ་གཅིག་པ་ 10 གཟའ་ཉི་མ་", "november 10 saturday"),
        param('dz', "མིར་ 2 སྤྱི་ཟླ་དྲུག་པ 2009 2 ཕྱི་ཆ་", "monday 2 june 2009 2 pm"),
    ])
    def test_translation(self, shortname, datetime_string, expected_translation):
        self.given_settings()
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

    @parameterized.expand([
        # English
        param('en', "yesterday", "1 day ago"),
        param('en', "today", "0 day ago"),
        param('en', "day before yesterday", "2 day ago"),
        param('en', "last month", "1 month ago"),
        param('en', "less than a minute ago", "45 second ago"),
        # German
        param('de', "vorgestern", "2 day ago"),
        param('de', "heute", "0 day ago"),
        param('de', "vor 3 Stunden", "3 hour ago"),
        param('de', "vor 2 Monaten", "2 month ago"),
        param('de', "vor 2 Monaten, 2 Wochen", "2 month ago 2 week"),
        # French
        param('fr', "avant-hier", "2 day ago"),
        param('fr', "hier", "1 day ago"),
        param('fr', "aujourd'hui", "0 day ago"),
        # Spanish
        param('es', "anteayer", "2 day ago"),
        param('es', "ayer", "1 day ago"),
        param('es', "ayer a las", "1 day ago "),
        param('es', "hoy", "0 day ago"),
        param('es', "hace un horas", "1 hour ago"),
        param('es', "2 semanas", "2 week"),
        param('es', "2 año", "2 year"),
        # Italian
        param('it', "altro ieri", "2 day ago"),
        param('it', "ieri", "1 day ago"),
        param('it', "oggi", "0 day ago"),
        param('it', "2 settimana fa", "2 week ago"),
        param('it', "2 anno fa", "2 year ago"),
        # Portuguese
        param('pt', "anteontem", "2 day ago"),
        param('pt', "ontem", "1 day ago"),
        param('pt', "hoje", "0 day ago"),
        param('pt', "56 minutos", "56 minute"),
        param('pt', "12 dias", "12 day"),
        param('pt', "há 14 min.", "14 minute ago."),
        param('pt', "1 segundo atrás", "1 second ago"),
        # Russian
        param('ru', "9 месяцев", "9 month"),
        param('ru', "8 недели", "8 week"),
        param('ru', "7 года", "7 year"),
        param('ru', "позавчера", "2 day ago"),
        param('ru', "сейчас", "0 second ago"),
        param('ru', "спустя 2 дня", "in 2 day"),
        param('ru', "вчера", "1 day ago"),
        param('ru', "сегодня", "0 day ago"),
        param('ru', "завтра", "in 1 day"),
        param('ru', "послезавтра", "in 2 day"),
        param('ru', "несколько секунд", "44 second"),
        # Turkish
        param('tr', "dün", "1 day ago"),
        param('tr', "22 dakika", "22 minute"),
        param('tr', "12 hafta", "12 week"),
        param('tr', "13 yıl", "13 year"),
        # Czech
        param('cs', "40 sekunda", "40 second"),
        param('cs', "4 týden", "4 week"),
        param('cs', "14 roků", "14 year"),
        # Chinese
        param('zh', "昨天", "1 day ago"),
        param('zh', "前天", "2 day ago"),
        param('zh', "50 秒", "50 second"),
        param('zh', "7 周", "7 week"),
        param('zh', "12 年", "12 year"),
        param('zh', "半小时前", "30 minute ago"),
        # Danish
        param('da', "i går", "1 day ago"),
        param('da', "i dag", "0 day ago"),
        param('da', "sidste måned", "1 month ago"),
        param('da', "mindre end et minut siden", "45  seconds"),
        # Dutch
        param('nl', "17 uur geleden", "17 hour ago"),
        param('nl', "27 jaar geleden", "27 year ago"),
        param('nl', "45 minuten", "45 minute"),
        param('nl', "nu", "0 second ago"),
        param('nl', "eergisteren", "2 day ago"),
        param('nl', "volgende maand", "in 1 month"),
        # Romanian
        param('ro', "23 săptămâni în urmă", "23 week ago"),
        param('ro', "23 săptămâni", "23 week"),
        param('ro', "13 oră", "13 hour"),
        # Arabic
        param('ar', "يومين", "2 day"),
        param('ar', "أمس", "1 day ago"),
        param('ar', "4 عام", "4 year"),
        param('ar', "منذ 2 ساعات", "ago 2 hour"),
        param('ar', "منذ ساعتين", "ago 2 hour"),
        param('ar', "اليوم السابق", "1 day ago"),
        param('ar', "اليوم", "0 day ago"),
        # Polish
        param('pl', "2 godz.", "2 hour."),
        param('pl', "Wczoraj o 07:40", "1 day ago  07:40"),
        # Vietnamese
        param('vi', "2 tuần 3 ngày", "2 week 3 day"),
        param('vi', "21 giờ trước", "21 hour ago"),
        param('vi', "Hôm qua 08:16", "1 day ago 08:16"),
        param('vi', "Hôm nay 15:39", "0 day ago 15:39"),
        # French
        param('fr', "maintenant", "0 second ago"),
        param('fr', "demain", "in 1 day"),
        param('fr', u"Il y a moins d'une minute", "1 minute ago"),
        param('fr', u"Il y a moins de 30s", "30 second ago"),
        # Tagalog
        param('tl', "kahapon", "1 day ago"),
        param('tl', "ngayon", "0 second ago"),
        # Ukrainian
        param('uk', "позавчора", "2 day ago"),
        # Belarusian
        param('be', "9 месяцаў", "9 month"),
        param('be', "8 тыдняў", "8 week"),
        param('be', "1 тыдзень", "1 week"),
        param('be', "2 года", "2 year"),
        param('be', "3 гады", "3 year"),
        param('be', "11 секунд", "11 second"),
        param('be', "учора", "1 day ago"),
        param('be', "пазаўчора", "2 day ago"),
        param('be', "сёння", "0 day ago"),
        param('be', "некалькі хвілін", "2 minute"),
        # Indonesian
        param('id', "baru saja", "0 second ago"),
        param('id', "hari ini", "0 day ago"),
        param('id', "kemarin", "1 day ago"),
        param('id', "kemarin lusa", "2 day ago"),
        param('id', "sehari yang lalu", "1 day  ago"),
        param('id', "seminggu yang lalu", "1 week  ago"),
        param('id', "sebulan yang lalu", "1 month  ago"),
        param('id', "setahun yang lalu", "1 year  ago"),
        # Finnish
        param('fi', "1 vuosi sitten", "1 year ago"),
        param('fi', "2 vuotta sitten", "2 year ago"),
        param('fi', "3 v sitten", "3 year ago"),
        param('fi', "4 v. sitten", "4 year. ago"),
        param('fi', "5 vv. sitten", "5 year. ago"),
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
        param('fi', "4 p. sitten", "4 day. ago"),
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
        param('fi', "nyt", "0 second ago"),
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
        param('ja', "現在", "0 second ago"),
        # Hebrew
        param('he', "אתמול", "1 day ago"),
        param('he', "אתמול בשעה 3", "1 day ago  3"),
        param('he', "היום", "0 day ago"),
        param('he', "לפני יומיים", "2 day ago"),
        param('he', "לפני שבועיים", "2 week ago"),
        # Bulgarian
        param("bg", "вдругиден", "in 2 day"),
        param("bg", "утре", "in 1 day"),
        param("bg", "след 5 дни", "in 5 day"),
        param("bg", "вчера", "1 day ago"),
        param("bg", "преди 9 дни", "9 day ago"),
        param("bg", "преди 10 минути", "10 minute ago"),
        param("bg", "преди час", "1 hour ago"),
        param("bg", "преди 4 години", "4 year ago"),
        param("bg", "преди десетилетие", "10 year ago"),
        # Bangla
        param('bn', "গতকাল", "1 day ago"),
        param('bn', "আজ", "0 day ago"),
        param('bn', "গত মাস", "1 month ago"),
        param('bn', "আগামী সপ্তাহ", "in 1 week"),
        # Hindi
        param('hi', "१ सप्ताह", "1 week"),
        param('hi', "२४ मिनट पहले", "24 minute ago"),
        param('hi', "5 वर्ष", "5 year"),
        param('hi', "५३ सप्ताह बाद", "53 week in"),
        param('hi', "12 सेकंड पूर्व", "12 second ago"),
        # Swedish
        param('sv', "igår", "1 day ago"),
        param('sv', "idag", "0 day ago"),
        param('sv', "förrgår", "2 day ago"),
        param('sv', "förra månaden", "1 month ago"),
        param('sv', "nästa månad", "in 1 month"),
        # Georgian
        param('ka', 'გუშინ', '1 day ago'),
        param('ka', 'დღეს', '0 day ago'),
        param('ka', 'ერთ თვე', '1 month'),
        param('ka', 'დღეიდან ერთ კვირა', 'in 1 week'),
    ])
    def test_freshness_translation(self, shortname, datetime_string, expected_translation):
        self.given_settings(settings={'NORMALIZE': False})
        # Finnish language use "t" as hour, so empty SKIP_TOKENS.
        if shortname == 'fi':
            self.settings.SKIP_TOKENS = []
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

    @parameterized.expand([
        param('pt', "sexta-feira, 10 de junho de 2014 14:52",
              ["sexta-feira", " ", "10", " ", "de", " ", "junho", " ", "de", " ", "2014", " ", "14", ":", "52"]),
        param('it', "14_luglio_15", ["14", "luglio", "15"]),
        param('zh', "1年11个月", ["1", "年", "11", "个月"]),
        param('zh', "1年11個月", ["1", "年", "11", "個月"]),
        param('tr', "2 saat önce", ["2 saat önce"]),
        param('fr', "il ya environ 23 heures'", ["il ya", " ", "environ", " ", "23", " ", "heures"]),
        param('de', "Gestern um 04:41", ['Gestern', ' ', 'um', ' ', '04', ':', '41']),
        param('de', "Donnerstag, 8. Januar 2015 um 07:17",
              ['Donnerstag', ' ', '8', '.', ' ', 'Januar', ' ', '2015', ' ', 'um', ' ', '07', ':', '17']),
        param('ru', "8 января 2015 г. в 9:10",
              ['8', ' ', 'января', ' ', '2015', ' ', 'г', '.', ' ', 'в', ' ', '9', ':', '10']),
        param('cs', "6. leden 2015 v 22:29", ['6', '.', ' ', 'leden', ' ', '2015', ' ', 'v', ' ', '22', ':', '29']),
        param('nl', "woensdag 7 januari 2015 om 21:32",
              ['woensdag', ' ', '7', ' ', 'januari', ' ', '2015', ' ', 'om', ' ', '21', ':', '32']),
        param('ro', "8 Ianuarie 2015 la 13:33", ['8', ' ', 'Ianuarie', ' ', '2015', ' ', 'la', ' ', '13', ':', '33']),
        param('ar', "8 يناير، 2015، الساعة 10:01 صباحاً",
              ['8', ' ', 'يناير', ' ', '2015', 'الساعة', ' ', '10', ':', '01',  ' ','صباحاً']),
        param('th', "8 มกราคม 2015 เวลา 12:22 น.",
              ['8', ' ', 'มกราคม', ' ', '2015', ' ', 'เวลา', ' ', '12', ':', '22', ' ', 'น.']),
        param('pl', "8 stycznia 2015 o 10:19", ['8', ' ', 'stycznia', ' ', '2015', ' ', 'o', ' ', '10', ':', '19']),
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015",
              ["Thứ Năm", " ", "ngày", " ", "8", " ", "tháng", " ", "1", " ", "năm", " ", "2015"]),
        param('tl', "Biyernes Hulyo 3 2015", ["Biyernes", " ", "Hulyo", " ", "3", " ", "2015"]),
        param('be', "3 верасня 2015 г. у 11:10",
              ['3', ' ', 'верасня', ' ', '2015', ' ', 'г', '.', ' ', 'у', ' ', '11', ':', '10']),
        param('id', "3 Juni 2015 13:05:46", ['3', ' ', 'Juni', ' ', '2015', ' ', '13', ':', '05', ':', '46']),
        param('he', "ה-21 לאוקטובר 2016 ב-15:00",
              ['ה-', '21', ' ', 'לאוקטובר', ' ', '2016', ' ', 'ב-', '15', ':', '00']),
        param('bn', "3 জুন 2015 13:05:46", ['3', ' ', 'জুন', ' ', '2015', ' ', '13', ':', '05', ':', '46']),
        param('hi', "13 मार्च 2013 11:15:09", ['13', ' ', 'मार्च', ' ', '2013', ' ', '11', ':', '15', ':', '09']),
    ])
    def test_date_tokens(self, shortname, datetime_string, expected_tokens):
        self.given_settings(settings={'NORMALIZE': False})
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
        self.given_settings()
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
        self.given_settings()
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_checked_if_applicable(strip_timezone)
        self.then_language_is_not_applicable()

    @apply_settings
    def given_settings(self, settings=None):
        self.settings = settings

    def given_string(self, datetime_string):
        if self.settings.NORMALIZE:
            datetime_string = normalize_unicode(datetime_string)
        self.datetime_string = datetime_string

    def given_bundled_language(self, shortname):
        self.language = default_loader.get_locale(shortname)

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(self.datetime_string, settings=self.settings)

    def when_datetime_string_splitted(self, keep_formatting=False):
        self.tokens = self.language._get_date_tokens(self.datetime_string, keep_formatting,
                                                     settings=self.settings)

    def when_datetime_string_checked_if_applicable(self, strip_timezone):
        self.result = self.language.is_applicable(self.datetime_string, strip_timezone,
                                                  settings=self.settings)

    def then_string_translated_to(self, expected_string):
        self.assertEqual(expected_string, self.translation)

    def then_tokens_are(self, expected_tokens):
        self.assertEqual(expected_tokens, self.tokens)

    def then_language_is_applicable(self):
        self.assertTrue(self.result)

    def then_language_is_not_applicable(self):
        self.assertFalse(self.result)
