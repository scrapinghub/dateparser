# coding: utf-8
from dateparser.parser import _parser
from convertdate import persian
from datetime import datetime

class persian_datetime(object):
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=0):
        self.year=year
        self.month=month
        self.day=day
        self.hour=hour
        self.minute=minute
        self.microsecond=microsecond
        self.tzinfo=tzinfo

    @classmethod
    def utcnow(cls):
        g_dt = datetime.utcnow()
        p_year, p_month, p_day = persian.from_gregorian(g_dt.year, g_dt.month, g_dt.day)
        return cls(p_year, p_month, p_day, g_dt.hour, g_dt.minute, g_dt.second, g_dt.microsecond, g_dt.tzinfo)

    @classmethod
    def strptime(cls, token, directive):
        persian_gregorian_day_map = dict(zip(persian.WEEKDAYS,  ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))
        year, month, day = 1348, 1, 1
        if directive in ('%A', '%a') and token.title() in persian.WEEKDAYS:
            pass
        elif directive == '%m' and len(token) == 2 and token.isdigit() and int(token) >= 1 and int(token) <= 12:
            month = int(token)
        elif directive == '%d' and len(token) == 2 and token.isdigit() and 0 < int(token) <= persian.month_length(year, month):
            day = int(token)
        elif directive == '%Y' and len(token) == 4 and token.isdigit():
            year = int(token)
        else:
            raise ValueError
        return cls(year,month,day)

class jalali_parser(_parser):
    datetime_cls = persian_datetime
    def _get_datetime_obj(self, **params):
        from convertdate import persian 
        day = params['day']
        if not(0 < day <= persian.month_length(params['year'], params['month'])) and not(self._token_day or hasattr(self, '_token_weekday')):
            day = persian.month_length(params['year'], params['month'])
        year, month, day = persian.to_gregorian(year=params['year'], month=params['month'], day=day)
        c_params = params.copy()
        c_params.update(dict(year=year,month=month, day=day))
        return datetime(**c_params)
