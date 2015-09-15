# coding: utf-8
from __future__ import unicode_literals
from datetime import datetime
import re

from jdatetime import JalaliToGregorian


class JalaliParser(object):
    _skip = ["م"]

    _digits = { "۰": 0, "۱": 1, "۲": 2, "۳": 3, "۴": 4,
                "۵": 5, "۶": 6, "۷": 7, "۸": 8, "۹": 9}

    _months = {
        # pinglish : (persian literals, month index, number of days)
        "Farvardin": (["فروردین"], 1, 31),
        "Ordibehesht": (["اردیبهشت"], 2, 31),
        "Khordad": (["خرداد"], 3, 31),
        "Tir": (["تیر"], 4, 31),
        "Mordad": (["امرداد","مرداد"], 5, 31),
        "Shahrivar": (["شهریور"], 6, 31),
        "Mehr": (["مهر"], 7, 30),
        "Aban": (["آبان"], 8, 30),
        "Azar": (["آذر"], 9, 30),
        "Dey": (["دی"], 10, 30),
        "Bahman": (["بهمن"], 11, 30),
        "Esfand": (["اسفند"], 12, 29),
    }

    _weekdays = {
        "Saturday": ["شنبه"],
        "Sunday": ["یکشنبه"],
        "Monday": ["دوشنبه"],
        "Tuesday": ["سهشنبه", "سه شنبه"],
        "Wednesday": ["چهارشنبه"],
        "Thursday": ["پنجشنبه"],
        "Friday": ["جمعه"],
    }

    _number_letters = {
        0: ["صفر"],
        1: ["یک", "اولین"],
        2: ["دو"],
        3: ["سه", "سوم"],
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
        22: ["بیست و دو"],
        23: ["بیست و سه"],
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

        for persian, latin in [('|'.join(props[0]), key) for key, props in self._months.items()]:
            result = re.sub(persian, latin, result)

        return result

    def replace_weekdays(self, source):
        result = source
        for persian, latin in [('|'.join(values), key) for key, values in self._weekdays.items()]:
            result = re.sub(persian, latin, result)
        return result

    def replace_days(self, source):
        # TODO 
        result = source
        day_pairs = PERSIAN_DAYS.items()
        day_pairs.sort(
                key=lambda (_, num): num,
                reverse=True
            )    
        for persian, number in day_pairs:
            result = result.replace(persian, str(number))
        return result

    def persian_to_latin(self, source):
        result = re.sub('|'.join(self._skip), '', source)
        result = self.replace_months(result)
        result = self.replace_weekdays(result)
        result = self.replace_digits(result)

        result = re.sub(r"[^\w ]", "", result, flags=re.UNICODE)
        result = result.strip()

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

    def get_date(self, persian):
        jdate = self.search_persian_date(persian)
        try:
            gdate = JalaliToGregorian(
                int(jdate['year']),
                self._months[jdate['month']][1],
                int(jdate['day'])
            ).getGregorianList()
            return datetime(gdate[0], gdate[1], gdate[2])
        except:
            pass
