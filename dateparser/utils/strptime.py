import calendar
import contextvars
import importlib.util
import sys
from collections.abc import Callable
from datetime import datetime, tzinfo
from time import struct_time
from types import ModuleType
from typing import TYPE_CHECKING, Any

import regex as re

from dateparser.utils import get_timezone_from_tz_string

if TYPE_CHECKING:
    from dateparser.conf import Settings

# Set to the original `%S` value (60) when `strptime` clamps a real leap
# second down to 59, since `datetime` cannot represent it; reset at the top
# of every `strptime` call, so it reflects only the most recent call.
_clamped_leap_second: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "_clamped_leap_second", default=None
)

# The 27 leap seconds IERS has inserted so far (none since 2016-12-31), all at
# 23:59:60 UTC on 30 June or 31 December.
_LEAP_SECOND_JUNE_30_YEARS = frozenset(
    {1972, 1981, 1982, 1983, 1985, 1992, 1993, 1994, 1997, 2012, 2015}
)
_LEAP_SECOND_DECEMBER_31_YEARS = frozenset(
    {
        1972,
        1973,
        1974,
        1975,
        1976,
        1977,
        1978,
        1979,
        1987,
        1989,
        1990,
        1995,
        1998,
        2005,
        2008,
        2016,
    }
)


def _reset_leap_second_flag() -> None:
    _clamped_leap_second.set(None)


def _get_clamped_leap_second() -> int | None:
    return _clamped_leap_second.get()


def _is_known_leap_second(
    year: int, month: int, day: int, hour: int, minute: int
) -> bool:
    """Whether (year, month, day, hour, minute), taken as UTC, is one of the
    historical instants a leap second was actually inserted at."""
    if (hour, minute) != (23, 59):
        return False
    if (month, day) == (6, 30):
        return year in _LEAP_SECOND_JUNE_30_YEARS
    if (month, day) == (12, 31):
        return year in _LEAP_SECOND_DECEMBER_31_YEARS
    return False


def _effective_tz_for_naive_input(
    date_obj: datetime, settings: "Settings"
) -> tzinfo | None:
    """The timezone naive input is interpreted in: `settings.TIMEZONE`,
    resolved for *date_obj*'s specific instant (to handle DST correctly), or
    `None` (treated as UTC) for the default "local" setting.
    """
    if "local" in settings.TIMEZONE.lower():
        return None
    tz = get_timezone_from_tz_string(settings.TIMEZONE)
    if hasattr(tz, "localize"):
        localized: datetime = tz.localize(date_obj)
        return localized.tzinfo
    return tz


def _validate_leap_second(date_obj: datetime, tz: tzinfo | None = None) -> None:
    """Raise `ValueError` if the most recent `strptime` call clamped a leap
    second (`:60`) that does not correspond to a real one.

    `date_obj` must already carry the clamped second (59) and the real
    calendar date; `tz` is the timezone the string's wall-clock value is in,
    if any (the check is undefined, and skipped, for non-fixed-offset zones).
    """
    clamped_second = _get_clamped_leap_second()
    if clamped_second is None:
        return

    # No fixed offset: treat the value as already UTC.
    offset = tz.utcoffset(date_obj) if tz is not None else None
    utc_dt = date_obj - offset if offset is not None else date_obj

    if not _is_known_leap_second(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute
    ):
        raise ValueError(
            f"{date_obj.year:04d}-{date_obj.month:02d}-{date_obj.day:02d} "
            f"{date_obj.hour:02d}:{date_obj.minute:02d}:{clamped_second} "
            "is not a known leap second"
        )


TIME_MATCHER = re.compile(
    r".*?"
    r"(?P<hour>2[0-3]|[0-1]\d|\d):"
    r"(?P<minute>[0-5]\d|\d):"
    r"(?P<second>6[0-1]|[0-5]\d|\d)"
    r"\.(?P<microsecond>[0-9]{1,6})"
)

MS_SEARCHER = re.compile(r"\.(?P<microsecond>[0-9]{1,6})")


def patch_strptime() -> Callable[[str, str], struct_time]:
    """Monkey patching _strptime to avoid problems related with non-english
    locale changes on the system.

    For example, if system's locale is set to fr_FR. Parser won't recognize
    any date since all languages are translated to english dates.
    """
    _strptime_spec = importlib.util.find_spec("_strptime")
    assert _strptime_spec is not None
    assert _strptime_spec.loader is not None
    _strptime: Any = importlib.util.module_from_spec(_strptime_spec)
    _strptime_spec.loader.exec_module(_strptime)
    sys.modules["strptime_patched"] = _strptime

    # Copy the namespace without re-executing calendar, whose enum decorators
    # would modify the original module. English names are rebound only here.
    _calendar = ModuleType("calendar_patched")
    _calendar.__dict__.update(vars(calendar), __name__="calendar_patched")
    sys.modules["calendar_patched"] = _calendar

    _strptime._getlang = lambda: ("en_US", "UTF-8")
    _strptime.calendar = _calendar
    _strptime.calendar.day_abbr = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    _strptime.calendar.day_name = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    _strptime.calendar.month_abbr = [
        "",
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    _strptime.calendar.month_name = [
        "",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]

    strptime_time: Callable[[str, str], struct_time] = _strptime._strptime_time
    return strptime_time


__strptime = patch_strptime()


def _prepare_format(date_string: str, og_format: str) -> tuple[str, str, bool]:
    # Adapted from std lib: https://github.com/python/cpython/blob/e34a5e33049ce845de646cf24a498766a2da3586/Lib/_strptime.py#L448
    regex_format = re.sub(r"([\\.^$*+?\(\){}\[\]|])", r"\\\1", og_format)
    regex_format = re.sub(r"\s+", r"\\s+", regex_format)
    regex_format = re.sub(r"'", "['\u02bc]", regex_format)
    year_in_format = False
    day_of_month_in_format = False
    day_of_year_in_format = False

    def repl(m: re.Match[str]) -> str:
        format_char = m[1]
        if format_char in ("Y", "y", "G"):
            nonlocal year_in_format
            year_in_format = True
        elif format_char == "d":
            nonlocal day_of_month_in_format
            day_of_month_in_format = True
        elif format_char == "j":
            nonlocal day_of_year_in_format
            day_of_year_in_format = True

        return ""

    _ = re.sub(r"%[-_0^#]*[0-9]*([OE]?\\?.?)", repl, regex_format)
    if day_of_month_in_format and not year_in_format:
        current_year = datetime.today().year
        return (
            f"{current_year} {date_string}",
            f"%Y {og_format}",
            day_of_year_in_format,
        )
    return date_string, og_format, day_of_year_in_format


def strptime(date_string: str, format: str) -> datetime:  # noqa: A002
    date_string, prepared_format, day_of_year_in_format = _prepare_format(
        date_string, format
    )
    time_tuple = __strptime(date_string, prepared_format)
    year, month, day, hour, minute, second = time_tuple[:6]

    _clamped_leap_second.set(None)

    if second == 61:
        # `%S` of 61 is only in stdlib's regex for a theoretical double leap
        # second, which has never happened.
        raise ValueError("61 is not a valid value for second")
    if second == 60:
        # `datetime` cannot represent a leap second: clamp it to 59. Callers
        # validate it against the known leap seconds (see
        # `_validate_leap_second`) once the full date is known.
        _clamped_leap_second.set(second)
        second = 59
    obj = datetime(year, month, day, hour, minute, second)

    if day_of_year_in_format and time_tuple.tm_yday != obj.timetuple().tm_yday:
        # A day of year past the end of the parsed year is rolled over into the
        # next year by the std lib (e.g. day 366 of 1999 becomes 2000-01-01),
        # which keeps the original value in tm_yday. Such a day does not belong
        # to the parsed year, so reject it instead of returning another year.
        raise ValueError(
            f"day of year {time_tuple.tm_yday} is out of range for year {obj.year - 1}"
        )

    if "%f" in prepared_format:
        try:
            match_groups = TIME_MATCHER.match(date_string).groupdict()  # type: ignore[union-attr]
            ms = match_groups["microsecond"]
            ms = ms + ((6 - len(ms)) * "0")
            obj = obj.replace(microsecond=int(ms))
        except AttributeError:
            match_groups = MS_SEARCHER.search(date_string).groupdict()  # type: ignore[union-attr]
            ms = match_groups["microsecond"]
            ms = ms + ((6 - len(ms)) * "0")
            obj = obj.replace(microsecond=int(ms))

    return obj
