# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import unittest
from datetime import datetime, timedelta, date, time
from functools import wraps

from dateutil.relativedelta import relativedelta
from mock import Mock, patch
from nose_parameterized import parameterized, param

from dateparser.date import DateDataParser, freshness_date_parser
from tests import BaseTestCase


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

    @parameterized.expand([
        # English dates
        param('yesterday', ago={'days': 1}, period='day'),
        param('the day before yesterday', ago={'days': 2}, period='day'),
        param('today', ago={'days': 0}, period='day'),
        param('an hour ago', ago={'hours': 1}, period='day'),
        param('about an hour ago', ago={'hours': 1}, period='day'),
        param('a day ago', ago={'days': 1}, period='day'),
        param('a week ago', ago={'weeks': 1}, period='week'),
        param('one week ago', ago={'weeks': 1}, period='week'),
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
        param('just now', ago={'seconds':0}, period='day'),

        # French dates
        param("Aujourd'hui", ago={'days': 0}, period='day'),
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
        param('1年09月，01周', ago={'years': 1, 'months': 9, 'weeks': 1}, period='week'),
        param('1年11个月', ago={'years': 1, 'months': 11}, period='month'),
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
    ])
    def test_relative_dates(self, date_string, ago, period):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_error_was_not_raised()
        self.then_date_was_parsed_by_freshness_parser()
        self.then_date_obj_is_exactly_this_time_ago(ago)
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
        self.then_error_was_raised(ValueError, ['year is out of range',
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
    ])
    def test_freshness_date_with_time(self, date_string, date, time):
        self.given_parser()
        self.given_date_string(date_string)
        self.when_date_is_parsed()
        self.then_date_is(date)
        self.then_time_is(time)

    def given_date_string(self, date_string):
        self.date_string = date_string

    def given_parser(self):
        self.add_patch(patch.object(freshness_date_parser, 'now', self.now))

        def collecting_get_date_data(get_date_data):
            @wraps(get_date_data)
            def wrapped(date_string):
                self.freshness_result = get_date_data(date_string)
                return self.freshness_result
            return wrapped
        self.add_patch(patch.object(freshness_date_parser,
                                    'get_date_data',
                                    collecting_get_date_data(freshness_date_parser.get_date_data)))

        self.freshness_parser = Mock(wraps=freshness_date_parser)
        self.add_patch(patch('dateparser.date.freshness_date_parser', new=self.freshness_parser))
        self.parser = DateDataParser()

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

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result['date_obj'], '"%s" should not be parsed' % self.date_string)

    def then_date_was_parsed_by_freshness_parser(self):
        self.assertEqual(self.result, self.freshness_result)

    def then_error_was_not_raised(self):
        self.assertEqual(NotImplemented, self.error)


if __name__ == '__main__':
    unittest.main()
