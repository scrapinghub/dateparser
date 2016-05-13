# coding: utf-8
from __future__ import unicode_literals

import regex as re
from collections import OrderedDict
from datetime import datetime, time
from functools import reduce

from jdatetime import JalaliToGregorian
from dateutil.parser import parse

from . import CalendarBase


def validate_time(string):
    if string.find(':') != -1:
        return string

    persian_time_map = [
        (u'\u0633\u0627\u0639\u062a', 'hour'),
        (u'\u062f\u0642\u06cc\u0642\u0647', 'minute'),
        (u'\u062b\u0627\u0646\u06cc\u0647', 'second')
    ]

    result_dict = {}
    template = '%(hour)s:%(minute)s:%(second)s'
    string = string.replace(u'و', '').strip()

    for persian, latin in persian_time_map:
        cursor = string.find(persian)
        if cursor == -1:
            result_dict[latin] = '00'
            continue
        elif cursor > 0:
            cursor_back = cursor - 3
            if cursor_back == -1:
                cursor_back = 0
            result = string[cursor_back: cursor]
        else:
            cursor += len(persian)
            result = string[cursor: cursor+3]

        result_dict[latin] = result.strip()

    return template % result_dict


class JalaliParser(CalendarBase):
    """Calendar parser class for Jalali calendar."""

    def __init__(self, source):
        super(JalaliParser, self).__init__(source)
        self.translated = None

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

    _weekdays = [
        ("Sunday", ["یکشنبه"]),
        ("Monday", ["دوشنبه"]),
        ("Tuesday", ["سهشنبه", "سه شنبه"]),
        ("Wednesday", ["چهارشنبه", "چهار شنبه"]),
        ("Thursday", ["پنجشنبه", "پنج شنبه"]),
        ("Friday", ["جمعه"]),
        ("Saturday", ["روز شنبه", "شنبه"]),
    ]

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

    def replace_digits(self, source):
        result = source
        for pers_digit, number in self._digits.items():
            result = result.replace(pers_digit, str(number))
        return result

    def replace_months(self, source):
        result = source
        for persian, latin in reduce(
                lambda a, b: a + b,
                [[(value, month) for value in repl[-1]] for month, repl in self._months.items()]):
            result = result.replace(persian, latin)
        return result

    def replace_weekdays(self, source):
        result = source
        for persian, latin in reduce(
                lambda a, b: a + b,
                [[(value, weekday) for value in repl] for weekday, repl in self._weekdays]):
            result = result.replace(persian, latin)
        return result

    def replace_days(self, source):
        result = re.sub(r'ام|م|ین', '', source)  # removes persian variant of th/first/second/third
        day_pairs = list(self._number_letters.items())

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

    def persian_to_latin(self, source):
        result = source
        result = self.replace_months(result)
        result = self.replace_weekdays(result)
        result = self.replace_digits(result)
        result = self.replace_days(result)

        result = result.strip()

        self.translated = result
        return result

    def search_persian_date(self, persian):
        latin = self.persian_to_latin(persian)
        rx_months = r"(?P<month>%s)" % r'|'.join(
            [month for month in self._months.keys()]
        )

        match = None
        for regex in [
                r"(?:^|[^\d])(?P<day>\d+)[ ,]+%s[ ,]+(?P<year>\d+)(?:[^\d]|$)" % rx_months
            ]:
            match = re.search(regex, latin)
            if match:
                break

        if match:
            return match.groupdict()

    def search_time(self):
        if not self.translated:
            self.translated = self.persian_to_latin(self.source)

        result = self.translated

        time_pointers = ['ساعت']
        for splitter in time_pointers:
            try:
                _, timestr = result.split(splitter, 1)
                timeobj = parse(validate_time(timestr)).time()
                return timeobj
            except ValueError:
                pass

        return time(0, 0)

    def get_date(self):
        """Output method for Jalali calendar parser."""
        jdate = self.search_persian_date(self.source)
        gtime = self.search_time()
        try:
            gdate = JalaliToGregorian(
                int(jdate['year']),
                self._months[jdate['month']][0],
                int(jdate['day'])
            ).getGregorianList()
            return datetime(gdate[0], gdate[1], gdate[2],
                            gtime.hour, gtime.minute, gtime.second)
        except TypeError:
            pass
