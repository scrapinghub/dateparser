import re
from typing import ClassVar

from hijridate import Gregorian, Hijri

from dateparser.calendars import non_gregorian_parser


class hijri:
    @classmethod
    def to_gregorian(cls, year: int, month: int, day: int) -> tuple[int, int, int]:
        g = Hijri(year=year, month=month, day=day, validate=False).to_gregorian()
        return g.datetuple()

    @classmethod
    def from_gregorian(cls, year: int, month: int, day: int) -> tuple[int, int, int]:
        h = Gregorian(year, month, day).to_hijri()
        return h.datetuple()

    @classmethod
    def month_length(cls, year: int, month: int) -> int:
        h = Hijri(year=year, month=month, day=1)
        return h.month_length()


class HijriDate:
    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day


class hijri_parser(non_gregorian_parser):
    calendar_converter = hijri
    default_year = 1389
    default_month = 1
    default_day = 1
    non_gregorian_date_cls = HijriDate

    _digit_table: ClassVar[dict[int, int]] = str.maketrans(
        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"
    )

    # Names are matched after removing tatweel and diacritics, and mapping
    # alef, yeh and teh marbuta variants to ا, ي and ه.
    _normalization: ClassVar[dict[int, int | None]] = str.maketrans(
        "أإآىیة",
        "اااييه",
        "\u0640\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670",
    )
    # Keys are uppercase so that the parser does not read "am" in them as a
    # meridian.
    _months: ClassVar[dict[str, tuple[int, str]]] = {
        "MUHARRAM": (1, "محرم"),
        "SAFAR": (2, "صفر"),
        "RABIALAWWAL": (3, "ربيع (?:ال)?اول[يه]?"),
        "RABIALTHANI": (4, "ربيع (?:ال)?(?:ثاني|اخر)[يه]?"),
        "JUMADAALULA": (5, "جمادي (?:ال)?اول[يه]?"),
        "JUMADAALAKHIRAH": (6, "جمادي (?:ال)?(?:ثاني|اخر)[يه]?"),
        "RAJAB": (7, "رجب"),
        "SHABAN": (8, "شعبان"),
        "RAMADAN": (9, "رمضان"),
        "SHAWWAL": (10, "شوال"),
        "DHUALQADAH": (11, "ذ[وي] ?القعده"),
        "DHUALHIJJAH": (12, "ذ[وي] ?الحجه"),
    }
    # The first word of a month name that needs a second one.
    _incomplete_month: ClassVar[re.Pattern[str]] = re.compile(
        r"(?<!\w)(?:ربيع|جمادي)(?!\w)"
    )

    _time_conventions: ClassVar[dict[str, list[str]]] = {
        "am": ["صباحا"],
        "pm": ["مساء"],
    }

    @classmethod
    def to_latin(cls, source: str) -> str:
        return super().to_latin(source.translate(cls._normalization))

    @classmethod
    def _replace_digits(cls, source: str) -> str:
        return source.translate(cls._digit_table)

    @classmethod
    def _replace_months(cls, source: str) -> str:
        result = source
        for latin, (_, pattern) in cls._months.items():
            result = re.sub(rf"(?<!\w)(?:ال)?(?:{pattern})(?!\w)", latin, result)
        if cls._incomplete_month.search(result):
            raise ValueError(f"Incomplete month name in {source!r}")
        return result

    @classmethod
    def _replace_time_conventions(cls, source: str) -> str:
        result = source
        for latin, arabics in cls._time_conventions.items():
            for arabic in arabics:
                result = result.replace(arabic, latin)
        return result

    def handle_two_digit_year(self, year: int) -> int:
        if year >= 90:
            return year + 1300
        return year + 1400
