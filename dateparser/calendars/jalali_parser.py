# coding: utf-8
from dateparser.parser import _parser
from convertdate import persian
from datetime import datetime

class persian_date(object):
    def __init__(self, year, month, day):
        self.year=year
        self.month=month
        self.day=day

class jalali_parser(_parser):

    _months = [
        # pinglish : (persian literals, month index, number of days)
        "Farvardin",
        "Ordibehesht",
        "Khordad",
        "Tir",
        "Mordad",
        "Shahrivar",
        "Mehr",
        "Aban",
        "Azar",
        "Dey",
        "Bahman",
        "Esfand",
    ]

    def _get_datetime_obj(self, **params):
        from convertdate import persian 
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
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        persian_gregorian_day_map = dict(zip(persian.WEEKDAYS,  days))
        year, month, day = 1348, 1, 1
        if directive in ('%A', '%a') and (token.title() in persian.WEEKDAYS or token.title() in days):
            print 'WHOOP ', token
        elif directive == '%m' and len(token) == 2 and token.isdigit() and int(token) >= 1 and int(token) <= 12:
            month = int(token)
        elif directive == '%B' and token in self._months:
            month = self._months.index(token) + 1
        elif directive == '%d' and len(token) == 2 and token.isdigit() and 0 < int(token) <= persian.month_length(year, month):
            day = int(token)
        elif directive == '%Y' and len(token) == 4 and token.isdigit():
            year = int(token)
        else:
            raise ValueError
        return persian_date(year,month,day)
