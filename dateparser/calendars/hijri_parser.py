from collections import OrderedDict
from functools import reduce
from hijri_converter import convert

from dateparser.calendars import non_gregorian_parser


class hijri:
    @classmethod
    def to_gregorian(cls, year=None, month=None, day=None):
        g = convert.Hijri(
            year=year, month=month, day=day, validate=False
        ).to_gregorian()
        return g.datetuple()

    @classmethod
    def from_gregorian(cls, year=None, month=None, day=None):
        h = convert.Gregorian(year, month, day).to_hijri()
        return h.datetuple()

    @classmethod
    def month_length(cls, year, month):
        h = convert.Hijri(year=year, month=month, day=1)
        return h.month_length()


class HijriDate:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def weekday(self):
        for week in hijri.monthcalendar(self.year, self.month):
            for idx, day in enumerate(week):
                if day == self.day:
                    return idx


class hijri_parser(non_gregorian_parser):
    calendar_converter = hijri
    default_year = 1389
    default_month = 1
    default_day = 1
    non_gregorian_date_cls = HijriDate

    _time_conventions = {
        "am": ["صباحاً"],
        "pm": ["مساءً"],
    }

    _months = OrderedDict(
        [ 
            ("01", ["مُحرم", "محرم"]),
            ("02", ["صفر"]),
            ("03", ["ربيع الأول", "ربيع الاول"]),
            ("04", ["ربيع الثاني", "ربيع الاخر`"]),
            ("05", ["جمادي الأول", "جمادي الاول"]),
            ("06", ["جمادي الثاني", "جمادي الاخر"]),
            ("07", ["رجب"]),
            ("08", ["شعبان"]),
            ("09", ["رمضان"]),
            ("10", ["شوال"]),
            ("11", ["ذو القعدة"]),
            ("12", ["ذو الحجة"]),
        ]
    )


    @classmethod
    def _replace_months(cls, source):
        print("Source is ", source)
        result = source
        for arabic, number in reduce(
            lambda a, b: a + b,
            [
                [(value, month) for value in rpl]
                for month, rpl in cls._months.items()
            ],
        ):
            print("arabic", arabic, " latin", number)
            result = result.replace(arabic, number)
        return result


    @classmethod
    def _replace_time_conventions(cls, source):
        result = source
        for latin, arabics in cls._time_conventions.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result
