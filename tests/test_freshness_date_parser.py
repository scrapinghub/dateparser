# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from datetime import datetime, timedelta, date, time
from functools import wraps
import pytz
import regex as re

from dateutil.relativedelta import relativedelta
from mock import Mock, patch
from nose_parameterized import parameterized, param

import dateparser
from dateparser.date import DateDataParser, freshness_date_parser
from tests import BaseTestCase
from dateparser.utils import normalize_unicode
from dateparser.conf import settings


class TestFreshnessDateDataParser(BaseTestCase):
    def setUp(self):
        super(TestFreshnessDateDataParser, self).setUp()
        self.now = datetime(2014, 9, 1, 10, 30)
        self.date_string = NotImplemented
        self.parser = NotImplemented
        self.result = NotImplemented
        self.freshness_parser = NotImplemented
        self.freshness_result = NotImplemented
        self.date = NotImplemented
        self.time = NotImplemented

        settings.TIMEZONE = 'utc'

    @parameterized.expand([
        # English dates
        param('yesterday', ago={'days': 1}, period='day'),
        param('the day before yesterday', ago={'days': 2}, period='day'),
        param('today', ago={'days': 0}, period='day'),
        param('an hour ago', ago={'hours': 1}, period='day'),
        param('about an hour ago', ago={'hours': 1}, period='day'),
        param('a day ago', ago={'days': 1}, period='day'),
        param('a week ago', ago={'weeks': 1}, period='week'),
        param('2 hours ago', ago={'hours': 2}, period='day'),
        param('about 23 hours ago', ago={'hours': 23}, period='day'),
        param('1 year 2 months', ago={'years': 1, 'months': 2}, period='month'),
        param('1 year, 09 months,01 weeks', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 year 11 months', ago={'years': 1, 'months': 11}, period='month'),
        param('1 year 12 months', ago={'years': 1, 'months': 12}, period='month'),
        param('15 hr', ago={'hours': 15}, period='day'),
        param('15 hrs', ago={'hours': 15}, period='day'),
        param('2 min', ago={'minutes': 2}, period='day'),
        param('2 mins', ago={'minutes': 2}, period='day'),
        param('3 sec', ago={'seconds': 3}, period='day'),
        param('1000 years ago', ago={'years': 1000}, period='year'),
        param('2013 years ago', ago={'years': 2013}, period='year'),  # We've fixed .now in setUp
        param('5000 months ago', ago={'years': 416, 'months': 8}, period='month'),
        param('{} months ago'.format(2013 * 12 + 8), ago={'years': 2013, 'months': 8}, period='month'),
        param('1 year, 1 month, 1 week, 1 day, 1 hour and 1 minute ago',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('just now', ago={'seconds': 0}, period='day'),

        # French dates
        param("Aujourd'hui", ago={'days': 0}, period='day'),
        param("Aujourd’hui", ago={'days': 0}, period='day'),
        param("Aujourdʼhui", ago={'days': 0}, period='day'),
        param("Aujourdʻhui", ago={'days': 0}, period='day'),
        param("Aujourd՚hui", ago={'days': 0}, period='day'),
        param("Aujourdꞌhui", ago={'days': 0}, period='day'),
        param("Aujourd＇hui", ago={'days': 0}, period='day'),
        param("Aujourd′hui", ago={'days': 0}, period='day'),
        param("Aujourd‵hui", ago={'days': 0}, period='day'),
        param("Aujourdʹhui", ago={'days': 0}, period='day'),
        param("Aujourd＇hui", ago={'days': 0}, period='day'),
        param("moins de 21s", ago={'seconds': 21}, period='day'),
        param("moins de 21m", ago={'minutes': 21}, period='day'),
        param("moins de 21h", ago={'hours': 21}, period='day'),
        param("moins de 21 minute", ago={'minutes': 21}, period='day'),
        param("moins de 21 heure", ago={'hours': 21}, period='day'),
        param("Hier", ago={'days': 1}, period='day'),
        param("Avant-hier", ago={'days': 2}, period='day'),
        param('Il ya un jour', ago={'days': 1}, period='day'),
        param('Il ya une heure', ago={'hours': 1}, period='day'),
        param('Il ya 2 heures', ago={'hours': 2}, period='day'),
        param('Il ya environ 23 heures', ago={'hours': 23}, period='day'),
        param('1 an 2 mois', ago={'years': 1, 'months': 2}, period='month'),
        param('1 année, 09 mois, 01 semaines', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 an 11 mois', ago={'years': 1, 'months': 11}, period='month'),
        param('Il ya 1 an, 1 mois, 1 semaine, 1 jour, 1 heure et 1 minute',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('Il y a 40 min', ago={'minutes': 40}, period='day'),

        # German dates
        param('Heute', ago={'days': 0}, period='day'),
        param('Gestern', ago={'days': 1}, period='day'),
        param('vorgestern', ago={'days': 2}, period='day'),
        param('vor einem Tag', ago={'days': 1}, period='day'),
        param('vor einer Stunden', ago={'hours': 1}, period='day'),
        param('Vor 2 Stunden', ago={'hours': 2}, period='day'),
        param('vor etwa 23 Stunden', ago={'hours': 23}, period='day'),
        param('1 Jahr 2 Monate', ago={'years': 1, 'months': 2}, period='month'),
        param('1 Jahr, 09 Monate, 01 Wochen', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 Jahr 11 Monate', ago={'years': 1, 'months': 11}, period='month'),
        param('vor 29h', ago={'hours': 29}, period='day'),
        param('vor 29m', ago={'minutes': 29}, period='day'),
        param('1 Jahr, 1 Monat, 1 Woche, 1 Tag, 1 Stunde und 1 Minute',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Italian dates
        param('oggi', ago={'days': 0}, period='day'),
        param('ieri', ago={'days': 1}, period='day'),
        param('2 ore fa', ago={'hours': 2}, period='day'),
        param('circa 23 ore fa', ago={'hours': 23}, period='day'),
        param('1 anno 2 mesi', ago={'years': 1, 'months': 2}, period='month'),
        param('1 anno, 09 mesi, 01 settimane', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 anno 11 mesi', ago={'years': 1, 'months': 11}, period='month'),
        param('1 anno, 1 mese, 1 settimana, 1 giorno, 1 ora e 1 minuto fa',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Portuguese dates
        param('ontem', ago={'days': 1}, period='day'),
        param('anteontem', ago={'days': 2}, period='day'),
        param('hoje', ago={'days': 0}, period='day'),
        param('uma hora atrás', ago={'hours': 1}, period='day'),
        param('1 segundo atrás', ago={'seconds': 1}, period='day'),
        param('um dia atrás', ago={'days': 1}, period='day'),
        param('uma semana atrás', ago={'weeks': 1}, period='week'),
        param('2 horas atrás', ago={'hours': 2}, period='day'),
        param('cerca de 23 horas atrás', ago={'hours': 23}, period='day'),
        param('1 ano 2 meses', ago={'years': 1, 'months': 2}, period='month'),
        param('1 ano, 09 meses, 01 semanas', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 ano 11 meses', ago={'years': 1, 'months': 11}, period='month'),
        param('1 ano, 1 mês, 1 semana, 1 dia, 1 hora e 1 minuto atrás',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Turkish dates
        param('Dün', ago={'days': 1}, period='day'),
        param('Bugün', ago={'days': 0}, period='day'),
        param('2 saat önce', ago={'hours': 2}, period='day'),
        param('yaklaşık 23 saat önce', ago={'hours': 23}, period='day'),
        param('1 yıl 2 ay', ago={'years': 1, 'months': 2}, period='month'),
        param('1 yıl, 09 ay, 01 hafta', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 yıl 11 ay', ago={'years': 1, 'months': 11}, period='month'),
        param('1 yıl, 1 ay, 1 hafta, 1 gün, 1 saat ve 1 dakika önce',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Russian dates
        param('сегодня', ago={'days': 0}, period='day'),
        param('Вчера в', ago={'days': 1}, period='day'),
        param('вчера', ago={'days': 1}, period='day'),
        param('2 часа назад', ago={'hours': 2}, period='day'),
        param('час назад', ago={'hours': 1}, period='day'),
        param('минуту назад', ago={'minutes': 1}, period='day'),
        param('2 ч. 21 мин. назад', ago={'hours': 2, 'minutes': 21}, period='day'),
        param('около 23 часов назад', ago={'hours': 23}, period='day'),
        param('1 год 2 месяца', ago={'years': 1, 'months': 2}, period='month'),
        param('1 год, 09 месяцев, 01 недель', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 год 11 месяцев', ago={'years': 1, 'months': 11}, period='month'),
        param('1 год, 1 месяц, 1 неделя, 1 день, 1 час и 1 минуту назад',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Czech dates
        param('Dnes', ago={'days': 0}, period='day'),
        param('Včera', ago={'days': 1}, period='day'),
        param('Předevčírem', ago={'days': 2}, period='day'),
        param('Před 2 hodinami', ago={'hours': 2}, period='day'),
        param('před přibližně 23 hodin', ago={'hours': 23}, period='day'),
        param('1 rok 2 měsíce', ago={'years': 1, 'months': 2}, period='month'),
        param('1 rok, 09 měsíců, 01 týdnů', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 rok 11 měsíců', ago={'years': 1, 'months': 11}, period='month'),
        param('3 dny', ago={'days': 3}, period='day'),
        param('3 hodiny', ago={'hours': 3}, period='day'),
        param('1 rok, 1 měsíc, 1 týden, 1 den, 1 hodina, 1 minuta před',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Spanish dates
        param('anteayer', ago={'days': 2}, period='day'),
        param('ayer', ago={'days': 1}, period='day'),
        param('hoy', ago={'days': 0}, period='day'),
        param('hace una hora', ago={'hours': 1}, period='day'),
        param('Hace un día', ago={'days': 1}, period='day'),
        param('Hace una semana', ago={'weeks': 1}, period='week'),
        param('Hace 2 horas', ago={'hours': 2}, period='day'),
        param('Hace cerca de 23 horas', ago={'hours': 23}, period='day'),
        param('1 año 2 meses', ago={'years': 1, 'months': 2}, period='month'),
        param('1 año, 09 meses, 01 semanas', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 año 11 meses', ago={'years': 1, 'months': 11}, period='month'),
        param('Hace 1 año, 1 mes, 1 semana, 1 día, 1 hora y 1 minuto',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Chinese dates
        param('昨天', ago={'days': 1}, period='day'),
        param('前天', ago={'days': 2}, period='day'),
        param('2小时前', ago={'hours': 2}, period='day'),
        param('约23小时前', ago={'hours': 23}, period='day'),
        param('1年2个月', ago={'years': 1, 'months': 2}, period='month'),
        param('1年2個月', ago={'years': 1, 'months': 2}, period='month'),
        param('1年09月，01周', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1年11个月', ago={'years': 1, 'months': 11}, period='month'),
        param('1年11個月', ago={'years': 1, 'months': 11}, period='month'),
        param('1年，1月，1周，1天，1小时，1分钟前',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Arabic dates
        param('اليوم', ago={'days': 0}, period='day'),
        param('يوم أمس', ago={'days': 1}, period='day'),
        param('منذ يومين', ago={'days': 2}, period='day'),
        param('منذ 3 أيام', ago={'days': 3}, period='day'),
        param('منذ 21 أيام', ago={'days': 21}, period='day'),
        param('1 عام, 1 شهر, 1 أسبوع, 1 يوم, 1 ساعة, 1 دقيقة',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Thai dates
        param('วันนี้', ago={'days': 0}, period='day'),
        param('เมื่อวานนี้', ago={'days': 1}, period='day'),
        param('2 วัน', ago={'days': 2}, period='day'),
        param('2 ชั่วโมง', ago={'hours': 2}, period='day'),
        param('23 ชม.', ago={'hours': 23}, period='day'),
        param('2 สัปดาห์ 3 วัน', ago={'weeks': 2, 'days': 3}, period='day'),
        param('1 ปี 9 เดือน 1 สัปดาห์', ago={'years': 1, 'months': 9, 'weeks': 1},
              period='week'),
        param('1 ปี 1 เดือน 1 สัปดาห์ 1 วัน 1 ชั่วโมง 1 นาที',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Vietnamese dates
        param('Hôm nay', ago={'days': 0}, period='day'),
        param('Hôm qua', ago={'days': 1}, period='day'),
        param('2 giờ', ago={'hours': 2}, period='day'),
        param('2 tuần 3 ngày', ago={'weeks': 2, 'days': 3}, period='day'),
        # following test unsupported, refer to discussion at:
        # http://github.com/scrapinghub/dateparser/issues/33
        #param('1 năm 1 tháng 1 tuần 1 ngày 1 giờ 1 chút',
        #      ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
        #      period='day'),

        # Belarusian dates
        param('сёння', ago={'days': 0}, period='day'),
        param('учора ў', ago={'days': 1}, period='day'),
        param('ўчора', ago={'days': 1}, period='day'),
        param('пазаўчора', ago={'days': 2}, period='day'),
        param('2 гадзіны таму назад', ago={'hours': 2}, period='day'),
        param('2 гадзіны таму', ago={'hours': 2}, period='day'),
        param('гадзіну назад', ago={'hours': 1}, period='day'),
        param('хвіліну таму', ago={'minutes': 1}, period='day'),
        param('2 гадзіны 21 хвіл. назад', ago={'hours': 2, 'minutes': 21}, period='day'),
        param('каля 23 гадзін назад', ago={'hours': 23}, period='day'),
        param('1 год 2 месяцы', ago={'years': 1, 'months': 2}, period='month'),
        param('1 год, 09 месяцаў, 01 тыдзень', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('2 гады 3 месяцы', ago={'years': 2, 'months': 3}, period='month'),
        param('5 гадоў, 1 месяц, 6 тыдняў, 3 дні, 5 гадзін 1 хвіліну і 3 секунды таму назад',
              ago={'years': 5, 'months': 1, 'weeks': 6, 'days': 3, 'hours': 5, 'minutes': 1, 'seconds': 3},
              period='day'),

        # Polish dates
        param("wczoraj", ago={'days': 1}, period='day'),
        param("1 godz. 2 minuty temu", ago={'hours': 1, 'minutes': 2}, period='day'),
        param("2 lata, 3 miesiące, 1 tydzień, 2 dni, 4 godziny, 15 minut i 25 sekund temu",
              ago={'years': 2, 'months': 3, 'weeks': 1, 'days': 2, 'hours': 4, 'minutes': 15, 'seconds': 25},
              period='day'),
        param("2 minuty temu", ago={'minutes': 2}, period='day'),
        param("15 minut temu", ago={'minutes': 15}, period='day'),

        # Bulgarian dates
        param('преди 3 дни', ago={'days': 3}, period='day'),
        param('преди час', ago={'hours': 1}, period='day'),
        param('преди година', ago={'years': 1}, period='year'),
        param('вчера', ago={'days': 1}, period='day'),
        param('онзи ден', ago={'days': 2}, period='day'),
        param('днес', ago={'days': 0}, period='day'),
        param('преди час', ago={'hours': 1}, period='day'),
        param('преди един ден', ago={'days': 1}, period='day'),
        param('преди седмица', ago={'weeks': 1}, period='week'),
        param('преди 2 часа', ago={'hours': 2}, period='day'),
        param('преди около 23 часа', ago={'hours': 23}, period='day'),
        # Bangla dates
        # param('গতকাল', ago={'days': 1}, period='day'),
        # param('আজ', ago={'days': 0}, period='day'),
        param('1 ঘন্টা আগে', ago={'hours': 1}, period='day'),
        param('প্রায় 1 ঘন্টা আগে', ago={'hours': 1}, period='day'),
        param('1 দিন আগে', ago={'days': 1}, period='day'),
        param('1 সপ্তাহ আগে', ago={'weeks': 1}, period='week'),
        param('2 ঘন্টা আগে', ago={'hours': 2}, period='day'),
        param('প্রায় 23 ঘন্টা আগে', ago={'hours': 23}, period='day'),
        param('1 বছর 2 মাস', ago={'years': 1, 'months': 2}, period='month'),
        param('1 বছর, 09 মাস,01 সপ্তাহ', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 বছর 11 মাস', ago={'years': 1, 'months': 11}, period='month'),
        param('1 বছর 12 মাস', ago={'years': 1, 'months': 12}, period='month'),
        param('15 ঘন্টা', ago={'hours': 15}, period='day'),
        param('2 মিনিট', ago={'minutes': 2}, period='day'),
        param('3 সেকেন্ড', ago={'seconds': 3}, period='day'),
        param('1000 বছর আগে', ago={'years': 1000}, period='year'),
        param('5000 মাস আগে', ago={'years': 416, 'months': 8}, period='month'),
        param('{} মাস আগে'.format(2013 * 12 + 8), ago={'years': 2013, 'months': 8}, period='month'),
        param('1 বছর, 1 মাস, 1 সপ্তাহ, 1 দিন, 1 ঘন্টা এবং 1 মিনিট আগে',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        # param('এখন', ago={'seconds': 0}, period='day'),

        # Hindi dates
        param('1 घंटे पहले', ago={'hours': 1},period='day'),
        param('15 मिनट पहले',ago={'minutes':15},period='day'),
        param('25 सेकंड पूर्व',ago={'seconds':25},period='day'),
        param('1 वर्ष, 8 महीने, 2 सप्ताह', ago={'years': 1, 'months': 8, 'weeks': 2}, period='week'),
        param('1 वर्ष 7 महीने', ago={'years': 1, 'months': 7}, period='month'),
        param('आज', ago={'days': 0}, period='day'),
    ])

    def test_relative_past_dates(self, date_string, ago, period):
        self.given_parser(settings={'NORMALIZE': False})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_parsed_by_freshness_parser()
        self.then_date_obj_is_exactly_this_time_ago(ago)
        self.then_period_is(period)

    @parameterized.expand([
        # English dates
        param('yesterday', ago={'days': 1}, period='day'),
        param('the day before yesterday', ago={'days': 2}, period='day'),
        param('today', ago={'days': 0}, period='day'),
        param('an hour ago', ago={'hours': 1}, period='day'),
        param('about an hour ago', ago={'hours': 1}, period='day'),
        param('a day ago', ago={'days': 1}, period='day'),
        param('a week ago', ago={'weeks': 1}, period='week'),
        param('2 hours ago', ago={'hours': 2}, period='day'),
        param('about 23 hours ago', ago={'hours': 23}, period='day'),
        param('1 year 2 months', ago={'years': 1, 'months': 2}, period='month'),
        param('1 year, 09 months,01 weeks', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 year 11 months', ago={'years': 1, 'months': 11}, period='month'),
        param('1 year 12 months', ago={'years': 1, 'months': 12}, period='month'),
        param('15 hr', ago={'hours': 15}, period='day'),
        param('15 hrs', ago={'hours': 15}, period='day'),
        param('2 min', ago={'minutes': 2}, period='day'),
        param('2 mins', ago={'minutes': 2}, period='day'),
        param('3 sec', ago={'seconds': 3}, period='day'),
        param('1000 years ago', ago={'years': 1000}, period='year'),
        param('2013 years ago', ago={'years': 2013}, period='year'),  # We've fixed .now in setUp
        param('5000 months ago', ago={'years': 416, 'months': 8}, period='month'),
        param('{} months ago'.format(2013 * 12 + 8), ago={'years': 2013, 'months': 8}, period='month'),
        param('1 year, 1 month, 1 week, 1 day, 1 hour and 1 minute ago',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('just now', ago={'seconds': 0}, period='day'),

        # French dates
        param("Aujourd'hui", ago={'days': 0}, period='day'),
        param("Aujourd’hui", ago={'days': 0}, period='day'),
        param("Aujourdʼhui", ago={'days': 0}, period='day'),
        param("Aujourdʻhui", ago={'days': 0}, period='day'),
        param("Aujourd՚hui", ago={'days': 0}, period='day'),
        param("Aujourdꞌhui", ago={'days': 0}, period='day'),
        param("Aujourd＇hui", ago={'days': 0}, period='day'),
        param("Aujourd′hui", ago={'days': 0}, period='day'),
        param("Aujourd‵hui", ago={'days': 0}, period='day'),
        param("Aujourdʹhui", ago={'days': 0}, period='day'),
        param("Aujourd＇hui", ago={'days': 0}, period='day'),
        param("Hier", ago={'days': 1}, period='day'),
        param("Avant-hier", ago={'days': 2}, period='day'),
        param('Il ya un jour', ago={'days': 1}, period='day'),
        param('Il ya une heure', ago={'hours': 1}, period='day'),
        param('Il ya 2 heures', ago={'hours': 2}, period='day'),
        param('Il ya environ 23 heures', ago={'hours': 23}, period='day'),
        param('1 an 2 mois', ago={'years': 1, 'months': 2}, period='month'),
        param('1 année, 09 mois, 01 semaines', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 an 11 mois', ago={'years': 1, 'months': 11}, period='month'),
        param('Il ya 1 an, 1 mois, 1 semaine, 1 jour, 1 heure et 1 minute',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('Il y a 40 min', ago={'minutes': 40}, period='day'),

        # German dates
        param('Heute', ago={'days': 0}, period='day'),
        param('Gestern', ago={'days': 1}, period='day'),
        param('vorgestern', ago={'days': 2}, period='day'),
        param('vor einem Tag', ago={'days': 1}, period='day'),
        param('vor einer Stunden', ago={'hours': 1}, period='day'),
        param('Vor 2 Stunden', ago={'hours': 2}, period='day'),
        param('Vor 2 Stunden', ago={'hours': 2}, period='day'),
        param('vor etwa 23 Stunden', ago={'hours': 23}, period='day'),
        param('1 Jahr 2 Monate', ago={'years': 1, 'months': 2}, period='month'),
        param('1 Jahr, 09 Monate, 01 Wochen', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 Jahr 11 Monate', ago={'years': 1, 'months': 11}, period='month'),
        param('vor 29h', ago={'hours': 29}, period='day'),
        param('vor 29m', ago={'minutes': 29}, period='day'),
        param('1 Jahr, 1 Monat, 1 Woche, 1 Tag, 1 Stunde und 1 Minute',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Italian dates
        param('oggi', ago={'days': 0}, period='day'),
        param('ieri', ago={'days': 1}, period='day'),
        param('2 ore fa', ago={'hours': 2}, period='day'),
        param('circa 23 ore fa', ago={'hours': 23}, period='day'),
        param('1 anno 2 mesi', ago={'years': 1, 'months': 2}, period='month'),
        param('1 anno, 09 mesi, 01 settimane', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 anno 11 mesi', ago={'years': 1, 'months': 11}, period='month'),
        param('1 anno, 1 mese, 1 settimana, 1 giorno, 1 ora e 1 minuto fa',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Portuguese dates
        param('ontem', ago={'days': 1}, period='day'),
        param('anteontem', ago={'days': 2}, period='day'),
        param('hoje', ago={'days': 0}, period='day'),
        param('uma hora atrás', ago={'hours': 1}, period='day'),
        param('1 segundo atrás', ago={'seconds': 1}, period='day'),
        param('um dia atrás', ago={'days': 1}, period='day'),
        param('uma semana atrás', ago={'weeks': 1}, period='week'),
        param('2 horas atrás', ago={'hours': 2}, period='day'),
        param('cerca de 23 horas atrás', ago={'hours': 23}, period='day'),
        param('1 ano 2 meses', ago={'years': 1, 'months': 2}, period='month'),
        param('1 ano, 09 meses, 01 semanas', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 ano 11 meses', ago={'years': 1, 'months': 11}, period='month'),
        param('1 ano, 1 mês, 1 semana, 1 dia, 1 hora e 1 minuto atrás',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Turkish dates
        param('Dün', ago={'days': 1}, period='day'),
        param('Bugün', ago={'days': 0}, period='day'),
        param('2 saat önce', ago={'hours': 2}, period='day'),
        param('yaklaşık 23 saat önce', ago={'hours': 23}, period='day'),
        param('1 yıl 2 ay', ago={'years': 1, 'months': 2}, period='month'),
        param('1 yıl, 09 ay, 01 hafta', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 yıl 11 ay', ago={'years': 1, 'months': 11}, period='month'),
        param('1 yıl, 1 ay, 1 hafta, 1 gün, 1 saat ve 1 dakika önce',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Russian dates
        param('сегодня', ago={'days': 0}, period='day'),
        param('Вчера в', ago={'days': 1}, period='day'),
        param('вчера', ago={'days': 1}, period='day'),
        param('2 часа назад', ago={'hours': 2}, period='day'),
        param('час назад', ago={'hours': 1}, period='day'),
        param('минуту назад', ago={'minutes': 1}, period='day'),
        param('2 ч. 21 мин. назад', ago={'hours': 2, 'minutes': 21}, period='day'),
        param('около 23 часов назад', ago={'hours': 23}, period='day'),
        param('1 год 2 месяца', ago={'years': 1, 'months': 2}, period='month'),
        param('1 год, 09 месяцев, 01 недель', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 год 11 месяцев', ago={'years': 1, 'months': 11}, period='month'),
        param('1 год, 1 месяц, 1 неделя, 1 день, 1 час и 1 минуту назад',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Czech dates
        param('Dnes', ago={'days': 0}, period='day'),
        param('Včera', ago={'days': 1}, period='day'),
        param('Předevčírem', ago={'days': 2}, period='day'),
        param('Před 2 hodinami', ago={'hours': 2}, period='day'),
        param('před přibližně 23 hodin', ago={'hours': 23}, period='day'),
        param('1 rok 2 měsíce', ago={'years': 1, 'months': 2}, period='month'),
        param('1 rok, 09 měsíců, 01 týdnů', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 rok 11 měsíců', ago={'years': 1, 'months': 11}, period='month'),
        param('3 dny', ago={'days': 3}, period='day'),
        param('3 hodiny', ago={'hours': 3}, period='day'),
        param('1 rok, 1 měsíc, 1 týden, 1 den, 1 hodina, 1 minuta před',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Spanish dates
        param('anteayer', ago={'days': 2}, period='day'),
        param('ayer', ago={'days': 1}, period='day'),
        param('hoy', ago={'days': 0}, period='day'),
        param('hace una hora', ago={'hours': 1}, period='day'),
        param('Hace un día', ago={'days': 1}, period='day'),
        param('Hace una semana', ago={'weeks': 1}, period='week'),
        param('Hace 2 horas', ago={'hours': 2}, period='day'),
        param('Hace cerca de 23 horas', ago={'hours': 23}, period='day'),
        param('1 año 2 meses', ago={'years': 1, 'months': 2}, period='month'),
        param('1 año, 09 meses, 01 semanas', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 año 11 meses', ago={'years': 1, 'months': 11}, period='month'),
        param('Hace 1 año, 1 mes, 1 semana, 1 día, 1 hora y 1 minuto',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Chinese dates
        param('昨天', ago={'days': 1}, period='day'),
        param('前天', ago={'days': 2}, period='day'),
        param('2小时前', ago={'hours': 2}, period='day'),
        param('约23小时前', ago={'hours': 23}, period='day'),
        param('1年2个月', ago={'years': 1, 'months': 2}, period='month'),
        param('1年2個月', ago={'years': 1, 'months': 2}, period='month'),
        param('1年09月，01周', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1年11个月', ago={'years': 1, 'months': 11}, period='month'),
        param('1年11個月', ago={'years': 1, 'months': 11}, period='month'),
        param('1年，1月，1周，1天，1小时，1分钟前',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Arabic dates
        param('اليوم', ago={'days': 0}, period='day'),
        param('يوم أمس', ago={'days': 1}, period='day'),
        param('منذ يومين', ago={'days': 2}, period='day'),
        param('منذ 3 أيام', ago={'days': 3}, period='day'),
        param('منذ 21 أيام', ago={'days': 21}, period='day'),
        param('1 عام, 1 شهر, 1 أسبوع, 1 يوم, 1 ساعة, 1 دقيقة',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Thai dates
        param('วันนี้', ago={'days': 0}, period='day'),
        param('เมื่อวานนี้', ago={'days': 1}, period='day'),
        param('2 วัน', ago={'days': 2}, period='day'),
        param('2 ชั่วโมง', ago={'hours': 2}, period='day'),
        param('23 ชม.', ago={'hours': 23}, period='day'),
        param('2 สัปดาห์ 3 วัน', ago={'weeks': 2, 'days': 3}, period='day'),
        param('1 ปี 9 เดือน 1 สัปดาห์', ago={'years': 1, 'months': 9, 'weeks': 1},
              period='week'),
        param('1 ปี 1 เดือน 1 สัปดาห์ 1 วัน 1 ชั่วโมง 1 นาที',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Vietnamese dates
        param('Hôm nay', ago={'days': 0}, period='day'),
        param('Hôm qua', ago={'days': 1}, period='day'),
        param('2 tuần 3 ngày', ago={'weeks': 2, 'days': 3}, period='day'),

        # Belarusian dates
        param('сёння', ago={'days': 0}, period='day'),
        param('учора ў', ago={'days': 1}, period='day'),
        param('ўчора', ago={'days': 1}, period='day'),
        param('пазаўчора', ago={'days': 2}, period='day'),
        param('2 гадзіны таму назад', ago={'hours': 2}, period='day'),
        param('2 гадзіны таму', ago={'hours': 2}, period='day'),
        param('гадзіну назад', ago={'hours': 1}, period='day'),
        param('хвіліну таму', ago={'minutes': 1}, period='day'),
        param('2 гадзіны 21 хвіл. назад', ago={'hours': 2, 'minutes': 21}, period='day'),
        param('каля 23 гадзін назад', ago={'hours': 23}, period='day'),
        param('1 год 2 месяцы', ago={'years': 1, 'months': 2}, period='month'),
        param('1 год, 09 месяцаў, 01 тыдзень', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('2 гады 3 месяцы', ago={'years': 2, 'months': 3}, period='month'),
        param('5 гадоў, 1 месяц, 6 тыдняў, 3 дні, 5 гадзін 1 хвіліну і 3 секунды таму назад',
              ago={'years': 5, 'months': 1, 'weeks': 6, 'days': 3, 'hours': 5, 'minutes': 1, 'seconds': 3},
              period='day'),

        # Polish dates
        param("wczoraj", ago={'days': 1}, period='day'),
        param("1 godz. 2 minuty temu", ago={'hours': 1, 'minutes': 2}, period='day'),
        param("2 lata, 3 miesiące, 1 tydzień, 2 dni, 4 godziny, 15 minut i 25 sekund temu",
              ago={'years': 2, 'months': 3, 'weeks': 1, 'days': 2, 'hours': 4, 'minutes': 15, 'seconds': 25},
              period='day'),
        param("2 minuty temu", ago={'minutes': 2}, period='day'),
        param("15 minut temu", ago={'minutes': 15}, period='day'),

        # Bangla dates
        # param('গতকাল', ago={'days': 1}, period='day'),
        # param('আজ', ago={'days': 0}, period='day'),
        param('1 ঘন্টা আগে', ago={'hours': 1}, period='day'),
        param('প্রায় 1 ঘন্টা আগে', ago={'hours': 1}, period='day'),
        param('1 দিন আগে', ago={'days': 1}, period='day'),
        param('1 সপ্তাহ আগে', ago={'weeks': 1}, period='week'),
        param('2 ঘন্টা আগে', ago={'hours': 2}, period='day'),
        param('প্রায় 23 ঘন্টা আগে', ago={'hours': 23}, period='day'),
        param('1 বছর 2 মাস', ago={'years': 1, 'months': 2}, period='month'),
        param('1 বছর, 09 মাস,01 সপ্তাহ', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1 বছর 11 মাস', ago={'years': 1, 'months': 11}, period='month'),
        param('1 বছর 12 মাস', ago={'years': 1, 'months': 12}, period='month'),
        param('15 ঘন্টা', ago={'hours': 15}, period='day'),
        param('2 মিনিট', ago={'minutes': 2}, period='day'),
        param('3 সেকেন্ড', ago={'seconds': 3}, period='day'),
        param('1000 বছর আগে', ago={'years': 1000}, period='year'),
        param('5000 মাস আগে', ago={'years': 416, 'months': 8}, period='month'),
        param('{} মাস আগে'.format(2013 * 12 + 8), ago={'years': 2013, 'months': 8}, period='month'),
        param('1 বছর, 1 মাস, 1 সপ্তাহ, 1 দিন, 1 ঘন্টা এবং 1 মিনিট আগে',
              ago={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        # param('এখন', ago={'seconds': 0}, period='day'),

        # Hindi dates
        param('1 घंटे पहले', ago={'hours': 1},period='day'),
        param('15 मिनट पहले',ago={'minutes':15},period='day'),
        param('25 सेकंड पूर्व',ago={'seconds':25},period='day'),
        param('1 वर्ष, 8 महीने, 2 सप्ताह', ago={'years': 1, 'months': 8, 'weeks': 2}, period='week'),
        param('1 वर्ष 7 महीने', ago={'years': 1, 'months': 7}, period='month'),
        param('आज', ago={'days': 0}, period='day'),
    ])
    def test_normalized_relative_dates(self, date_string, ago, period):
        date_string = normalize_unicode(date_string)
        self.given_parser(settings={'NORMALIZE': True})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_parsed_by_freshness_parser()
        self.then_date_obj_is_exactly_this_time_ago(ago)
        self.then_period_is(period)

    @parameterized.expand([
        # English dates
        param('tomorrow', in_future={'days': 1}, period='day'),
        param('today', in_future={'days': 0}, period='day'),
        param('in an hour', in_future={'hours': 1}, period='day'),
        param('in about an hour', in_future={'hours': 1}, period='day'),
        param('in 1 day', in_future={'days': 1}, period='day'),
        param('in a week', in_future={'weeks': 1}, period='week'),
        param('in 2 hours', in_future={'hours': 2}, period='day'),
        param('in about 23 hours', in_future={'hours': 23}, period='day'),
        param('in 1 year 2 months', in_future={'years': 1, 'months': 2}, period='month'),
        param('in 1 year, 09 months,01 weeks', in_future={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('in 1 year 11 months', in_future={'years': 1, 'months': 11}, period='month'),
        param('in 1 year 12 months', in_future={'years': 1, 'months': 12}, period='month'),
        param('in 15 hr', in_future={'hours': 15}, period='day'),
        param('in 15 hrs', in_future={'hours': 15}, period='day'),
        param('in 2 min', in_future={'minutes': 2}, period='day'),
        param('in 2 mins', in_future={'minutes': 2}, period='day'),
        param('in 3 sec', in_future={'seconds': 3}, period='day'),
        param('in 1000 years', in_future={'years': 1000}, period='year'),
        param('in 5000 months', in_future={'years': 416, 'months': 8}, period='month'),
        param('in {} months'.format(2013 * 12 + 8), in_future={'years': 2013, 'months': 8}, period='month'),
        param('in 1 year, 1 month, 1 week, 1 day, 1 hour and 1 minute',
              in_future={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('just now', in_future={'seconds': 0}, period='day'),

        # French dates
        param("Aujourd'hui", in_future={'days': 0}, period='day'),
        param('Dans un jour', in_future={'days': 1}, period='day'),
        param('Dans une heure', in_future={'hours': 1}, period='day'),
        param('En 2 heures', in_future={'hours': 2}, period='day'),
        param('Dans environ 23 heures', in_future={'hours': 23}, period='day'),
        param('Dans 1 an 2 mois', in_future={'years': 1, 'months': 2}, period='month'),
        param('En 1 année, 09 mois, 01 semaines', in_future={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('Dans 1 an 11 mois', in_future={'years': 1, 'months': 11}, period='month'),
        param('Dans 1 année, 1 mois, 1 semaine, 1 jour, 1 heure et 1 minute',
              in_future={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),
        param('Dans 40 min', in_future={'minutes': 40}, period='day'),

        # German dates
        param('Heute', in_future={'days': 0}, period='day'),
        param('Morgen', in_future={'days': 1}, period='day'),
        param('in einem Tag', in_future={'days': 1}, period='day'),
        param('in einer Stunde', in_future={'hours': 1}, period='day'),
        param('in 2 Stunden', in_future={'hours': 2}, period='day'),
        param('in etwa 23 Stunden', in_future={'hours': 23}, period='day'),
        param('im 1 Jahr 2 Monate', in_future={'years': 1, 'months': 2}, period='month'),
        param('im 1 Jahr, 09 Monate, 01 Wochen', in_future={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('im 1 Jahr 11 Monate', in_future={'years': 1, 'months': 11}, period='month'),
        param('im 1 Jahr, 1 Monat, 1 Woche, 1 Tag, 1 Stunde und 1 Minute',
              in_future={'years': 1, 'months': 1, 'weeks': 1, 'days': 1, 'hours': 1, 'minutes': 1},
              period='day'),

        # Polish dates
        param("jutro", in_future={'days': 1}, period='day'),
        param("pojutrze", in_future={'days': 2}, period='day'),
        param("za 2 lata, 3 miesiące, 1 tydzień, 2 dni, 4 godziny, 15 minut i 25 sekund",
              in_future={'years': 2, 'months': 3, 'weeks': 1, 'days': 2, 'hours': 4, 'minutes': 15, 'seconds': 25},
              period='day'),
        param("za 2 minuty", in_future={'minutes': 2}, period='day'),
        param("za 15 minut", in_future={'minutes': 15}, period='day'),

        # Turkish dates
        param('yarın', in_future={'days': 1}, period='day'),
        param('2 gün içerisinde', in_future={'days': 2}, period='day'),
        param('4 ay içerisinde', in_future={'months': 4}, period='month'),
        param('3 gün sonra', in_future={'days': 3}, period='day'),
        param('2 ay sonra', in_future={'months': 2}, period='month'),
        param('5 yıl 3 gün sonra', in_future={'years': 5, 'days': 3}, period='day'),
        param('5 gün içinde', in_future={'days': 5}, period='day'),
        param('6 ay içinde', in_future={'months': 6}, period='month'),
        param('5 yıl içinde', in_future={'years': 5}, period='year'),
        param('5 sene içinde', in_future={'years': 5}, period='year'),
        param('haftaya', in_future={'weeks': 1}, period='week'),
        param('gelecek hafta', in_future={'weeks': 1}, period='week'),
        param('gelecek ay', in_future={'months': 1}, period='month'),
        param('gelecek yıl', in_future={'years': 1}, period='year'),

        # Hindi dates
        param('1 वर्ष 10 महीने में', in_future={'years': 1, 'months': 10}, period='month'),
        param('15 घंटे बाद', in_future={'hours': 15}, period='day'),
        param('2 मिनट में', in_future={'minutes': 2}, period='day'),
        param('17 सेकंड बाद', in_future={'seconds': 17}, period='day'),
        param('1 वर्ष, 5 महीने, 1 सप्ताह में', in_future={'years': 1, 'months': 5, 'weeks': 1}, period='week'),
    ])
    def test_relative_future_dates(self, date_string, in_future, period):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_parsed_by_freshness_parser()
        self.then_date_obj_is_exactly_this_time_in_future(in_future)
        self.then_period_is(period)

    @parameterized.expand([
        param('15th of Aug, 2014 Diane Bennett'),
    ])
    def test_insane_dates(self, date_string):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_not_parsed()

    @parameterized.expand([
        param('5000 years ago'),
        param('2014 years ago'),  # We've fixed .now in setUp
        param('{} months ago'.format(2013 * 12 + 9)),
    ])
    def test_dates_not_supported_by_date_time(self, date_string):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_raised(ValueError, ['is out of range',
                                                "('year must be in 1..9999'"])

    @parameterized.expand([
        param('несколько секунд назад', boundary={'seconds': 45}, period='day'),
        param('há alguns segundos', boundary={'seconds': 45}, period='day'),
    ])
    def test_inexplicit_dates(self, date_string, boundary, period):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_parsed_by_freshness_parser()
        self.then_period_is(period)
        self.then_date_obj_is_between(self.now - timedelta(**boundary), self.now)

    @parameterized.expand([
        param('Today at 9 pm', date(2014, 9, 1), time(21, 0)),
        param('Today at 11:20 am', date(2014, 9, 1), time(11, 20)),
        param('Yesterday 1:20 pm', date(2014, 8, 31), time(13, 20)),
        param('the day before yesterday 16:50', date(2014, 8, 30), time(16, 50)),
        param('2 Tage 18:50', date(2014, 8, 30), time(18, 50)),
        param('1 day ago at 2 PM', date(2014, 8, 31), time(14, 0)),
        param('Dnes v 12:40', date(2014, 9, 1), time(12, 40)),
        param('1 week ago at 12:00 am', date(2014, 8, 25), time(0, 0)),
        param('tomorrow at 2 PM', date(2014, 9, 2), time(14, 0)),
    ])
    def test_freshness_date_with_time(self, date_string, date, time):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    @parameterized.expand([
        param('2 hours ago', 'Asia/Karachi', date(2014, 9, 1), time(13, 30)),
        param('3 hours ago', 'Europe/Paris', date(2014, 9, 1), time(9, 30)),
        param('5 hours ago', 'US/Eastern', date(2014, 9, 1), time(1, 30)), # date in DST range
        param('Today at 9 pm', 'Asia/Karachi', date(2014, 9, 1), time(21, 0)),
    ])
    def test_freshness_date_with_pytz_timezones(self, date_string, timezone, date, time):
        self.given_parser(settings={'TIMEZONE': timezone})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    @parameterized.expand([
        param('Today at 4:25 pm', 'US/Mountain', 'UTC', date(2014, 9, 1), time(22, 25)),
        param('Yesterday at 4:25 pm', 'US/Mountain', 'UTC', date(2014, 8, 31), time(22, 25)),
        param('Yesterday', 'US/Mountain', 'UTC', date(2014, 8, 31), time(16, 30)),
        param('Today', 'US/Mountain', 'UTC', date(2014, 9, 1), time(16, 30)),
    ])
    def test_freshness_date_with_timezone_conversion(self, date_string, timezone, to_timezone, date, time):
        self.given_parser(settings={'TIMEZONE': timezone, 'TO_TIMEZONE': to_timezone, 'RELATIVE_BASE': datetime(2014, 9, 1, 10, 30)})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    def test_freshness_date_with_to_timezone_setting(self):
        _settings = settings.replace(**{
            'TIMEZONE': 'local',
            'TO_TIMEZONE': 'UTC',
            'RELATIVE_BASE': datetime(2014, 9, 1, 10, 30)
        })

        parser = dateparser.freshness_date_parser.FreshnessDateDataParser()
        parser.get_local_tz = Mock(return_value=pytz.timezone('US/Eastern'))
        result = parser.get_date_data('1 minute ago', _settings)
        result = result['date_obj']
        self.assertEqual(result.date(), date(2014, 9, 1))
        self.assertEqual(result.time(), time(14, 29))

    @parameterized.expand([
        param('2 hours ago', 'PKT', date(2014, 9, 1), time(13, 30)),
        param('5 hours ago', 'EST', date(2014, 9, 1), time(0, 30)),
        param('3 hours ago', 'MET', date(2014, 9, 1), time(8, 30)),
    ])
    def test_freshness_date_with_timezone_abbreviations(self, date_string, timezone, date, time):
        self.given_parser(settings={'TIMEZONE': timezone})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    @parameterized.expand([
        param('2 hours ago', '+05:00', date(2014, 9, 1), time(13, 30)),
        param('5 hours ago', '-05:00', date(2014, 9, 1), time(0, 30)),
        param('3 hours ago', '+01:00', date(2014, 9, 1), time(8, 30)),
    ])
    def test_freshness_date_with_timezone_utc_offset(self, date_string, timezone, date, time):
        self.given_parser(settings={'TIMEZONE': timezone})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    @parameterized.expand([
        param('Today at 9 pm', date(2010, 6, 4), time(21, 0)),
        param('Today at 11:20 am', date(2010, 6, 4), time(11, 20)),
        param('Yesterday 1:20 pm', date(2010, 6, 3), time(13, 20)),
        param('the day before yesterday 16:50', date(2010, 6, 2), time(16, 50)),
        param('2 Tage 18:50', date(2010, 6, 2), time(18, 50)),
        param('1 day ago at 2 PM', date(2010, 6, 3), time(14, 0)),
        param('Dnes v 12:40', date(2010, 6, 4), time(12, 40)),
        param('1 week ago at 12:00 am', date(2010, 5, 28), time(0, 0)),
        param('yesterday', date(2010, 6, 3), time(13, 15)),
        param('the day before yesterday', date(2010, 6, 2), time(13, 15)),
        param('today', date(2010, 6, 4), time(13, 15)),
        param('an hour ago', date(2010, 6, 4), time(12, 15)),
        param('about an hour ago', date(2010, 6, 4), time(12, 15)),
        param('a day ago', date(2010, 6, 3), time(13, 15)),
        param('a week ago', date(2010, 5, 28), time(13, 15)),
        param('2 hours ago', date(2010, 6, 4), time(11, 15)),
        param('about 23 hours ago', date(2010, 6, 3), time(14, 15)),
        param('1 year 2 months', date(2009, 4, 4), time(13, 15)),
        param('1 year, 09 months,01 weeks', date(2008, 8, 28), time(13, 15)),
        param('1 year 11 months', date(2008, 7, 4), time(13, 15)),
        param('1 year 12 months', date(2008, 6, 4), time(13, 15)),
        param('15 hr', date(2010, 6, 3), time(22, 15)),
        param('15 hrs', date(2010, 6, 3), time(22, 15)),
        param('2 min', date(2010, 6, 4), time(13, 13)),
        param('2 mins', date(2010, 6, 4), time(13, 13)),
        param('3 sec', date(2010, 6, 4), time(13, 14, 57)),
        param('1000 years ago', date(1010, 6, 4), time(13, 15)),
        param('2008 years ago', date(2, 6, 4), time(13, 15)),
        param('5000 months ago', date(1593, 10, 4), time(13, 15)),
        param('{} months ago'.format(2008 * 12 + 8), date(1, 10, 4), time(13, 15)),
        param('1 year, 1 month, 1 week, 1 day, 1 hour and 1 minute ago',
              date(2009, 4, 26), time(12, 14)),
        param('just now', date(2010, 6, 4), time(13, 15))
    ])
    def test_freshness_date_with_relative_base(self, date_string, date, time):
        self.given_parser(settings={'RELATIVE_BASE': datetime(2010, 6, 4, 13, 15)})
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    def given_date_string(self, date_string):
        self.date_string = date_string

    def given_parser(self, settings=None):

        def collecting_get_date_data(get_date_data):
            @wraps(get_date_data)
            def wrapped(*args, **kwargs):
                self.freshness_result = get_date_data(*args, **kwargs)
                return self.freshness_result
            return wrapped
        self.add_patch(patch.object(freshness_date_parser,
                                    'get_date_data',
                                    collecting_get_date_data(freshness_date_parser.get_date_data)))

        self.freshness_parser = Mock(wraps=freshness_date_parser)
        self.add_patch(patch.object(self.freshness_parser, 'now', self.now))

        dt_mock = Mock(wraps=dateparser.freshness_date_parser.datetime)
        dt_mock.utcnow = Mock(return_value=self.now)
        self.add_patch(patch('dateparser.freshness_date_parser.datetime', new=dt_mock))
        self.add_patch(patch('dateparser.date.freshness_date_parser', new=self.freshness_parser))
        self.parser = DateDataParser(settings=settings)

    def when_date_is_parsed(self):
        try:
            self.result = self.parser.get_date_data(self.date_string)
        except Exception as error:
            self.error = error

    def then_date_is(self, date):
        self.assertEqual(date, self.result['date_obj'].date())

    def then_time_is(self, time):
        self.assertEqual(time, self.result['date_obj'].time())

    def then_period_is(self, period):
        self.assertEqual(period, self.result['period'])

    def then_date_obj_is_between(self, low_boundary, high_boundary):
        self.assertGreater(self.result['date_obj'], low_boundary)
        self.assertLess(self.result['date_obj'], high_boundary)

    def then_date_obj_is_exactly_this_time_ago(self, ago):
        self.assertEqual(self.now - relativedelta(**ago), self.result['date_obj'])

    def then_date_obj_is_exactly_this_time_in_future(self, in_future):
        self.assertEqual(self.now + relativedelta(**in_future), self.result['date_obj'])

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result['date_obj'], '"%s" should not be parsed' % self.date_string)

    def then_date_was_parsed_by_freshness_parser(self):
        self.assertEqual(self.result, self.freshness_result)

    def then_error_was_not_raised(self):
        self.assertEqual(NotImplemented, self.error)


if __name__ == '__main__':
    unittest.main()
