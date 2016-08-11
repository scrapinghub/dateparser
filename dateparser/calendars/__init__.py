# coding: utf-8

from __future__ import unicode_literals
from dateparser.parser import _parser
from dateparser.conf import settings
from datetime import datetime

class CalendarBase(object):
    """Base setup class for non-Gregorian calendar system.

    :param source:
        Date string passed to calendar parser.
    :type source: str|unicode
    """

    parser = NotImplemented

    def __init__(self, source):
        self.source = source

    def get_date(self):
        raise NotImplemented

    def get_date(self):
        try:
            date_obj, period = self.parser.parse(self.source, settings)
            return {'date_obj': date_obj, 'period': period}
        except ValueError:
            pass

class CalendarConverter(object):

    @classmethod
    def to_gregorian(cls, year=None, month=None, day=None):
        raise NotImplemented


    @classmethod
    def from_gregorian(cls, year=None, month=None, day=None):
        raise NotImplemented

    @classmethod
    def month_length(cls, year, month):
        raise NotImplemented


class non_gregorian_parser(_parser):

    calendar_converter = NotImplemented
    default_year = NotImplemented
    default_month = NotImplemented
    default_day = NotImplemented
    non_gregorian_date_cls = NotImplemented

    _digits = None
    _months = None
    _weekdays = None
    _number_letters = None


    @classmethod
    def replace_time_conventions(cls, source):
        return source

    @classmethod
    def replace_digits(cls, source):
        return source

    @classmethod
    def replace_months(cls, source):
        return source

    @classmethod
    def replace_weekdays(cls, source):
        return source

    @classmethod
    def replace_time(cls, source):
        return source

    @classmethod
    def replace_days(cls, source):
        return source

    @classmethod
    def to_latin(cls, source):
        result = source
        result = cls.replace_months(result)
        result = cls.replace_weekdays(result)
        result = cls.replace_digits(result)
        result = cls.replace_days(result)
        result = cls.replace_time(result)
        result = cls.replace_time_conventions(result)

        result = result.strip()

        return result

    def _get_datetime_obj(self, **params):
        day = params['day']
        if not(0 < day <= self.calendar_converter.month_length(params['year'], params['month'])) and not(self._token_day or hasattr(self, '_token_weekday')):
            day = persian.month_length(params['year'], params['month'])
        year, month, day = self.calendar_converter.to_gregorian(year=params['year'], month=params['month'], day=day)
        c_params = params.copy()
        c_params.update(dict(year=year,month=month, day=day))
        return datetime(**c_params)

    def _get_datetime_obj_params(self):
        if not self.now:
            self._set_relative_base()
        now_year, now_month, now_day = self.calendar_converter.from_gregorian(self.now.year, self.now.month, self.now.day)
        params = {
            'day': self.day or now_day,
            'month': self.month or now_month,
            'year': self.year or now_year,
            'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0,
        }
        return params

    def _get_date_obj(self, token, directive):
        year, month, day = self.default_year, self.default_month, self.default_day
        if directive == '%A' and self._weekdays and token.title() in self._weekdays:
            pass
        elif directive == '%m' and len(token) <= 2 and token.isdigit() and int(token) >= 1 and int(token) <= 12:
            month = int(token)
        elif directive == '%B' and self._months and token in self._months:
            month = list(self._months.keys()).index(token) + 1
        elif directive == '%d' and len(token) <= 2 and token.isdigit() and 0 < int(token) <= self.calendar_converter.month_length(year, month):
            day = int(token)
        elif directive == '%Y' and len(token) == 4 and token.isdigit():
            year = int(token)
        else:
            raise ValueError
        return self.non_gregorian_date_cls(year, month, day)

    @classmethod
    def parse(cls, datestring, settings):
        datestring = cls.to_latin(datestring)
        return super(non_gregorian_parser, cls).parse(datestring, settings)
