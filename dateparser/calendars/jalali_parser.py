# coding: utf-8
from dateparser.parser import _parser
from convertdate import persian
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))

class jalali_parser(_parser):

    def _parse_date_component(self, token, directive):
        print token, directive, len(token)
        day_pairs = dict(zip(persian.WEEKDAYS,  ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']))
        persian_dummy_year, persian_dummy_month, persian_dummy_day = persian.from_gregorian(1999, 3, 17)
        #dummy_jd_year, dummy_jd_month, dummy_jd_day = persian.gregorian.to_jd(1900, 1, 1)
        if directive in ('%A', '%a') and token.title() in persian.WEEKDAYS:
            return datetime.strptime(day_pairs[token.title()], '%A')
        elif directive == '%m' and len(token) == 2 and token.isdigit() and int(token) >= 1 and int(token) <= 12:
            return datetime(*persian.to_gregorian(persian_dummy_year, int(token), persian_dummy_day))
        elif directive == '%d' and len(token) == 2 and token.isdigit():
            if  0 < int(token) <= persian.month_length(persian_dummy_year, persian_dummy_month):
                return datetime(*persian.to_gregorian(persian_dummy_year, persian_dummy_month, int(token)))
            else:
                raise ValueError
        elif directive == '%Y' and len(token) == 4 and token.isdigit():
            return datetime(*persian.to_gregorian(int(token), persian_dummy_month, persian_dummy_day))
        elif directive == '%y' and len(token) == 2 and token.isdigit():
            return datetime(*persian.to_gregorian(int(token), persian_dummy_month, persian_dummy_day))
        else:
            raise ValueError


    @classmethod
    def parse(cls, datestring, settings):
        dateobj, period = super(jalali_parser, cls).parse(datestring ,settings)

        return dateobj - relativedelta(years=1) - relativedelta(days=1), period
