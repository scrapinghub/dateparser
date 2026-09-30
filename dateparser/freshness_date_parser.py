import contextlib
import re
from datetime import datetime, time, timezone, tzinfo
from typing import TYPE_CHECKING, Any

import regex
from dateutil.relativedelta import relativedelta

from dateparser.utils import (
    _get_localzone,
    apply_timezone,
    localize_timezone,
    set_correct_day_from_settings,
    set_correct_month_from_settings,
    strip_braces,
)

from .parser import time_parser
from .timezone_parser import pop_tz_offset_from_string

if TYPE_CHECKING:
    from .conf import Settings
    from .date import DateData

_UNITS = r"decade|year|month|week|day|hour|minute|second"
_PATTERN = rf"([+-]?\s*(?>\d+(?:[.,\s]\d{{3}}(?!\d))*(?:[.,]\d*)?))\s*({_UNITS})\b"
PATTERN: "re.Pattern[str] | regex.Pattern[str]"
try:
    PATTERN = re.compile(_PATTERN, re.IGNORECASE | re.DOTALL)
except re.error:
    # Python 3.10 has no atomic groups.
    PATTERN = regex.compile(_PATTERN, regex.IGNORECASE | regex.DOTALL)
# Matches the text before a number that is the end of a longer one, e.g. the
# day in "2024-06-01 3 days".
_NUMERIC_PREFIX = re.compile(r"(?<![\d:])\d[\d.,/-]*[.,\s/-]*$")
# "the 1st of last month" translates to " 1 1 month ago".
_DAY_OF_MONTH = re.compile(r"^\s*(\d{1,2})\s+(?!\d{3}\s)(?=(?:in\s+)?\d+\s+month\b)")


class FreshnessDateDataParser:
    """Parses date string like "1 year, 2 months ago" and "3 hours, 50 minutes ago"."""

    def _are_all_words_units(self, date_string: str) -> bool:
        skip = [_UNITS, r"ago|in|\d+", r":|[ap]m"]

        date_string = re.sub(r"\s+", " ", date_string.strip())

        words = [x for x in re.split(r"\W", date_string) if x]
        words = [x for x in words if not re.match("|".join(skip), x)]
        return not words

    def _parse_time(self, date_string: str, settings: "Settings") -> time | None:
        """Attempts to parse time part of date strings like '1 day ago, 2 PM'"""
        date_string = PATTERN.sub("", date_string)
        date_string = re.sub(r"\b(?:ago|in)\b", "", date_string)
        with contextlib.suppress(Exception):
            return time_parser(date_string)
        return None

    def get_local_tz(self) -> tzinfo:
        return _get_localzone()

    def parse(  # noqa: PLR0912, PLR0915
        self, date_string: str, settings: "Settings"
    ) -> tuple[datetime | None, str | None, tuple[str, ...]]:
        date_string = strip_braces(date_string)
        date_string, ptz = pop_tz_offset_from_string(date_string)
        day = None
        if match := _DAY_OF_MONTH.match(date_string):
            day = int(match[1])
            date_string = date_string[match.end() :]
        _time = self._parse_time(date_string, settings)

        _settings_tz = settings.TIMEZONE.lower()

        def apply_time(dateobj: datetime, timeobj: time | None) -> datetime:
            if not isinstance(timeobj, time):
                return dateobj

            return dateobj.replace(
                hour=timeobj.hour,
                minute=timeobj.minute,
                second=timeobj.second,
                microsecond=timeobj.microsecond,
            )

        if settings.RELATIVE_BASE:
            now = settings.RELATIVE_BASE

            if "local" not in _settings_tz:
                now = localize_timezone(now, settings.TIMEZONE)

            if ptz:
                now = now.astimezone(ptz) if now.tzinfo else ptz.localize(now)

            if not now.tzinfo:
                now = now.replace(tzinfo=self.get_local_tz())

        elif ptz:
            localized_now = datetime.now(ptz)

            if "local" in _settings_tz:
                now = localized_now
            else:
                now = apply_timezone(localized_now, settings.TIMEZONE)

        elif "local" not in _settings_tz:
            utc_dt = datetime.now(tz=timezone.utc)
            now = apply_timezone(utc_dt, settings.TIMEZONE)
        else:
            now = datetime.now(self.get_local_tz())

        date, period, parts = self._parse_date(
            date_string, now, settings.PREFER_DATES_FROM
        )

        if date and day is not None:
            if period != "month":
                return None, None, ()
            try:
                date = date.replace(day=day)
            except ValueError:
                return None, None, ()
            period = "day"
            parts += ("day",)

        if date:
            if period == "year":
                date = set_correct_month_from_settings(date, settings, date.month)
            if period in ("year", "month"):
                date = set_correct_day_from_settings(date, settings, date.day)
            old_date = date
            date = apply_time(date, _time)
            if settings.RETURN_TIME_AS_PERIOD and old_date != date:
                period = "time"
            if isinstance(_time, time) and "time" not in parts:
                parts += ("time",)

            if settings.TO_TIMEZONE:
                date = apply_timezone(date, settings.TO_TIMEZONE)

            if not settings.RETURN_AS_TIMEZONE_AWARE or (
                settings.RETURN_AS_TIMEZONE_AWARE
                and "default" == settings.RETURN_AS_TIMEZONE_AWARE
                and not ptz
            ):
                date = date.replace(tzinfo=None)

        return date, period, parts

    def _parse_date(  # noqa: PLR0912
        self, date_string: str, now: datetime, prefer_dates_from: str
    ) -> tuple[datetime, str, tuple[str, ...]] | tuple[None, None, tuple[()]]:
        if not self._are_all_words_units(date_string):
            return None, None, ()

        kwargs, explicit_signs = self.get_kwargs(date_string)

        if not kwargs:
            return None, None, ()
        period = "day"
        if "days" not in kwargs:
            for k in ["weeks", "months", "years", "decades"]:
                if k in kwargs:
                    period = "year" if k == "decades" else k[:-1]
                    break

        going_forward = re.search(r"\bin\b", date_string) or (
            re.search(r"\bfuture\b", prefer_dates_from)
            and not re.search(r"\bago\b", date_string)
        )

        adjusted_kwargs: dict[str, Any] = {}
        for key, value in kwargs.items():
            if explicit_signs.get(key, False) or going_forward:
                adjusted_kwargs[key] = value
            else:
                adjusted_kwargs[key] = -value

        # Fold ``decades`` into ``years`` after each component's sign has been
        # resolved so that an unsigned component combined with an explicitly
        # signed one still follows the default ago/future context (fixes
        # #1304).
        if "decades" in adjusted_kwargs:
            adjusted_kwargs["years"] = adjusted_kwargs.get(
                "years", 0
            ) + 10 * adjusted_kwargs.pop("decades")

        td = relativedelta(**adjusted_kwargs)

        date = now + td

        # The smallest unit in the string determines which parts of the
        # resulting date are meaningful.
        parts: tuple[str, ...]
        if kwargs.keys() & {"seconds", "minutes", "hours"}:
            parts = ("year", "month", "day", "time")
        elif kwargs.keys() & {"days", "weeks"}:
            parts = ("year", "month", "day")
        elif "months" in kwargs:
            parts = ("year", "month")
        else:
            parts = ("year",)

        return date, period, parts

    @staticmethod
    def _parse_number(num: str) -> float:
        # A separator followed by exactly 3 digits groups thousands, any other
        # one is a decimal mark.
        num = "".join(num.split()).replace(",", ".")
        integer, separator, decimals = num.rpartition(".")
        if not separator:
            return float(num)
        if len(decimals) == 3:
            return float(num.replace(".", ""))
        return float(integer.replace(".", "") + "." + decimals)

    def get_kwargs(self, date_string: str) -> tuple[dict[str, float], dict[str, bool]]:
        kwargs: dict[str, float] = {}
        explicit_signs: dict[str, bool] = {}

        for match in PATTERN.finditer(date_string):
            num, unit = match.groups()
            num = num.lstrip()
            start = match.start()
            # A number separated from the match only by whitespace, e.g. the 1
            # in "year 1 40 minute", is a fragment only if the match starts
            # with what could be a digit group of it.
            if (
                start
                and not date_string[start - 1].isalpha()
                and (prefix := _NUMERIC_PREFIX.search(date_string, 0, start))
                and (not prefix.group().rstrip().isdigit() or re.match(r"\d{3}", num))
            ):
                return {}, {}
            unit += "s"
            explicit_signs[unit] = num[0] in "+-"
            kwargs[unit] = float(num) if num.isdecimal() else self._parse_number(num)

        return kwargs, explicit_signs

    def get_date_data(self, date_string: str, settings: "Settings") -> "DateData":
        from dateparser.date import DateData  # noqa: PLC0415

        date, period, parts = self.parse(date_string, settings)
        return DateData(date_obj=date, period=period, parts=parts)


freshness_date_parser = FreshnessDateDataParser()
