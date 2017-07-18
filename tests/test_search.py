# -*- coding: utf-8 -*-
from nose_parameterized import parameterized, param
from tests import BaseTestCase
from dateparser.search import ExactLanguageSearch
import datetime


class TestTranslateSearch(BaseTestCase):
    def setUp(self):
        super(TestTranslateSearch, self).setUp()
        self.els = ExactLanguageSearch()

    @parameterized.expand([
        param('en', "Sep 03 2014"),
        param('en', "friday, 03 september 2014"),
        # Chinese
        param('zh', "1年11个月"),
        param('zh', "1年11個月"),
        param('zh', "2015年04月08日10点05"),
        param('zh', "2015年04月08日10:05"),
        param('zh', "2013年04月08日"),
        param('zh', "周一"),
        param('zh', "礼拜一"),
        param('zh', "周二"),
        param('zh', "礼拜二"),
        param('zh', "周三"),
        param('zh', "礼拜三"),
        param('zh', "星期日 2015年04月08日10:05"),
        param('zh', "周六 2013年04月08日"),
        param('zh', "下午3:30"),
        param('zh', "凌晨3:30"),
        param('zh', "中午"),
        # French
        param('fr', "20 Février 2012"),
        param('fr', "Mercredi 19 Novembre 2013"),
        param('fr', "18 octobre 2012 à 19 h 21 min"),
        # German
        param('de', "29. Juni 2007"),
        param('de', "Montag 5 Januar, 2015"),
        # Hungarian
        param('hu', '2016 augusztus 11'),
        param('hu', '2016-08-13 szombat 10:21'),
        param('hu', '2016. augusztus 14. vasárnap 10:21'),
        param('hu', 'hétfő'),
        param('hu', 'tegnapelőtt'),
        param('hu', 'ma'),
        param('hu', '2 hónappal ezelőtt'),
        param('hu', '2016-08-13 szombat 10:21 GMT'),
        # Spanish
        param('es', "Miércoles 31 Diciembre 2014"),
        # Italian
        param('it', "Giovedi Maggio 29 2013"),
        param('it', "19 Luglio 2013"),
        # Portuguese
        param('pt', "22 de dezembro de 2014 às 02:38"),
        # Russian
        param('ru', "5 августа 2014 г. в 12:00"),
        # Turkish
        param('tr', "2 Ocak 2015 Cuma, 16:49"),
        # Czech
        param('cs', "22. prosinec 2014 v 2:38"),
        # Dutch
        param('nl', "maandag 22 december 2014 om 2:38"),
        # Romanian
        param('ro', "22 Decembrie 2014 la 02:38"),
        # Polish
        param('pl', "4 stycznia o 13:50"),
        param('pl', "29 listopada 2014 o 08:40"),
        # Ukrainian
        param('uk', "30 листопада 2013 о 04:27"),
        # Belarusian
        param('be', "5 снежня 2015 г. у 12:00"),
        param('be', "11 верасня 2015 г. у 12:11"),
        param('be', "3 стд 2015 г. у 10:33"),
        # Arabic
        param('ar', "6 يناير، 2015، الساعة 05:16 مساءً"),
        param('ar', "7 يناير، 2015، الساعة 11:00 صباحاً"),
        # Vietnamese
        param('vi', "Thứ Năm, ngày 8 tháng 1 năm 2015"),
        param('vi', "Thứ Tư, 07/01/2015 | 22:34"),
        param('vi', "9 Tháng 1 2015 lúc 15:08"),
        # Thai
        param('th', "เมื่อ กุมภาพันธ์ 09, 2015, 09:27:57 AM"),
        param('th', "เมื่อ กรกฎาคม 05, 2012, 01:18:06 AM"),

        # Tagalog
        param('tl', "Biyernes Hulyo 3, 2015"),
        param('tl', "Pebrero 5, 2015 7:00 pm"),
        # Indonesian
        param('id', "06 Sep 2015"),
        param('id', "07 Feb 2015 20:15"),

        # Miscellaneous
        param('en', "2014-12-12T12:33:39-08:00"),
        param('en', "2014-10-15T16:12:20+00:00"),
        param('en', "28 Oct 2014 16:39:01 +0000"),
        param('es', "13 Febrero 2015 a las 23:00"),

        # Danish
        param('da', "Sep 03 2014"),
        param('da', "fredag, 03 september 2014"),
        param('da', "fredag d. 3 september 2014"),

        # Finnish
        param('fi', "maanantai tammikuu 16, 2015"),
        param('fi', "ma tammi 16, 2015"),
        param('fi', "tiistai helmikuu 16, 2015"),
        param('fi', "ti helmi 16, 2015"),
        param('fi', "keskiviikko maaliskuu 16, 2015"),
        param('fi', "ke maalis 16, 2015"),
        param('fi', "torstai huhtikuu 16, 2015"),
        param('fi', "to huhti 16, 2015"),
        param('fi', "perjantai toukokuu 16, 2015"),
        param('fi', "pe touko 16, 2015"),
        param('fi', "lauantai kesäkuu 16, 2015"),
        param('fi', "la kesä 16, 2015"),
        param('fi', "sunnuntai heinäkuu 16, 2015"),
        param('fi', "su heinä 16, 2015"),
        param('fi', "su elokuu 16, 2015"),
        param('fi', "su elo 16, 2015"),
        param('fi', "su syyskuu 16, 2015"),
        param('fi', "su syys 16, 2015"),
        param('fi', "su lokakuu 16, 2015"),
        param('fi', "su loka 16, 2015"),
        param('fi', "su marraskuu 16, 2015"),
        param('fi', "su marras 16, 2015"),
        param('fi', "su joulukuu 16, 2015"),
        param('fi', "su joulu 16, 2015"),
        param('fi', "1. tammikuuta, 2016"),
        param('fi', "tiistaina, 27. lokakuuta 2015"),

        # Japanese
        param('ja', "午後3時"),
        param('ja', "2時"),
        param('ja', "11時42分"),
        param('ja', "3ヶ月"),
        param('ja', "約53か月前"),
        param('ja', "3月"),
        param('ja', "十二月"),
        param('ja', "2月10日"),
        param('ja', "2013年2月"),
        param('ja', "2013年04月08日"),
        param('ja', "2016年03月24日 木曜日 10時05分"),
        param('ja', "2016年3月20日 21時40分"),
        param('ja', "2016年03月21日 23時05分11秒"),
        param('ja', "2016年3月21日(月) 14時48分"),
        param('ja', "2016年3月20日(日) 21時40分"),
        param('ja', "2016年3月20日 (日) 21時40分"),

        # Hebrew
        param('he', "20 לאפריל 2012"),
        param('he', "יום רביעי ה-19 בנובמבר 2013"),
        param('he', "18 לאוקטובר 2012 בשעה 19:21"),
        param('he', "יום ה' 6/10/2016"),
        param('he', "חצות"),
        param('he', "1 אחר חצות"),
        param('he', "3 לפנות בוקר"),
        param('he', "3 בבוקר"),
        param('he', "3 בצהריים"),
        param('he', "6 לפנות ערב"),
        param('he', "6 אחרי הצהריים"),
        param('he', "6 אחרי הצהרים"),

        # Bangla
        param('bn', "সেপ্টেম্বর 03 2014"),
        param('bn', "শুক্রবার, 03 সেপ্টেম্বর 2014"),

        # Hindi
        param('hi', 'सोमवार 13 जून 1998'),
        param('hi', 'मंगल 16 1786 12:18'),
        param('hi', 'शनि 11 अप्रैल 2002 03:09'),

        # Swedish
        param('sv', "Sept 03 2014"),
        param('sv', "fredag, 03 september 2014"),
    ])
    def test_search_date_string(self, shortname, datetime_string):
        result = self.els.search(shortname, datetime_string)[1][0]
        self.assertEqual(result, datetime_string)

    @parameterized.expand([
        # Arabic
        param('ar', 'في 29 يوليو 1938 غزت القوات اليابانية الاتحاد'
                    ' السوفييتي ووقعت أولى المعارك والتي انتصر فيها السوفييت، وعلى الرغم من ذلك رفضت'
                    ' اليابان الاعتراف بذلك وقررت في 11 مايو 1939 تحريك الحدود المنغولية حتى نهر غول،'
                    ' حيث وقعت معركة خالخين غول والتي انتصر فيها الجيش الأحمر على جيش كوانتونغ',
              [('في 29 يوليو 1938', datetime.datetime(1938, 7, 29, 0, 0)),
               ('في 11 مايو 1939', datetime.datetime(1939, 5, 11, 0, 0))]),

        # Belarusian
        param('be', 'Пасля апублікавання Патсдамскай дэкларацыі 26 ліпеня 1945 года і адмовы Японіі капітуляваць '
                    'на яе ўмовах ЗША скінулі атамныя бомбы.',
              [('26 ліпеня 1945 года і', datetime.datetime(1945, 7, 26, 0, 0))]),

        # Bulgarian
        param('bg', 'На 16 юни 1944 г. започват въздушни '
                    'бомбардировки срещу Япония, използувайки новозавладените острови като бази.',
              [('На 16 юни 1944 г', datetime.datetime(1944, 6, 16, 0, 0))]),

        # Chinese
        param('zh', '不過大多數人仍多把第二次世界大戰的爆發定為1939年9月1日德國入侵波蘭開始，這次入侵行動隨即導致英國與法國向德國宣戰。',
              [('1939年9月1', datetime.datetime(1939, 9, 1, 0, 0))]),

        # Czech
        param('cs', 'V roce 1920 byla proto vytvořena Společnost národů, jež měla fungovat jako fórum, '
                             'na němž měly národy mírovým způsobem urovnávat svoje spory.',
              [('1920', datetime.datetime(1920, 1, 1, 0, 0))]),

        # Danish
        param('da', 'Krigen i Europa begyndte den 1. september 1939, da Nazi-Tyskland invaderede Polen, '
                             'og endte med Nazi-Tysklands betingelsesløse overgivelse den 8. maj 1945.',
              [('1. september 1939,', datetime.datetime(1939, 9, 1, 0, 0)),
               ('8. maj 1945.', datetime.datetime(1945, 5, 8, 0, 0))]),

        # Dutch
        param('nl', ' De meest dramatische uitbreiding van het conflict vond plaats op 22 juni 1941 met de '
                    'Duitse aanval op de Sovjet-Unie.',
              [('22 juni 1941', datetime.datetime(1941, 6, 22, 0, 0))]),

        # English
        param('en', 'I will meet you tomorrow at noon',
              [('tomorrow at noon', datetime.datetime(2000, 1, 2, 12, 0))]),

        param('en', 'in a minute',
              [('in a minute', datetime.datetime(2000, 1, 1, 0, 1))]),
        param('en', 'July 13th.\r\n July 14th',
              [('July 13th', datetime.datetime(2000, 7, 13, 0, 0)),
               ('July 14th', datetime.datetime(2000, 7, 14, 0, 0))]),

        # Filipino / Tagalog
        param('tl', 'Maraming namatay sa mga Hapon hanggang sila\'y sumuko noong Agosto 15, 1945.',
              [('noong Agosto 15, 1945', datetime.datetime(1945, 8, 15, 0, 0))]),

        # Finnish
        param('fi', 'Iso-Britannia ja Ranska julistivat sodan Saksalle 3. syyskuuta 1939.',
              [('3. syyskuuta 1939.', datetime.datetime(1939, 9, 3, 0, 0))]),

        # French
        param('fr', 'La Seconde Guerre mondiale, ou Deuxième Guerre mondiale4, est un conflit armé à '
                    'l\'échelle planétaire qui dura du 1 septembre 1939 au 2 septembre 1945.',
              [('un', datetime.datetime(2000, 1, 1, 0, 0)),
               ('1 septembre 1939', datetime.datetime(1939, 9, 1, 0, 0)),
               ('2 septembre 1945', datetime.datetime(1945, 9, 2, 0, 0))]),

        # Hebrew
        param('he', 'במרץ 1938 "אוחדה" אוסטריה עם גרמניה (אנשלוס). ',
              [('במרץ 1938', datetime.datetime(1938, 3, 1, 0, 0))]),

        # Hindi
        param('hi',
              'जुलाई 1937 में, मार्को-पोलो ब्रिज हादसे का बहाना लेकर जापान ने चीन पर हमला कर दिया और चीनी साम्राज्य की राजधानी बीजिंग '
              'पर कब्जा कर लिया,',
              [('जुलाई 1937 में,', datetime.datetime(1937, 7, 1, 0, 0))]),

        # Hungarian
        param('hu', 'A háború Európában 1945. május 8-án Németország feltétel nélküli megadásával, '
                             'míg Ázsiában szeptember 2-án, Japán kapitulációjával fejeződött be.',
              [('1945. május 8-án', datetime.datetime(1945, 5, 8, 0, 0)),
               ('szeptember 2-án,', datetime.datetime(2000, 9, 2, 0, 0))]),

        # Georgian
        param('ka', '1937 წელს დაიწყო იაპონია-ჩინეთის მეორე ომი.',
              [('1937', datetime.datetime(1937, 1, 1, 0, 0))]),

        # German
        param('de', 'Die UdSSR blieb gemäß dem Neutralitätspakt '
                    'vom 13. April 1941 gegenüber Japan vorerst neutral.',
              [('Die', datetime.datetime(1999, 12, 28, 0, 0)),
               ('13. April 1941', datetime.datetime(1941, 4, 13, 0, 0))]),

        # Indonesian
        param('id', 'Kekaisaran Jepang menyerah pada tanggal 15 Agustus 1945, sehingga mengakhiri perang '
                             'di Asia dan memperkuat kemenangan total Sekutu atas Poros.',
              [('tanggal 15 Agustus 1945,', datetime.datetime(1945, 8, 15, 0, 0))]),

        # Italian
        param('it', ' Con questo il 2 ottobre 1935 prese il via la campagna '
                    'd\'Etiopia. Il 9 maggio 1936 venne proclamato l\'Impero. ',
              [('2 ottobre 1935', datetime.datetime(1935, 10, 2, 0, 0)),
               ('9 maggio 1936', datetime.datetime(1936, 5, 9, 0, 0))]),

        # Japanese
        param('ja', '1939年9月1日、ドイツ軍がポーランドへ侵攻したことが第二次世界大戦の始まりとされている。',
              [('1939年9月1', datetime.datetime(1939, 9, 1, 0, 0))]),

        # Persian
        param('fa', 'نگ جهانی دوم جنگ جدی بین سپتامبر 1939 و 2 سپتامبر 1945 بود.',
              [('سپتامبر 1939', datetime.datetime(1939, 9, 1, 0, 0)),
               ('2 سپتامبر 1945', datetime.datetime(1945, 9, 2, 0, 0))]),

        # Polish
        param('pl', 'II wojna światowa – największa wojna światowa w historii, '
                    'trwająca od 1 września 1939 do 2 września 1945 (w Europie do 8 maja 1945)',
              [('1 września 1939', datetime.datetime(1939, 9, 1, 0, 0)),
               ('2 września 1945 (w', datetime.datetime(1945, 9, 2, 0, 0)),
               ('8 maja 1945)', datetime.datetime(1945, 5, 8, 0, 0))]),

        # Portuguese
        param('pt', 'Em outubro de 1936, Alemanha e Itália formaram o Eixo Roma-Berlim.',
              [('Em outubro de 1936,', datetime.datetime(1936, 10, 1, 0, 0))]),

        # Romanian
        param('ro', 'Pe 17 septembrie 1939, după semnarea unui acord de încetare a focului cu Japonia, '
                             'sovieticii au invadat Polonia dinspre est.',
              [('17 septembrie 1939,', datetime.datetime(1939, 9, 17, 0, 0)),
               ('a', datetime.datetime(2000, 1, 1, 0, 0))]),

        # Russian
        param('ru', 'Втора́я мирова́я война́ (1 сентября 1939 — 2 сентября 1945) — '
                    'война двух мировых военно-политических коалиций, ставшая крупнейшим вооружённым '
                    'конфликтом в истории человечества.',
              [('(1 сентября 1939', datetime.datetime(1939, 9, 1, 0, 0)),
               ('2 сентября 1945)', datetime.datetime(1945, 9, 2, 0, 0))]),

        # Spanish
        param('es', 'Desde finales de 1939 hasta inicios de 1941, merced a una serie de fulgurantes campañas militares '
                    'y la firma de tratados, Alemania conquistó o sometió gran parte de la Europa continental.',
              [('de 1939', datetime.datetime(1939, 1, 1, 0, 0)),
               ('de 1941,', datetime.datetime(1941, 1, 1, 0, 0)),
               ('a una', datetime.datetime(2000, 1, 1, 0, 0))]),

        # Swedish
        param('sv', 'Efter kommunisternas seger 1922 drog de allierade och Japan bort sina trupper.',
              [('1922', datetime.datetime(1922, 1, 1, 0, 0))]),

        # Thai
        param('th', 'และเมื่อวันที่ 11 พฤษภาคม 1939 ญี่ปุ่นตัดสินใจขยายพรมแดนญี่ปุ่น-มองโกเลียขึ้นไปถึงแม่น้ำคัลคินกอลด้วยกำลัง',
              [('11 พฤษภาคม 1939', datetime.datetime(1939, 5, 11, 0, 0))]),

        # Turkish
        param('tr', 'Almanya’nın Polonya’yı işgal ettiği 1 Eylül 1939 savaşın başladığı '
                    'tarih olarak genel kabul görür.',
              [('1 Eylül 1939', datetime.datetime(1939, 9, 1, 0, 0))]),

        # Ukrainian
        param('uk', 'Інші дати, що розглядаються деякими авторами як дати початку війни: початок японської інтервенції '
                    'в Маньчжурію 13 вересня 1931, початок другої японсько-китайської війни 7 липня 1937 року та '
                    'початок угорсько-української війни 14 березня 1939 року.',
              [('13 вересня 1931,', datetime.datetime(1931, 9, 13, 0, 0)),
               ('7 липня 1937', datetime.datetime(1937, 7, 7, 0, 0)),
               ('14 березня 1939', datetime.datetime(1939, 3, 14, 0, 0))]),

        # Vietnamese
        param('vi', 'Ý theo gương Đức, đã tiến hành xâm lược Ethiopia năm 1935 và sát '
                    'nhập Albania vào ngày 12 tháng 4 năm 1939.',
              [('năm 1935', datetime.datetime(1935, 1, 1, 0, 0)),
               ('ngày 12 tháng 4 năm 1939', datetime.datetime(1939, 4, 12, 0, 0))]),
    ])
    def test_search_and_parse(self, shortname, string, expected):
        result = self.els.search_parse(shortname, string,
                                       settings={'RELATIVE_BASE': datetime.datetime(2000, 1, 1)})
        self.assertEqual(result, expected)
