# coding: utf-8
from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from nose_parameterized import parameterized, param

from dateparser.freshness_date_parser import FreshnessDateDataParser


class TestFreshnessDateDataParser(unittest.TestCase):

    en_params = [
        ('yesterday', dict(days=1), 'day'),
        ('the day before yesterday', dict(days=2), 'day'),
        ('today', dict(days=0), 'day'),
        ('an hour ago', dict(hours=1), 'day'),
        ('about an hour ago', dict(hours=1), 'day'),
        ('a day ago', dict(days=1), 'day'),
        ('a week ago', dict(weeks=1), 'weeks'),
        ('one week ago', dict(weeks=1), 'weeks'),
        ('2 hours ago', dict(hours=2), 'day'),
        ('about 23 hours ago', dict(hours=23), 'day'),
        ('1 year 2 months', dict(years=1, months=2), 'months'),
        ('1 year, 09 months,01 weeks', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 year 11 months', dict(years=1, months=11), 'months'),
        ('1 year 12 months', dict(years=1, months=12), 'months'),
        ('15 hr', dict(hours=15), 'day'),
        ('15 hrs', dict(hours=15), 'day'),
        ('2 min', dict(minutes=2), 'day'),
        ('2 mins', dict(minutes=2), 'day'),
        ('3 sec', dict(seconds=3), 'day'),
        (
            '1 year, 1 month, 1 week, 1 day, 1 hour and 1 minute ago',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
        ('1000 years ago', dict(years=1000), 'years'),
        ('5000 months ago', dict(years=416,months=8), 'months'),
    ]

    fr_params = [
        ("Aujourd'hui", dict(days=0), 'day'),
        ("Hier", dict(days=1), 'day'),
        ("Avant-hier", dict(days=2), 'day'),
        ('Il ya un jour', dict(days=1), 'day'),
        ('Il ya une heure', dict(hours=1), 'day'),
        ('Il ya 2 heures', dict(hours=2), 'day'),
        ('Il ya environ 23 heures', dict(hours=23), 'day'),
        ('1 an 2 mois', dict(years=1, months=2), 'months'),
        ('1 année, 09 mois, 01 semaines', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 an 11 mois', dict(years=1, months=11), 'months'),
        (
            'Il ya 1 an, 1 mois, 1 semaine, 1 jour, 1 heure et 1 minute',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    de_params = [
        ('Heute', dict(days=0), 'day'),
        ('Gestern', dict(days=1), 'day'),
        ('vorgestern', dict(days=2), 'day'),
        ('vor einem Tag', dict(days=1), 'day'),
        ('vor einer Stunden', dict(hours=1), 'day'),
        ('Vor 2 Stunden', dict(hours=2), 'day'),
        ('Vor 2 Stunden', dict(hours=2), 'day'),
        ('vor etwa 23 Stunden', dict(hours=23), 'day'),
        ('1 Jahr 2 Monate', dict(years=1, months=2), 'months'),
        ('1 Jahr, 09 Monate, 01 Wochen', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 Jahr 11 Monate', dict(years=1, months=11), 'months'),
        ('vor 29h', dict(hours=29), 'day'),
        ('vor 29m', dict(minutes=29), 'day'),
        (
            '1 Jahr, 1 Monat, 1 Woche, 1 Tag, 1 Stunde und 1 Minute',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    it_params = [
        ('oggi', dict(days=0), 'day'),
        ('ieri', dict(days=1), 'day'),
        ('2 ore fa', dict(hours=2), 'day'),
        ('circa 23 ore fa', dict(hours=23), 'day'),
        ('1 anno 2 mesi', dict(years=1, months=2), 'months'),
        ('1 anno, 09 mesi, 01 settimane', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 anno 11 mesi', dict(years=1, months=11), 'months'),
        (
            '1 anno, 1 mese, 1 settimana, 1 giorno, 1 ora e 1 minuto fa',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    pt_params = [
        ('ontem', dict(days=1), 'day'),
        ('anteontem', dict(days=2), 'day'),
        ('hoje', dict(days=0), 'day'),
        ('uma hora atrás', dict(hours=1), 'day'),
        ('um dia atrás', dict(days=1), 'day'),
        ('uma semana atrás', dict(weeks=1), 'weeks'),
        ('2 horas atrás', dict(hours=2), 'day'),
        ('cerca de 23 horas atrás', dict(hours=23), 'day'),
        ('1 ano 2 meses', dict(years=1, months=2), 'months'),
        ('1 ano, 09 meses, 01 semanas', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 ano 11 meses', dict(years=1, months=11), 'months'),
        (
            '1 ano, 1 mês, 1 semana, 1 dia, 1 hora e 1 minuto atrás',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    tr_params = [
        ('Dün', dict(days=1), 'day'),
        ('2 saat önce', dict(hours=2), 'day'),
        ('yaklaşık 23 saat önce', dict(hours=23), 'day'),
        ('1 yıl 2 ay', dict(years=1, months=2), 'months'),
        ('1 yıl, 09 ay, 01 hafta', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 yıl 11 ay', dict(years=1, months=11), 'months'),
        (
            '1 yıl, 1 ay, 1 hafta, 1 gün, 1 saat ve 1 dakika önce',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    ru_params = [
        ('сегодня', dict(days=0), 'day'),
        ('вчеравчера', dict(days=1), 'day'),
        ('Вчера в', dict(days=1), 'day'),
        ('вчера', dict(days=1), 'day'),
        ('2 часа назад', dict(hours=2), 'day'),
        ('час назад', dict(hours=1), 'day'),
        ('минуту назад', dict(minutes=1), 'day'),
        ('2 ч. 21 мин. назад', dict(hours=2, minutes=21), 'day'),
        ('около 23 часов назад', dict(hours=23), 'day'),
        ('1 год 2 месяца', dict(years=1, months=2), 'months'),
        ('1 год, 09 месяцев, 01 недель', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 год 11 месяцев', dict(years=1, months=11), 'months'),
        (
            '1 год, 1 месяц, 1 неделя, 1 день, 1 час и 1 минуту назад',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    cs_params = [
        ('Před 2 hodinami', dict(hours=2), 'day'),
        ('před přibližně 23 hodin', dict(hours=23), 'day'),
        ('1 rok 2 měsíce', dict(years=1, months=2), 'months'),
        ('1 rok, 09 měsíců, 01 týdnů', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 rok 11 měsíců', dict(years=1, months=11), 'months'),
        (
            '1 rok, 1 měsíc, 1 týden, 1 den, 1 hodina a 1 minuta před',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
        ('3 dny', dict(days=3), 'day'),
        ('3 hodiny', dict(hours=3), 'day'),
    ]

    es_params = [
        ('anteayer', dict(days=2), 'day'),
        ('ayer', dict(days=1), 'day'),
        ('hoy', dict(days=0), 'day'),
        ('hace una hora', dict(hours=1), 'day'),
        ('Hace un día', dict(days=1), 'day'),
        ('Hace una semana', dict(weeks=1), 'weeks'),
        ('Hace 2 horas', dict(hours=2), 'day'),
        ('Hace cerca de 23 horas', dict(hours=23), 'day'),
        ('1 año 2 meses', dict(years=1, months=2), 'months'),
        ('1 año, 09 meses, 01 semanas', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1 año 11 meses', dict(years=1, months=11), 'months'),
        (
            'Hace 1 año, 1 mes, 1 semana, 1 día, 1 hora y 1 minuto',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    cn_params = [
        ('昨天', dict(days=1), 'day'),
        ('前天', dict(days=2), 'day'),
        ('2小时前', dict(hours=2), 'day'),
        ('约23小时前', dict(hours=23), 'day'),
        ('1年2个月', dict(years=1, months=2), 'months'),
        ('1年09月，01周', dict(years=1, months=9, weeks=1), 'weeks'),
        ('1年11个月', dict(years=1, months=11), 'months'),
        (
            '1年，1月，1周，1天，1小时，1分钟前',
            dict(years=1, months=1, weeks=1, days=1, hours=1, minutes=1),
            'day',
        ),
    ]

    def setUp(self):
        self.now = datetime.utcnow()
        self.fp = FreshnessDateDataParser(now=self.now)

    def iter_params(self, params):

        for params in params:
            date_string, td_kwargs, _period = params

            date, period = self.fp.parse(date_string)

            td = relativedelta(**td_kwargs)

            def check_equal(first, second):
                msg = "%s != %s\n        for string: '%s'" % (
                    repr(first), repr(second), date_string)
                self.assertEqual(first, second, msg)

            check_equal(self.now - td, date)
            check_equal(period, _period)

    def test_en_dates(self):
        self.iter_params(self.en_params)

    def test_fr_dates(self):
        self.iter_params(self.fr_params)

    def test_de_dates(self):
        self.iter_params(self.de_params)

    def test_it_dates(self):
        self.iter_params(self.it_params)

    def test_pt_dates(self):
        self.iter_params(self.pt_params)

    def test_tr_dates(self):
        self.iter_params(self.tr_params)

    def test_ru_dates(self):
        self.iter_params(self.ru_params)

    def test_cs_dates(self):
        self.iter_params(self.cs_params)

    def test_es_dates(self):
        self.iter_params(self.es_params)

    def test_cn_dates(self):
        self.iter_params(self.cn_params)

    def test_insane_dates(self):
        cur_year = self.now.year
        self.assertRaises(ValueError, self.fp.parse, '5000 years ago')
        self.assertRaises(ValueError, self.fp.parse, str(cur_year) + ' years ago')
        
        date, period = self.fp.parse('15th of Aug, 2014 Diane Bennett')
        self.assertEqual(date, None, '"15th of Aug, 2014 Diane Bennett" should not be parsed')

    @parameterized.expand([
        param('несколько секунд назад', timedelta(seconds=45)),
        param('há alguns segundos', timedelta(seconds=45)),
    ])
    def test_inexplicit_dates(self, date_string, boundary):
        date, period = self.fp.parse(date_string)
        self.assertEqual('day', period)
        self.assertLess(date, self.now)
        self.assertLess(self.now - date, boundary)


if __name__ == '__main__':
    unittest.main()
