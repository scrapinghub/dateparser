# coding: utf-8

from __future__ import unicode_literals

import re

from dateparser.parser import _parser
from convertdate import persian
from datetime import datetime
from collections import OrderedDict
from functools import reduce


class persian_date(object):
    def __init__(self, year, month, day):
        self.year=year
        self.month=month
        self.day=day

    def weekday(self):
        for week in persian.monthcalendar(self.year, self.month):
            for idx, day in enumerate(week):
                if day==self.day:
                    return idx

class jalali_parser(_parser):

    _digits = {"۰": 0, "۱": 1, "۲": 2, "۳": 3, "۴": 4,
               "۵": 5, "۶": 6, "۷": 7, "۸": 8, "۹": 9}

    _months = OrderedDict([
        # pinglish : (persian literals, month index, number of days)
        ("Farvardin", (1, 31, ["فروردین"])),
        ("Ordibehesht", (2, 31, ["اردیبهشت"])),
        ("Khordad", (3, 31, ["خرداد"])),
        ("Tir", (4, 31, ["تیر"])),
        ("Mordad", (5, 31, ["امرداد", "مرداد"])),
        ("Shahrivar", (6, 31, ["شهریور", "شهريور"])),
        ("Mehr", (7, 30, ["مهر"])),
        ("Aban", (8, 30, ["آبان"])),
        ("Azar", (9, 30, ["آذر"])),
        ("Dey", (10, 30, ["دی"])),
        ("Bahman", (11, 30, ["بهمن", "بهن"])),
        ("Esfand", (12, 29, ["اسفند"])),
    ])

    _weekdays = OrderedDict([
        ("Sunday", ["یکشنبه"]),
        ("Monday", ["دوشنبه"]),
        ("Tuesday", ["سهشنبه", "سه شنبه"]),
        ("Wednesday", ["چهارشنبه", "چهار شنبه"]),
        ("Thursday", ["پنجشنبه", "پنج شنبه"]),
        ("Friday", ["جمعه"]),
        ("Saturday", ["روز شنبه", "شنبه"]),
    ])

    _number_letters = {
        0: ["صفر"],
        1: ["یک", "اول"],
        2: ["دو"],
        3: ["سه", "سو"],
        4: ["چهار"],
        5: ["پنج"],
        6: ["شش"],
        7: ["هفت"],
        8: ["هشت"],
        9: ["نه"],
        10: ["ده"],
        11: ["یازده"],
        12: ["دوازده"],
        13: ["سیزده"],
        14: ["چهارده"],
        15: ["پانزده"],
        16: ["شانزده"],
        17: ["هفده"],
        18: ["هجده"],
        19: ["نوزده"],
        20: ["بیست"],
        21: ["بیست و یک"],
        22: ["بیست و دو", "بیست ثانیه"],
        23: ["بیست و سه", "بیست و سو"],
        24: ["بیست و چهار"],
        25: ["بیست و پنج"],
        26: ["بیست و شش"],
        27: ["بیست و هفت"],
        28: ["بیست و هشت"],
        29: ["بیست و نه"],
        30: ["سی"],
        31: ["سی و یک"],
    }

    @classmethod
    def replace_digits(cls, source):
        result = source
        for pers_digit, number in cls._digits.items():
            result = result.replace(pers_digit, str(number))
        return result

    @classmethod
    def replace_months(cls, source):
        result = source
        for persian, latin in reduce(
                lambda a, b: a + b,
                [[(value, month) for value in repl[-1]] for month, repl in cls._months.items()]):
            result = result.replace(persian, latin)
        return result

    @classmethod
    def replace_weekdays(cls, source):
        result = source
        for persian, latin in reduce(
                lambda a, b: a + b,
                [[(value, weekday) for value in repl] for weekday, repl in cls._weekdays.items()]):
            result = result.replace(persian, latin)
        return result

    @classmethod
    def replace_time(cls, source):
        def only_numbers(match_obj):
            matched_string = match_obj.group()
            return re.sub(r'\D', ' ', matched_string)
        hour_pattern = r'ساعت\s+\d{2}'
        minute_pattern = r'\d{2}\s+دقیقه'
        second_pattern = r'\d{2}\s+ثانیه'
        result = re.sub(hour_pattern, only_numbers, source)
        result = re.sub(minute_pattern, only_numbers, result)
        result = re.sub(second_pattern, only_numbers, result)
        result = re.sub(r'\s+و\s+', ':', result)
        result = result.replace('ساعت', '')
        return result

    @classmethod
    def replace_days(cls, source):
        result = re.sub(r'ام|م|ین', '', source)  # removes persian variant of th/first/second/third
        day_pairs = list(cls._number_letters.items())

        def comp_key(tup):
            return tup[0]

        day_pairs.sort(key=comp_key, reverse=True)

        thirteen, thirty = day_pairs[-14], day_pairs[1]
        day_pairs[-14] = thirty
        day_pairs[1] = thirteen

        for persian, number in reduce(
                lambda a, b: a + b,
                [[(val, repl) for val in persian] for repl, persian in day_pairs]):
            result = result.replace(persian, str(number))
        return result

    @classmethod
    def to_latin(cls, source):
        result = source
        result = cls.replace_months(result)
        result = cls.replace_weekdays(result)
        result = cls.replace_digits(result)
        result = cls.replace_days(result)
        result = cls.replace_time(result)

        result = result.strip()

        return result


    def _get_datetime_obj(self, **params):
        day = params['day']
        if not(0 < day <= persian.month_length(params['year'], params['month'])) and not(self._token_day or hasattr(self, '_token_weekday')):
            day = persian.month_length(params['year'], params['month'])
        year, month, day = persian.to_gregorian(year=params['year'], month=params['month'], day=day)
        c_params = params.copy()
        c_params.update(dict(year=year,month=month, day=day))
        return datetime(**c_params)

    def _get_datetime_obj_params(self):
        if not self.now:
            self._set_relative_base()
        persian_now_year, persian_now_month, persian_now_day = persian.from_gregorian(self.now.year, self.now.month, self.now.day)
        params = {
            'day': self.day or persian_now_day,
            'month': self.month or persian_now_month,
            'year': self.year or persian_now_year,
            'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0,
        }
        return params

    def _get_date_obj(self, token, directive):
        year, month, day = 1348, 1, 1
        if directive == '%A' and token.title() in self._weekdays:
            pass
        elif directive == '%m' and len(token) <= 2 and token.isdigit() and int(token) >= 1 and int(token) <= 12:
            month = int(token)
        elif directive == '%B' and token in self._months:
            month = list(self._months.keys()).index(token) + 1
        elif directive == '%d' and len(token) <= 2 and token.isdigit() and 0 < int(token) <= persian.month_length(year, month):
            day = int(token)
        elif directive == '%Y' and len(token) == 4 and token.isdigit():
            year = int(token)
        else:
            raise ValueError
        return persian_date(year,month,day)

    @classmethod
    def parse(cls, datestring, settings):
        datestring = cls.to_latin(datestring)
        return super(jalali_parser, cls).parse(datestring, settings)

