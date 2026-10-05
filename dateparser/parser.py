import calendar
import contextlib
from collections.abc import Callable, Iterable, Iterator
from datetime import datetime, time, timedelta, tzinfo
from functools import partial
from io import StringIO
from typing import TYPE_CHECKING, Any, ClassVar, Literal, overload

import pytz
import regex as re

from dateparser.utils import (
    _get_missing_parts,
    _get_parts,
    _now,
    get_last_day_of_month,
    get_next_leap_year,
    get_previous_leap_year,
    get_timezone_from_tz_string,
    set_correct_day_from_settings,
    set_correct_month_from_settings,
)
from dateparser.utils.strptime import strptime

if TYPE_CHECKING:
    from dateparser.conf import Settings

NSP_COMPATIBLE = re.compile(r"\D+")
MERIDIAN = re.compile(r"am|pm")
MICROSECOND = re.compile(r"\d{1,6}")
EIGHT_DIGIT = re.compile(r"^\d{8}$")
HOUR_MINUTE_REGEX = re.compile(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
_RANGE_DASHES = {"-", "–"}


def no_space_parser_eligibile(datestring: str) -> bool:
    src = NSP_COMPATIBLE.search(datestring)
    return not src or src.group() == ":"


def get_unresolved_attrs(parser_object: object) -> tuple[list[str], list[str]]:
    attrs = ["year", "month", "day"]
    seen = []
    unseen = []
    for attr in attrs:
        if getattr(parser_object, attr, None) is not None:
            seen.append(attr)
        else:
            unseen.append(attr)
    return seen, unseen


date_order_chart = {
    "DMY": "%d%m%y",
    "DYM": "%d%y%m",
    "MDY": "%m%d%y",
    "MYD": "%m%y%d",
    "YDM": "%y%d%m",
    "YMD": "%y%m%d",
}


@overload
def resolve_date_order(order: str, lst: Literal[False] | None = None) -> str: ...


@overload
def resolve_date_order(order: str, lst: Literal[True]) -> list[str]: ...


def resolve_date_order(order: str, lst: bool | None = None) -> str | list[str]:
    chart_list = {
        "DMY": ["day", "month", "year"],
        "DYM": ["day", "year", "month"],
        "MDY": ["month", "day", "year"],
        "MYD": ["month", "year", "day"],
        "YDM": ["year", "day", "month"],
        "YMD": ["year", "month", "day"],
    }

    return chart_list[order] if lst else date_order_chart[order]


class _StrictDateOrderError(ValueError):
    """The date string does not fit DATE_ORDER as STRICT_DATE_ORDER requires:
    a number was read as a part that the order does not put at its position,
    or with "all", a number could not be read in that order at all.
    The other parsers of the locale may still read the date string, but no
    other locale should guess a reading of it."""


_PART_OF_DIRECTIVE = {"%d": "day", "%m": "month", "%y": "year", "%Y": "year"}


def _strict_date_order(settings: "Settings") -> str:
    """Return the STRICT_DATE_ORDER value in effect, which is "none" unless the
    caller set DATE_ORDER."""
    if "DATE_ORDER" in settings._mod_settings:
        return settings.STRICT_DATE_ORDER
    return "none"


def _check_strict_date_order(
    parts: list[str], four_digit_year: bool, date_order: str, strict: str
) -> None:
    """Raise _StrictDateOrderError if *parts*, the parts of the date that were
    read from numbers, in the order they were read, are not where DATE_ORDER
    puts them, as far as *strict*, the STRICT_DATE_ORDER value, requires. A
    month name and a missing part are not in *parts*, so they are not checked:
    "32 DEC" with DMY is still December 2032."""
    if strict == "none":
        return
    order = resolve_date_order(date_order, lst=True)
    if strict == "year":
        # Any number that is not a valid day or month is read as a two-digit
        # year, so check that it is where DATE_ORDER puts the year: in
        # "32 DEC 10" with DMY, 32 is an invalid day, not the year 2032. Of the
        # parts read, those before the year must be exactly those that the order
        # puts before it, whichever way they are misplaced: "10 DEC 32" with MYD
        # reads the day before the year. A four-digit year cannot be anything
        # else.
        if four_digit_year or "year" not in parts:
            return
        before_year = order[: order.index("year")]
        if set(parts[: parts.index("year")]) != set(before_year).intersection(parts):
            raise _StrictDateOrderError(f"The year is not where {date_order} puts it")
        return
    # "all": the day and month must be where DATE_ORDER puts them too, so they
    # are not swapped when they do not fit.
    if four_digit_year:
        # A four-digit year is read wherever it is, and a date that starts
        # with one is read as year, month and day unless DATE_ORDER starts
        # with the year.
        if parts[:1] == ["year"] and not date_order.startswith("Y"):
            order = ["month", "day"]
        parts = [part for part in parts if part != "year"]
    if parts != [part for part in order if part in parts]:
        raise _StrictDateOrderError(f"The date parts are not in {date_order} order")


def _parse_absolute(
    datestring: str,
    settings: "Settings",
    tz: tzinfo | None = None,
    date_order: str | None = None,
) -> tuple[datetime, str | None, tuple[str, ...]]:
    return _parser.parse(datestring, settings, tz, date_order=date_order)


def _parse_nospaces(
    datestring: str,
    settings: "Settings",
    tz: tzinfo | None = None,
    date_order: str | None = None,
) -> tuple[datetime, str, tuple[str, ...]]:
    return _no_spaces_parser.parse(datestring, settings, date_order=date_order)


class _time_parser:
    time_directives: ClassVar[list[str]] = [
        "%H:%M:%S",
        "%I:%M:%S %p",
        "%H:%M",
        "%I:%M %p",
        "%I %p",
        "%H:%M:%S.%f",
        "%I:%M:%S.%f %p",
        "%H:%M %p",
    ]

    def __call__(self, timestring: str) -> time:
        _timestring = timestring
        for directive in self.time_directives:
            try:
                return strptime(timestring.strip(), directive).time()
            except ValueError:
                pass
        raise ValueError(f"{_timestring} does not seem to be a valid time string")


time_parser = _time_parser()


class _no_spaces_parser:
    _dateformats: ClassVar[list[str]] = [
        "%Y%m%d",
        "%Y%d%m",
        "%m%Y%d",
        "%m%d%Y",
        "%d%Y%m",
        "%d%m%Y",
        "%y%m%d",
        "%y%d%m",
        "%m%y%d",
        "%m%d%y",
        "%d%y%m",
        "%d%m%y",
    ]

    _preferred_formats: ClassVar[list[str]] = [
        "%Y%m%d%H%M",
        "%Y%m%d%H%M%S",
        "%Y%m%d%H%M%S.%f",
    ]

    _preferred_formats_ordered_8_digit: ClassVar[list[str]] = [
        "%m%d%Y",
        "%d%m%Y",
        "%Y%m%d",
        "%Y%d%m",
        "%m%Y%d",
        "%d%Y%m",
    ]

    _timeformats: ClassVar[list[str]] = ["%H%M%S.%f", "%H%M%S", "%H%M", "%H"]

    period: ClassVar[dict[str, list[str]]] = {
        "day": ["%d", "%H", "%M", "%S"],
        "month": ["%m"],
    }

    _default_order = resolve_date_order("MDY")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._all = (
            self._dateformats
            + [x + y for x in self._dateformats for y in self._timeformats]
            + self._timeformats
        )

        self.date_formats = {
            "%m%d%y": (
                self._preferred_formats
                + sorted(
                    self._all,
                    key=lambda x: x.lower().startswith("%m%d%y"),
                    reverse=True,
                )
            ),
            "%m%y%d": sorted(
                self._all, key=lambda x: x.lower().startswith("%m%y%d"), reverse=True
            ),
            "%y%m%d": sorted(
                self._all, key=lambda x: x.lower().startswith("%y%m%d"), reverse=True
            ),
            "%y%d%m": sorted(
                self._all, key=lambda x: x.lower().startswith("%y%d%m"), reverse=True
            ),
            "%d%m%y": sorted(
                self._all, key=lambda x: x.lower().startswith("%d%m%y"), reverse=True
            ),
            "%d%y%m": sorted(
                self._all, key=lambda x: x.lower().startswith("%d%y%m"), reverse=True
            ),
        }

    @classmethod
    def _get_period(cls, format_string: str) -> str:
        for pname, pdrv in sorted(cls.period.items(), key=lambda x: x[0]):
            for drv in pdrv:
                if drv in format_string:
                    return pname
        return "year"

    @classmethod
    def _find_best_matching_date(
        cls, datestring: str
    ) -> tuple[datetime, str, tuple[str, ...]] | None:
        for fmt in cls._preferred_formats_ordered_8_digit:
            with contextlib.suppress(Exception):
                dt = strptime(datestring, fmt), cls._get_period(fmt), _get_parts(fmt)
                if len(str(dt[0].year)) == 4:
                    return dt
        return None

    @classmethod
    def parse(
        cls, datestring: str, settings: "Settings", date_order: str | None = None
    ) -> tuple[datetime, str, tuple[str, ...]]:
        if not no_space_parser_eligibile(datestring):
            raise ValueError(f"Unable to parse date from: {datestring}")

        datestring = datestring.replace(":", "")
        if not datestring:
            raise ValueError("Empty string")
        tokens = tokenizer(datestring)
        date_order = date_order or settings.DATE_ORDER
        if date_order:
            order = resolve_date_order(date_order)
        else:
            order = cls._default_order
            if EIGHT_DIGIT.match(datestring):
                dt = cls._find_best_matching_date(datestring)
                if dt is not None:
                    return dt
        nsp = cls()
        found: tuple[tuple[datetime, str, tuple[str, ...]], str] | None = None
        ambiguous: tuple[tuple[datetime, str, tuple[str, ...]], str] | None = None
        for token, _ in tokens.tokenize():
            for fmt in nsp.date_formats[order]:
                with contextlib.suppress(Exception):
                    dt = strptime(token, fmt), cls._get_period(fmt), _get_parts(fmt)
                    if len(str(dt[0].year)) < 4:
                        ambiguous = dt, fmt
                        continue

                    missing = _get_missing_parts(fmt)
                    _check_strict_parsing(missing, settings)
                    found = dt, fmt
                if found:
                    break
            if found:
                break
        found = found or ambiguous
        if found is None:
            raise ValueError(f"Unable to parse date from: {datestring}")
        dt, fmt = found
        # The formats are only sorted by DATE_ORDER, so the one that matched
        # may read the numbers in another order.
        _check_strict_date_order(
            [_PART_OF_DIRECTIVE[directive] for directive in re.findall("%[dmyY]", fmt)],
            four_digit_year="%Y" in fmt,
            date_order=date_order,
            strict=_strict_date_order(settings),
        )
        return dt


def _get_missing_error(missing: Iterable[str]) -> str:
    return "Fields missing from the date string: {}".format(", ".join(missing))


def _check_strict_parsing(missing: list[str], settings: "Settings") -> None:
    if settings.STRICT_PARSING and missing:
        raise ValueError(_get_missing_error(missing))
    if settings.REQUIRE_PARTS and missing:
        errors = [part for part in settings.REQUIRE_PARTS if part in missing]
        if errors:
            raise ValueError(_get_missing_error(errors))


class _parser:
    alpha_directives: ClassVar[dict[str, list[str]]] = {
        "weekday": ["%A", "%a"],
        "month": ["%B", "%b"],
    }

    num_directives: ClassVar[dict[str, list[str]]] = {
        "month": ["%m"],
        "day": ["%d"],
        "year": ["%y", "%Y"],
    }

    day: int | None
    month: int | None
    year: int | None
    time: Callable[[], time] | None
    now: datetime
    _token_day: tuple[str, int] | str | int | None
    _token_month: tuple[str, int] | str | int | None
    _token_year: tuple[str, int] | str | None
    _token_time: str | None

    def __init__(  # noqa: PLR0912, PLR0915
        self,
        tokens: Iterable[tuple[str, int]],
        settings: "Settings",
        date_order: str | None = None,
        tz: tzinfo | None = None,
    ) -> None:
        self.settings = settings
        self._tz = tz
        self._date_order = date_order or settings.DATE_ORDER
        self._strict = _strict_date_order(settings)
        self.tokens = [(t[0].strip(), t[1]) for t in list(tokens)]
        self.filtered_tokens = [
            (t[0], t[1], i) for i, t in enumerate(self.tokens) if t[1] <= 1
        ]
        # Move a meridian written before a time (e.g. Chinese 下午 02:26) after
        # it, where the time parsing below looks for it.
        for i in range(len(self.filtered_tokens) - 1):
            current, following = self.filtered_tokens[i : i + 2]
            preceding = self.filtered_tokens[i - 1][0] if i else ""
            if (
                current[0] in ("am", "pm")
                and ":" in following[0]
                and ":" not in preceding
            ):
                self.filtered_tokens[i : i + 2] = [following, current]

        self.unset_tokens: list[tuple[str, int, str]] = []

        self.day = None
        self.month = None
        self.year = None
        self.time = None

        self.auto_order: list[str] = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None
        self._weekday_modifier = None

        self.ordered_num_directives = {
            k: self.num_directives[k]
            for k in resolve_date_order(self._date_order, lst=True)
        }
        numbers = sorted(
            (t[0] for t in self.filtered_tokens if t[1] == 0 and t[0].isdigit()),
            key=len,
        )
        if (
            not any(t[1] == 1 for t in self.filtered_tokens)
            and len(numbers) == 2
            and len(numbers[0]) <= 2
            and len(numbers[1]) == 4
        ):
            # A year and a single other number (e.g. "05/2020"): the other
            # number is the month whatever the date order.
            self.ordered_num_directives = {
                k: self.num_directives[k] for k in ("month", "day", "year")
            }

        skip_index: list[int] = []
        skip_component: str | None = None
        skip_tokens = ["t", "year", "hour", "minute"]

        for index, token_type_original_index in enumerate(self.filtered_tokens):
            if index in skip_index:
                continue

            token, token_type, original_index = token_type_original_index

            if token in skip_tokens:
                continue

            if token in ("last", "this", "next"):
                if self._weekday_modifier:
                    raise ValueError(f"Unable to parse: {token}")
                self._weekday_modifier = token
                continue

            if self.time is None:
                meridian_index = index + 1

                with contextlib.suppress(Exception):
                    # try case where hours and minutes are separated by a period. Example: 13.20.
                    _is_before_period = self.tokens[original_index + 1][0] == "."
                    _is_after_period = (
                        original_index != 0
                        and self.tokens[original_index - 1][0] == "."
                    )

                    if _is_before_period and not _is_after_period:
                        index_next_token = index + 1
                        next_token = self.filtered_tokens[index_next_token][0]
                        index_in_tokens_for_next_token = self.filtered_tokens[
                            index_next_token
                        ][2]

                        next_token_is_last = (
                            index_next_token == len(self.filtered_tokens) - 1
                        )
                        if (
                            next_token_is_last
                            or self.tokens[index_in_tokens_for_next_token + 1][0] != "."
                        ):
                            new_token = token + ":" + next_token
                            if re.match(HOUR_MINUTE_REGEX, new_token):
                                token = new_token
                                skip_index.append(index + 1)
                                meridian_index += 1

                try:
                    microsecond = MICROSECOND.search(  # type: ignore[union-attr]
                        self.filtered_tokens[index + 1][0]
                    ).group()
                    # Is after time token? raise ValueError if ':' can't be found:
                    token.index(":")
                    # Is after period? raise ValueError if '.' can't be found:
                    self.tokens[self.tokens.index((token, 0)) + 1][0].index(".")
                except Exception:
                    microsecond = None

                if microsecond:
                    meridian_index += 1

                try:
                    meridian = MERIDIAN.search(  # type: ignore[union-attr]
                        self.filtered_tokens[meridian_index][0]
                    ).group()
                except Exception:
                    meridian = None

                if any([":" in token, meridian, microsecond]):
                    if meridian and not microsecond:
                        self._token_time = f"{token} {meridian}"
                        skip_index.append(meridian_index)
                    elif microsecond and not meridian:
                        self._token_time = f"{token}.{microsecond}"
                        skip_index.append(index + 1)
                    elif meridian and microsecond:
                        self._token_time = f"{token}.{microsecond} {meridian}"
                        skip_index.append(index + 1)
                        skip_index.append(meridian_index)
                    else:
                        self._token_time = token
                    self.time = partial(time_parser, self._token_time)
                    continue

            results = self._parse(token_type, token, skip_component=skip_component)
            for res in results:
                if len(token) == 4 and res[0] == "year":
                    skip_component = "year"
                setattr(self, *res)

        known, unknown = get_unresolved_attrs(self)
        unset_tokens = [
            unset_token
            for unset_token in self.unset_tokens
            if not (
                self._token_day and self._is_range(self._token_day[0], unset_token[0])
            )
        ]
        if unset_tokens and self._strict == "all":
            # A four-digit year displaced a number that was read as the year,
            # so that number was not where DATE_ORDER puts the year.
            raise _StrictDateOrderError(
                f"{unset_tokens[0][0]} is not where {self._date_order} puts it"
            )
        _check_strict_date_order(
            self.auto_order,
            four_digit_year=self._token_year is not None
            and len(self._token_year[0]) == 4,
            date_order=self._date_order,
            strict=self._strict,
        )
        if len(unset_tokens) > len(unknown):
            raise ValueError("Too many numbers in date string")
        params: dict[str, int] = {}
        for attr in known:
            params.update({attr: getattr(self, attr)})
        for attr in unknown:
            for token, token_type, _ in unset_tokens:
                if token_type == 0:
                    params.update({attr: int(token)})
                    setattr(self, f"_token_{attr}", token)
                    setattr(self, attr, int(token))

    def _is_range(self, first: object, last: object) -> bool:
        """Return whether *first* and *last* are the ends of a range, e.g. 12
        and 14 in “June 12-14, 2021”. A dash before *first* or after *last*
        makes them part of a date instead, e.g. 4 and 25 in “6-4-25”."""

        def is_dash(index: int) -> bool:
            return (
                0 <= index < len(self.tokens)
                and self.tokens[index][0].lstrip(".") in _RANGE_DASHES
            )

        return any(
            self.tokens[index][0] == first
            and is_dash(index + 1)
            and self.tokens[index + 2][0] == last
            and not is_dash(index - 1)
            and not is_dash(index + 3)
            for index in range(len(self.tokens) - 2)
        )

    @classmethod
    def _has_month_name(cls, tokens: Iterable[tuple[str, int]]) -> bool:
        for token, token_type in tokens:
            if token_type != 1:
                continue
            for directive in cls.alpha_directives["month"]:
                try:
                    strptime(token.strip(), directive)
                    return True
                except ValueError:
                    pass
        return False

    def _month_number_becomes_day(self) -> None:
        """Record in auto_order that the number read as the month is the day,
        now that a month name was found, and that the other end of the range,
        which was read as the day, is dropped. That end comes after the month
        in "12-14 June" with MDY, but before it in "12-12 June" with DMY."""
        if self.day:
            self.auto_order.remove("day")
        self.auto_order[self.auto_order.index("month")] = "day"

    def _unparsed_number_error(self, token: str) -> ValueError:
        """Return the error for a number that fits none of the parts of the date
        that are left in the order."""
        if self._strict == "all" and self._is_date_part(token):
            # The number is a date part, but not where DATE_ORDER puts it, so
            # the date string cannot be read in that order: no other locale
            # may read it either, e.g. as a relative date.
            return _StrictDateOrderError(
                f"{token} is not where {self._date_order} puts it"
            )
        return ValueError(f"Unable to parse: {token}")

    def _is_date_part(self, token: str) -> bool:
        """Return whether *token* can be read as a day, month or year."""
        for directives in self.num_directives.values():
            for directive in directives:
                try:
                    self._get_date_obj(token, directive)
                except ValueError:
                    continue
                return True
        return False

    def _get_period(self) -> str:
        if self.settings.RETURN_TIME_AS_PERIOD and getattr(self, "time", None):
            return "time"

        for period in ["time", "day"]:
            if getattr(self, period, None):
                return "day"

        for period in ["month", "year"]:
            if getattr(self, period, None):
                return period

        return "day"

    def _get_parts(self) -> tuple[str, ...]:
        parts = tuple(part for part in ("year", "month", "day") if getattr(self, part))
        if not parts and (hasattr(self, "_token_weekday") or self.time):
            # A weekday or a time on its own is resolved to a full date by
            # _correct_for_time_frame.
            parts = ("year", "month", "day")
        if self.time:
            parts += ("time",)
        return parts

    def _get_datetime_obj(self, **params: Any) -> datetime:
        try:
            return datetime(**params)
        except ValueError as e:
            error_text = e.__str__()
            error_msgs = ["day is out of range", "day must be in", "must be in range"]
            if any(msg in error_text for msg in error_msgs):
                if not (self._token_day or hasattr(self, "_token_weekday")):
                    # if day is not available put last day of the month
                    params["day"] = get_last_day_of_month(
                        params["year"], params["month"]
                    )
                    return datetime(**params)
                if (
                    not self._token_year
                    and params["day"] == 29
                    and params["month"] == 2
                    and not calendar.isleap(params["year"])
                ):
                    # fix the year when year is not present and it is 29 of February
                    params["year"] = self._get_correct_leap_year(
                        self.settings.PREFER_DATES_FROM, params["year"]
                    )
                    return datetime(**params)
            raise

    def _get_correct_leap_year(self, prefer_dates_from: str, current_year: int) -> int:
        if prefer_dates_from == "future":
            return get_next_leap_year(current_year)
        if prefer_dates_from == "past":
            return get_previous_leap_year(current_year)

        # Default case ('current_period'): return closer leap year
        next_leap_year = get_next_leap_year(current_year)
        previous_leap_year = get_previous_leap_year(current_year)
        next_leap_year_is_closer = (
            next_leap_year - current_year < current_year - previous_leap_year
        )
        return next_leap_year if next_leap_year_is_closer else previous_leap_year

    def _set_relative_base(self) -> None:
        self.now = self.settings.RELATIVE_BASE or _now(self.settings, self._tz)

    def _get_datetime_obj_params(self) -> dict[str, int]:
        if not self.now:
            self._set_relative_base()

        return {
            "day": self.day or self.now.day,
            "month": self.month or self.now.month,
            "year": self.year or self.now.year,
            "hour": 0,
            "minute": 0,
            "second": 0,
            "microsecond": 0,
        }

    def _get_date_obj(self, token: str, directive: str) -> datetime:
        return strptime(token, directive)

    def _results(self) -> datetime:
        missing = [
            field for field in ("day", "month", "year") if not getattr(self, field)
        ]
        _check_strict_parsing(missing, self.settings)
        self._set_relative_base()

        time = self.time() if self.time is not None else None
        params = self._get_datetime_obj_params()

        if time:
            params.update(
                {
                    "hour": time.hour,
                    "minute": time.minute,
                    "second": time.second,
                    "microsecond": time.microsecond,
                }
            )

        return self._get_datetime_obj(**params)

    def _correct_for_time_frame(  # noqa: PLR0912, PLR0915
        self, dateobj: datetime, tz: tzinfo | None
    ) -> datetime:
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        token_weekday, _ = getattr(self, "_token_weekday", (None, None))

        if token_weekday and not (
            self._token_year or self._token_month or self._token_day
        ):
            target = days.index(token_weekday[:3].lower())
            steps_forward = (target - dateobj.weekday()) % 7
            steps_back = (dateobj.weekday() - target) % 7
            modifier = self._weekday_modifier
            if modifier == "next" or (
                not modifier and "future" in self.settings.PREFER_DATES_FROM
            ):
                steps = steps_forward or 7
            elif modifier == "this":
                steps = steps_forward
            elif modifier == "last" or self.settings.PREFER_DATES_FROM == "past":
                steps = -(steps_back or 7)
            else:
                steps = -steps_back

            dateobj = dateobj + timedelta(days=steps)

            # set the token_month here so that it is not subsequently
            # altered by _correct_for_month
            self._token_month = dateobj.month

        # NOTE: If this assert fires, self.now needs to be made offset-aware in a similar
        # way that dateobj is temporarily made offset-aware.
        assert not (self.now.tzinfo is None and dateobj.tzinfo is not None), (
            "`self.now` doesn't have `tzinfo`. Review comment in code for details."
        )

        # Store the original dateobj values so that upon subsequent parsing everything is not
        # treated as offset-aware if offset awareness is changed.
        original_dateobj = dateobj

        # Since date comparisons must be either offset-naive or offset-aware, normalize dateobj
        # to be offset-aware if one or the other is already offset-aware.
        if self.now.tzinfo is not None and dateobj.tzinfo is None:
            dateobj = pytz.utc.localize(dateobj)

        if self.month and not self.year:
            try:
                if self.now < self._correct_for_day(dateobj):
                    if self.settings.PREFER_DATES_FROM == "past":
                        dateobj = dateobj.replace(year=dateobj.year - 1)
                elif self.settings.PREFER_DATES_FROM == "future":
                    dateobj = dateobj.replace(year=dateobj.year + 1)
            except ValueError:
                if dateobj.day == 29 and dateobj.month == 2:
                    valid_year = self._get_correct_leap_year(
                        self.settings.PREFER_DATES_FROM, dateobj.year
                    )
                    dateobj = dateobj.replace(year=valid_year)
                else:
                    raise

        if self._token_year and len(self._token_year[0]) == 2:
            if self.now < dateobj:
                if "past" in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year - 100)
            elif "future" in self.settings.PREFER_DATES_FROM:
                dateobj = dateobj.replace(year=dateobj.year + 100)

        if self._token_time and not any(
            [
                self._token_year,
                self._token_month,
                self._token_day,
                hasattr(self, "_token_weekday"),
            ]
        ):
            tz_offset = timedelta(hours=0)
            if self.settings.RELATIVE_BASE:
                # Convert dateobj to utc time to compare with RELATIVE_BASE
                try:
                    tz = tz or get_timezone_from_tz_string(self.settings.TIMEZONE)
                    tz_offset = tz.utcoffset(dateobj) or tz_offset
                except (pytz.UnknownTimeZoneError, pytz.NonExistentTimeError):
                    pass

            if (
                "past" in self.settings.PREFER_DATES_FROM
                and self.now < dateobj - tz_offset
            ):
                dateobj = dateobj + timedelta(days=-1)
            if (
                "future" in self.settings.PREFER_DATES_FROM
                and self.now > dateobj - tz_offset
            ):
                dateobj = dateobj + timedelta(days=1)

        # Reset dateobj to the original value, thus removing any offset awareness that may
        # have been set earlier.
        return dateobj.replace(tzinfo=original_dateobj.tzinfo)

    def _correct_for_day(self, dateobj: datetime) -> datetime:
        if (
            getattr(self, "_token_day", None)
            or getattr(self, "_token_weekday", None)
            or getattr(self, "_token_time", None)
        ):
            return dateobj

        return set_correct_day_from_settings(
            dateobj, self.settings, current_day=self.now.day
        )

    def _correct_for_month(self, dateobj: datetime) -> datetime:
        if getattr(self, "_token_month", None):
            return dateobj

        return set_correct_month_from_settings(
            dateobj, self.settings, current_month=self.now.month
        )

    @classmethod
    def parse(
        cls,
        datestring: str,
        settings: "Settings",
        tz: tzinfo | None = None,
        date_order: str | None = None,
    ) -> tuple[datetime, str | None, tuple[str, ...]]:
        tokens = list(tokenizer(datestring).tokenize())
        date_order = date_order or settings.DATE_ORDER
        try:
            po = cls(tokens, settings, date_order=date_order, tz=tz)
            dateobj = po._results()
        except ValueError as error:
            if (
                "DATE_ORDER" not in settings._mod_settings
                # The swap would replace a reading that STRICT_DATE_ORDER
                # rejected with a date that the default never gives, and
                # "all" forbids the swap altogether.
                or isinstance(error, _StrictDateOrderError)
                or settings.STRICT_DATE_ORDER == "all"
                or str(error).startswith("Fields missing")
                or cls._has_month_name(tokens)
            ):
                raise
            # The numbers do not fit the date order set by the caller, so read
            # them with the day and month swapped, e.g. "2021-01-13" with YDM.
            swapped = date_order.translate(str.maketrans("DM", "MD"))
            po = cls(tokens, settings, date_order=swapped, tz=tz)
            dateobj = po._results()

        # correction for past, future if applicable
        dateobj = po._correct_for_time_frame(dateobj, tz)

        # correction for preference of month: beginning, current, end
        # must happen before day so that day is derived from the correct month
        dateobj = po._correct_for_month(dateobj)

        # correction for preference of day: beginning, current, end
        dateobj = po._correct_for_day(dateobj)

        period = po._get_period()

        return dateobj, period, po._get_parts()

    def _parse(
        self, token_type: int, token: str, skip_component: str | None = None
    ) -> list[tuple[str, int]]:
        def set_and_return(
            token: str,
            token_type: int,
            component: str,
            dateobj: Any,
            skip_date_order: bool = False,
        ) -> list[tuple[str, int]]:
            if not skip_date_order:
                self.auto_order.append(component)
            setattr(self, f"_token_{component}", (token, token_type))
            return [(component, getattr(dateobj, component))]

        def parse_number(
            token: str, skip_component: str | None = None
        ) -> list[tuple[str, int]]:
            token_type = 0

            num_directives = self.ordered_num_directives
            if (
                skip_component == "year"
                and self.day is None
                and self.month is None
                and not self._date_order.startswith("Y")
            ):
                # The date string starts with a four-digit year (e.g. an
                # ISO 8601 date like "2017-06-22"), so the remaining numeric
                # components are expected in month-day order, unless the date
                # order itself puts the year first (e.g. YDM).
                num_directives = {
                    k: self.num_directives[k] for k in ("month", "day", "year")
                }

            def try_directives(
                skip_directive: str | None = None,
            ) -> list[tuple[str, int]]:
                for component, directives in num_directives.items():
                    if skip_component == component:
                        continue
                    for directive in directives:
                        if directive == skip_directive:
                            continue
                        try:
                            do = self._get_date_obj(token, directive)
                            prev_value = getattr(self, component, None)
                            if not prev_value:
                                return set_and_return(token, token_type, component, do)
                            try:
                                prev_token, prev_type = getattr(
                                    self, f"_token_{component}"
                                )
                                if prev_type == token_type:
                                    do = self._get_date_obj(prev_token, directive)
                            except ValueError:
                                self.unset_tokens.append(
                                    (prev_token, prev_type, component)
                                )
                                return set_and_return(token, token_type, component, do)
                        except ValueError:
                            pass
                raise self._unparsed_number_error(token)

            order = list(self.ordered_num_directives)
            components_after_year = order[order.index("year") + 1 :]
            year_position_already_passed = any(
                getattr(self, component) is not None
                for component in components_after_year
            )
            if year_position_already_passed:
                # A component that the date order places after the year has
                # already been found, so the year position in the date string
                # has already been passed and this number cannot be a
                # two-digit year: in "4月20日" ("April 20"), 20 is the day,
                # not the year 2020 (#519). Read it as a two-digit year only
                # if it cannot be anything else (e.g. 99 in "4-99").
                try:
                    return try_directives(skip_directive="%y")
                except ValueError:
                    pass
            return try_directives()

        def parse_alpha(
            token: str, skip_component: str | None = None
        ) -> list[tuple[str, int]]:
            token_type = 1

            for component, directives in self.alpha_directives.items():
                if skip_component == component:
                    continue
                for directive in directives:
                    with contextlib.suppress(Exception):
                        do = self._get_date_obj(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(
                                token, token_type, component, do, skip_date_order=True
                            )
                        if component == "month" and (
                            not self.day
                            or self._is_range(
                                self._token_month[0],  # type: ignore[index]
                                self._token_day[0],  # type: ignore[index]
                            )
                        ):
                            # A number read as the month becomes the day, which
                            # requires the day to be free, or to be the end of
                            # a range that starts at that number, e.g. 14 in
                            # “12-14 June”.
                            self._month_number_becomes_day()
                            self._token_day = self._token_month
                            self._token_month = token, token_type
                            return [
                                (component, getattr(do, component)),
                                ("day", prev_value),
                            ]
            raise ValueError(f"Unable to parse: {token}")

        handlers: dict[int, Callable[[str, str | None], list[tuple[str, int]]]] = {
            0: parse_number,
            1: parse_alpha,
        }
        return handlers[token_type](token, skip_component)


class tokenizer:
    digits = "0123456789:"
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def _isletter(self, tkn: str) -> bool:
        return tkn in self.letters

    def _isdigit(self, tkn: str) -> bool:
        return tkn in self.digits

    def __init__(self, ds: str) -> None:
        self.instream = StringIO(ds)

    def _switch(self, chara: str, charb: str) -> tuple[int, bool]:
        if self._isdigit(chara):
            return 0, not self._isdigit(charb)

        if self._isletter(chara):
            return 1, not self._isletter(charb)

        return 2, self._isdigit(charb) or self._isletter(charb)

    def tokenize(self) -> Iterator[tuple[str, int]]:
        token = ""
        EOF = False

        while not EOF:
            nextchar = self.instream.read(1)

            if not nextchar:
                EOF = True
                token_type, _ = self._switch(token[-1], nextchar)
                yield token, token_type
                return

            if token:
                token_type, switch = self._switch(token[-1], nextchar)

                if not switch:
                    token += nextchar
                else:
                    yield token, token_type
                    token = nextchar
            else:
                token += nextchar
