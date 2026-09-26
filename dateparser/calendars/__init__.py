from collections.abc import Callable
from datetime import datetime, tzinfo
from typing import Any

from dateparser.conf import Settings, settings
from dateparser.date import DateData
from dateparser.parser import _parser


class CalendarBase:
    """Base setup class for non-Gregorian calendar system.

    :param source:
        Date string passed to calendar parser.
    :type source: str
    """

    parser: type["non_gregorian_parser"] = NotImplemented

    def __init__(self, source: str) -> None:
        self.source = source

    def get_date(self) -> DateData | None:
        try:
            date_obj, period = self.parser.parse(self.source, settings)
            return DateData(date_obj=date_obj, period=period)
        except ValueError:
            pass
        return None


class non_gregorian_parser(_parser):
    calendar_converter: Any = NotImplemented
    default_year: int = NotImplemented
    default_month: int = NotImplemented
    default_day: int = NotImplemented
    non_gregorian_date_cls: Callable[[int, int, int], Any] = NotImplemented

    _digits: dict[str, int] | None = None
    _months: dict[str, tuple[int, int, list[str]]] | None = None
    _weekdays: dict[str, list[str]] | None = None
    _number_letters: dict[int, list[str]] | None = None

    @classmethod
    def _replace_time_conventions(cls, source: str) -> str:
        return source

    @classmethod
    def _replace_digits(cls, source: str) -> str:
        return source

    @classmethod
    def _replace_months(cls, source: str) -> str:
        return source

    @classmethod
    def _replace_weekdays(cls, source: str) -> str:
        return source

    @classmethod
    def _replace_time(cls, source: str) -> str:
        return source

    @classmethod
    def _replace_days(cls, source: str) -> str:
        return source

    @classmethod
    def to_latin(cls, source: str) -> str:
        result = source
        result = cls._replace_months(result)
        result = cls._replace_weekdays(result)
        result = cls._replace_digits(result)
        result = cls._replace_days(result)
        result = cls._replace_time(result)
        result = cls._replace_time_conventions(result)

        result = result.strip()

        return result

    def handle_two_digit_year(self, year: int) -> int:
        raise ValueError

    def _get_datetime_obj(self, **params: Any) -> datetime:
        day = params["day"]
        year = params["year"]
        month = params["month"]
        if not (0 < day <= self.calendar_converter.month_length(year, month)) and not (
            self._token_day or hasattr(self, "_token_weekday")
        ):
            day = self.calendar_converter.month_length(year, month)
        year, month, day = self.calendar_converter.to_gregorian(
            year=year, month=month, day=day
        )
        c_params = params.copy()
        c_params.update(dict(year=year, month=month, day=day))
        return datetime(**c_params)

    def _get_datetime_obj_params(self) -> dict[str, int]:
        if not self.now:
            self._set_relative_base()
        now_year, now_month, now_day = self.calendar_converter.from_gregorian(
            self.now.year, self.now.month, self.now.day
        )
        params = {
            "day": self.day or now_day,
            "month": self.month or now_month,
            "year": self.year or now_year,
            "hour": 0,
            "minute": 0,
            "second": 0,
            "microsecond": 0,
        }
        return params

    def _get_date_obj(self, token: str, directive: str) -> Any:
        year, month, day = self.default_year, self.default_month, self.default_day
        token_len = len(token)
        is_digit = token.isdigit()
        if directive == "%A" and self._weekdays and token.title() in self._weekdays:
            pass
        elif (
            directive == "%m" and token_len <= 2 and is_digit and 1 <= int(token) <= 12
        ):
            month = int(token)
        elif directive == "%B" and self._months and token in self._months:
            month = list(self._months.keys()).index(token) + 1
        elif (
            directive == "%d"
            and token_len <= 2
            and is_digit
            and 0 < int(token) <= self.calendar_converter.month_length(year, month)
        ):
            day = int(token)
        elif directive == "%Y" and token_len == 4 and is_digit:
            year = int(token)
        elif directive == "%Y" and token_len == 2 and is_digit:
            year = self.handle_two_digit_year(int(token))
        else:
            raise ValueError
        return self.non_gregorian_date_cls(year, month, day)

    @classmethod
    def parse(
        cls,
        datestring: str,
        settings: Settings,
        tz: tzinfo | None = None,
        date_order: str | None = None,
    ) -> tuple[datetime, str | None]:
        datestring = cls.to_latin(datestring)
        return super().parse(datestring, settings, tz, date_order)
