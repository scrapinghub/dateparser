# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from datetime import datetime
from dateutil.relativedelta import relativedelta


def flatten(iterable):
    return [i for item in iterable for i in item]


class FreshnessDateDataParser(object):
    '''Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes
    ago"

    '''
    langs = {
        'en': {
            'word_replacements': [
                ('2 days', ['the day before yesterday']),
                ('1 day', ['yesterday']),
                ('0 days', ['today']),
                ('1', ['an', 'a', 'one']),
                (r'\1 hour\2', ['(\d+)\s*hr(s?)']),
                (r'\1 minute\2', ['(\d+)\s*min(s?)']),
                (r'\1 second\2', ['(\d+)\s*sec(s?)']),
            ],
            'units': {
                'year':     ('year', 'years'),
                'month':    ('month', 'months'),
                'week':     ('week', 'weeks'),
                'day':      ('day', 'days'),
                'hour':     ('hour', 'hours'),
                'minute':   ('minute', 'minutes'),
                'second':   ('second', 'seconds'),
            }
        },
        'de': {
            'word_replacements': [
                ('2 Tag', ['vorgestern']),
                ('1 Tag', ['gestern']),
                ('0 Tage', ['Heute']),
                # Earlier we had an assumption that '\d hours ago' would mean only up to 23 hours,
                # and translated it for 'Today', but then we came across 'vor 29h' on codekicker.de
                (r'vor \1 Stunden', ['vor (\d+)\s*h']),
                (r'vor \1 Minuten', ['vor (\d+)\s*m']),

                ('1', ['einer', 'einem']),
            ],
            'units': {
                'year':     ('Jahr', 'Jahre'),
                'month':    ('Monat', 'Monate'),
                'week':     ('Woche', 'Wochen'),
                'day':      ('Tag', 'Tage'),
                'hour':     ('Stunde', 'Stunden'),
                'minute':   ('Minute', 'Minuten'),
            }
        },
        'es': {
            'word_replacements': [
                ('2 día', ['anteayer']),
                ('1 día', ['ayer']),
                ('0 día', ['hoy']),
                ('1', ['un', 'una']),
            ],
            'units': {
                'year':     ('año', 'años'),
                'month':    ('mes', 'meses'),
                'week':     ('semana', 'semanas'),
                'day':      ('día', 'días'),
                'hour':     ('hora', 'horas'),
                'minute':   ('minuto', 'minutos'),
            }
        },
        'fr': {
            'word_replacements': [
                ('2 jour', ["avant-hier"]),
                ('1 jour', ["hier"]),
                ('0 jours', ["aujourd'hui"]),
                ('1', ['un', 'une']),
            ],
            'units': {
                'year':     ('an', 'année', 'années'),
                'month':    ('mois', 'mois'),
                'week':     ('semaine', 'semaines'),
                'day':      ('jour', 'jours'),
                'hour':     ('heure', 'heures'),
                'minute':   ('minute', 'minutes'),
            }
        },
        'it': {
            'word_replacements': [
                ('0 giorni', ['oggi']),
                ('1 giorno', ['ieri']),
            ],
            'units': {
                'year':     ('anno', 'anni'),
                'month':    ('mese', 'mesi'),
                'week':     ('settimana', 'settimane'),
                'day':      ('giorno', 'giorni'),
                'hour':     ('ora', 'ore'),
                'minute':   ('minuto', 'minuti'),
            }
        },
        'pt': {
            'word_replacements': [
                ('2 dias', ['anteontem']),
                ('1 dia', ['ontem']),
                ('0 dias', ['hoje']),
                ('1', ['um', 'uma']),
                ('44 segundos', ['alguns segundos']),
            ],
            'units': {
                'year':     ('ano', 'anos'),
                'month':    ('mês', 'meses'),
                'week':     ('semana', 'semanas'),
                'day':      ('dia', 'dias'),
                'hour':     ('hora', 'horas'),
                'minute':   ('minuto', 'minutos'),
                'second':   ('segunda', 'segundos'),
            }
        },
        'tr': {
            'word_replacements': [
                ('1 gün', ['dün']),
            ],
            'units': {
                'year':     ('yıl', 'yıl'),
                'month':    ('ay', 'ay'),
                'week':     ('hafta', 'hafta'),
                'day':      ('gün', 'gün'),
                'hour':     ('saat', 'saat'),
                'minute':   ('dakika', 'dakika'),
            }
        },
        'ru': {
            'word_replacements': [
                ('1 дней', ['вчеравчера', 'Вчера в', 'вчера', 'Вчера']),
                ('0 день', ['сегодня']),
                ('час', ['ч']),
                ('минуту', ['мин']),
                ('1 минуту', ['^минуту']),
                ('1 час', ['^час']),
                ('44 секунды', ['несколько секунд']),
            ],
            'units': {
                'year':     ('год', 'года', 'лет'),
                'month':    ('месяц', 'месяца', 'месяцев'),
                'week':     ('неделя', 'недели', 'недель', 'неделю'),
                'day':      ('день', 'дня', 'дней'),
                'hour':     ('час', 'часа', 'часов'),
                'minute':   ('минута', 'минута', 'минут', 'минуту'),
                'second':   ('секунда', 'секунды', 'секунд', 'секунду'),
            }
        },
        'cs': {
            'units': {
                'year':     ('rok', 'roků'),
                'month':    ('měsíc', 'měsíců', 'měsíce'),
                'week':     ('týden', 'týdnů'),
                'day':      ('den', 'dnů', 'dny'),
                'hour':     ('hodina', 'hodin', 'hodiny', 'hodinami'),
                'minute':   ('minuta', 'minut'),
            }
        },
        'cn': {
            'word_replacements': [
                ('1天', ['昨天']),
                ('2天', ['前天']),
            ],
            'units': {
                'year':     ('年',),
                'month':    ('月', '个月'),
                'week':     ('周', '星期'),
                'day':      ('天',),
                'hour':     ('小时',),
                'minute':   ('分', '分钟'),
            },
            'no_word_spacing': True,
        },
        'ar': {
            'word_replacements': [
                ('0 يوم', ['اليوم']),
                ('1 يوم',['يوم أمس']),
                ('2 يوم', ['يومين']),
                (r'\1 أيام', [r'\b(\d{1,2})\s*أيام']),
            ],
            'units': {
                'year':     ('عام', 'سنة'),
                'month':    ('شهر',),
                'week':     ('أسبوع',),
                'day':      ('يوم', 'أيام'),
                'hour':     ('ساعة', 'ساعات'),
                'minute':   ('دقيقة', 'دقائق'),
            },
        }
    }

    def __init__(self, now=None):
        self.now = now or datetime.utcnow()
        self.units_map = {}

        for lang in self.langs.itervalues():
            d = lang['units']
            for k, vlist in d.iteritems():
                for v in vlist:
                    self.units_map[v.lower()] = k

    def parse(self, date_string):
        kwargs = {}
        for lang in self.langs.itervalues():
            td_kwargs = self.try_lang(date_string, lang)
            if len(td_kwargs) > len(kwargs):
                kwargs = td_kwargs

        if not kwargs:
            return None, None

        period = 'day'
        if 'days' not in kwargs:
            for k in ['weeks', 'months', 'years']:
                if k in kwargs:
                    period = k
                    break

        td = relativedelta(**kwargs)

        date = self.now - td

        return date, period

    def apply_replacements(self, date_string, lang):
        if 'word_replacements' in lang:
            for replacement, words in lang['word_replacements']:
                for w in words:
                    date_string = re.sub(ur'\b%s\b' % w, replacement, date_string,
                                         flags=re.IGNORECASE | re.UNICODE)

        return date_string

    def try_lang(self, date_string, lang):
        date_string = self.apply_replacements(date_string, lang)

        if lang.get('no_word_spacing', False):
            pattern = r'(\d+)\s*(%s)'
        else:
            pattern = r'(\d+)\s*(%s)\b'
        pattern = pattern % '|'.join(flatten(lang['units'].values()))

        m = re.findall(pattern, date_string, re.I | re.S | re.U)
        if not m:
            return {}

        kwargs = {}
        for num, unit in m:
            unit = self.units_map[unit.lower()]
            kwargs[unit + 's'] = int(num)

        years = kwargs.get('years', None)
        months = kwargs.get('months', None)

        validate = lambda val, lower, upper: \
            val is None or (lower <= val <= upper)

        if validate(years, 1, 19) and validate(months, 1, 12):
            return kwargs
        else:
            return {}

    def get_date_data(self, date_string):
        date, period = self.parse(date_string)
        return dict(date_obj=date, period=period)

freshness_date_parser = FreshnessDateDataParser()
