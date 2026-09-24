from hijridate import Gregorian, Hijri

from dateparser.calendars import non_gregorian_parser


class hijri:
    @classmethod
    def to_gregorian(cls, year=None, month=None, day=None):
        g = Hijri(year=year, month=month, day=day, validate=False).to_gregorian()
        return g.datetuple()

    @classmethod
    def from_gregorian(cls, year=None, month=None, day=None):
        h = Gregorian(year, month, day).to_hijri()
        return h.datetuple()

    @classmethod
    def month_length(cls, year, month):
        h = Hijri(year=year, month=month, day=1)
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

    _digits = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

    # Month names are matched after mapping alef and yeh variants to ا and ي.
    # Arabic letters are separators for the tokenizer, so a variant also
    # covers any name that starts with it, e.g. جمادي الاول covers جمادي الاولي.
    # Keys are uppercase so that the parser does not read "am" in them as a
    # meridian.
    _alef_yeh = str.maketrans("أإآىی", "ااايي")
    _months = {
        "MUHARRAM": ["محرم"],
        "SAFAR": ["صفر"],
        "RABIALAWWAL": ["ربيع الاول"],
        "RABIALTHANI": ["ربيع الثاني", "ربيع الاخر"],
        "JUMADAALULA": ["جمادي الاول"],
        "JUMADAALAKHIRAH": ["جمادي الثاني", "جمادي الاخر"],
        "RAJAB": ["رجب"],
        "SHABAN": ["شعبان"],
        "RAMADAN": ["رمضان"],
        "SHAWWAL": ["شوال"],
        "DHUALQADAH": ["ذو القعدة", "ذي القعدة"],
        "DHUALHIJJAH": ["ذو الحجة", "ذي الحجة"],
    }

    _time_conventions = {
        "am": ["صباحاً"],
        "pm": ["مساءً"],
    }

    @classmethod
    def _replace_digits(cls, source):
        return source.translate(cls._digits)

    @classmethod
    def _replace_months(cls, source):
        result = source.translate(cls._alef_yeh)
        for latin, arabics in cls._months.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result

    @classmethod
    def _replace_time_conventions(cls, source):
        result = source
        for latin, arabics in cls._time_conventions.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result

    def handle_two_digit_year(self, year):
        if year >= 90:
            return year + 1300
        else:
            return year + 1400
