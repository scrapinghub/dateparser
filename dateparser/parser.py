import calendar
import contextlib
from datetime import datetime, timedelta, timezone
from io import StringIO
from typing import ClassVar

import pytz
import regex as re

from dateparser.utils import (
    _get_missing_parts,
    get_last_day_of_month,
    get_next_leap_year,
    get_previous_leap_year,
    get_timezone_from_tz_string,
    set_correct_day_from_settings,
    set_correct_month_from_settings,
)
from dateparser.utils.strptime import strptime

NSP_COMPATIBLE = re.compile(r"\D+")
MERIDIAN = re.compile(r"am|pm")
MICROSECOND = re.compile(r"\d{1,6}")
EIGHT_DIGIT = re.compile(r"^\d{8}$")
HOUR_MINUTE_REGEX = re.compile(r"^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")


def no_space_parser_eligibile(datestring):
    src = NSP_COMPATIBLE.search(datestring)
    return not src or src.group() == ":"


def get_unresolved_attrs(parser_object):
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


def resolve_date_order(order, lst=None):
    chart_list = {
        "DMY": ["day", "month", "year"],
        "DYM": ["day", "year", "month"],
        "MDY": ["month", "day", "year"],
        "MYD": ["month", "year", "day"],
        "YDM": ["year", "day", "month"],
        "YMD": ["year", "month", "day"],
    }

    return chart_list[order] if lst else date_order_chart[order]


def _parse_absolute(datestring, settings, tz=None, date_order=None):
    return _parser.parse(datestring, settings, tz, date_order=date_order)


def _parse_nospaces(datestring, settings, tz=None, date_order=None):
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

    def __call__(self, timestring):
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

    def __init__(self, *args, **kwargs):
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
    def _get_period(cls, format_string):
        for pname, pdrv in sorted(cls.period.items(), key=lambda x: x[0]):
            for drv in pdrv:
                if drv in format_string:
                    return pname
        return "year"

    @classmethod
    def _find_best_matching_date(cls, datestring):
        for fmt in cls._preferred_formats_ordered_8_digit:
            with contextlib.suppress(Exception):
                dt = strptime(datestring, fmt), cls._get_period(fmt)
                if len(str(dt[0].year)) == 4:
                    return dt
        return None

    @classmethod
    def parse(cls, datestring, settings, date_order=None):
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
        ambiguous_date = None
        for token, _ in tokens.tokenize():
            for fmt in nsp.date_formats[order]:
                with contextlib.suppress(Exception):
                    dt = strptime(token, fmt), cls._get_period(fmt)
                    if len(str(dt[0].year)) < 4:
                        ambiguous_date = dt
                        continue

                    missing = _get_missing_parts(fmt)
                    _check_strict_parsing(missing, settings)
                    return dt
        if ambiguous_date:
            return ambiguous_date
        raise ValueError(f"Unable to parse date from: {datestring}")


def _get_missing_error(missing):
    return "Fields missing from the date string: {}".format(", ".join(missing))


def _check_strict_parsing(missing, settings):
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

    def __init__(self, tokens, settings, date_order=None):  # noqa: PLR0912, PLR0915
        self.settings = settings
        self._date_order = date_order or settings.DATE_ORDER
        self.tokens = [(t[0].strip(), t[1]) for t in list(tokens)]
        self.filtered_tokens = [
            (t[0], t[1], i) for i, t in enumerate(self.tokens) if t[1] <= 1
        ]

        self.unset_tokens = []

        self.day = None
        self.month = None
        self.year = None
        self.time = None

        self.auto_order = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None

        self.ordered_num_directives = {
            k: self.num_directives[k]
            for k in resolve_date_order(self._date_order, lst=True)
        }

        skip_index = []
        skip_component = None
        skip_tokens = ["t", "year", "hour", "minute"]

        for index, token_type_original_index in enumerate(self.filtered_tokens):
            if index in skip_index:
                continue

            token, token_type, original_index = token_type_original_index

            if token in skip_tokens:
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
                    microsecond = MICROSECOND.search(
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
                    meridian = MERIDIAN.search(
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
                    self.time = lambda: time_parser(self._token_time)
                    continue

            results = self._parse(token_type, token, skip_component=skip_component)
            for res in results:
                if len(token) == 4 and res[0] == "year":
                    skip_component = "year"
                setattr(self, *res)

        known, unknown = get_unresolved_attrs(self)
        params = {}
        for attr in known:
            params.update({attr: getattr(self, attr)})
        for attr in unknown:
            for token, token_type, _ in self.unset_tokens:
                if token_type == 0:
                    params.update({attr: int(token)})
                    setattr(self, f"_token_{attr}", token)
                    setattr(self, attr, int(token))

    def _get_period(self):
        if self.settings.RETURN_TIME_AS_PERIOD and getattr(self, "time", None):
            return "time"

        for period in ["time", "day"]:
            if getattr(self, period, None):
                return "day"

        for period in ["month", "year"]:
            if getattr(self, period, None):
                return period

        return "day"

    def _get_datetime_obj(self, **params):
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

    def _get_correct_leap_year(self, prefer_dates_from, current_year):
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

    def _set_relative_base(self):
        self.now = self.settings.RELATIVE_BASE
        if not self.now:
            self.now = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    def _get_datetime_obj_params(self):
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

    def _get_date_obj(self, token, directive):
        return strptime(token, directive)

    def _results(self):
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

    def _correct_for_time_frame(self, dateobj, tz):  # noqa: PLR0912, PLR0915
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        token_weekday, _ = getattr(self, "_token_weekday", (None, None))

        if token_weekday and not (
            self._token_year or self._token_month or self._token_day
        ):
            day_index = calendar.weekday(dateobj.year, dateobj.month, dateobj.day)
            day = token_weekday[:3].lower()
            steps = 0
            if "future" in self.settings.PREFER_DATES_FROM:
                if days[day_index] == day:
                    steps = 7
                else:
                    while days[day_index] != day:
                        day_index = (day_index + 1) % 7
                        steps += 1
                delta = timedelta(days=steps)
            else:
                if days[day_index] == day:
                    steps = 7 if self.settings.PREFER_DATES_FROM == "past" else 0
                else:
                    while days[day_index] != day:
                        day_index -= 1
                        steps += 1
                delta = timedelta(days=-steps)

            dateobj = dateobj + delta

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
                if self.now < dateobj:
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
            # Convert dateobj to utc time to compare with self.now
            try:
                tz = tz or get_timezone_from_tz_string(self.settings.TIMEZONE)
                tz_offset = tz.utcoffset(dateobj)
            except (pytz.UnknownTimeZoneError, pytz.NonExistentTimeError):
                tz_offset = timedelta(hours=0)

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

    def _correct_for_day(self, dateobj):
        if (
            getattr(self, "_token_day", None)
            or getattr(self, "_token_weekday", None)
            or getattr(self, "_token_time", None)
        ):
            return dateobj

        return set_correct_day_from_settings(
            dateobj, self.settings, current_day=self.now.day
        )

    def _correct_for_month(self, dateobj):
        if getattr(self, "_token_month", None):
            return dateobj

        return set_correct_month_from_settings(
            dateobj, self.settings, current_month=self.now.month
        )

    @classmethod
    def parse(cls, datestring, settings, tz=None, date_order=None):
        tokens = tokenizer(datestring)
        po = cls(tokens.tokenize(), settings, date_order=date_order)
        dateobj = po._results()

        # correction for past, future if applicable
        dateobj = po._correct_for_time_frame(dateobj, tz)

        # correction for preference of month: beginning, current, end
        # must happen before day so that day is derived from the correct month
        dateobj = po._correct_for_month(dateobj)

        # correction for preference of day: beginning, current, end
        dateobj = po._correct_for_day(dateobj)

        period = po._get_period()

        return dateobj, period

    def _parse(self, token_type, token, skip_component=None):
        def set_and_return(
            token, token_type, component, dateobj, skip_date_order=False
        ):
            if not skip_date_order:
                self.auto_order.append(component)
            setattr(self, f"_token_{component}", (token, token_type))
            return [(component, getattr(dateobj, component))]

        def parse_number(token, skip_component=None):
            token_type = 0

            num_directives = self.ordered_num_directives
            if (
                skip_component == "year"
                and self.day is None
                and self.month is None
                and "DATE_ORDER" not in self.settings._mod_settings
            ):
                # The date string starts with a four-digit year (e.g. an
                # ISO 8601 date like "2017-06-22"), so the remaining numeric
                # components are expected in month-day order, regardless of
                # the locale date order, unless the caller explicitly set
                # DATE_ORDER (#360).
                num_directives = {
                    k: self.num_directives[k] for k in ("month", "day", "year")
                }

            def try_directives(skip_directive=None):
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
                raise ValueError(f"Unable to parse: {token}")

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

        def parse_alpha(token, skip_component=None):
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
                        if component == "month":
                            index = self.auto_order.index("month")
                            self.auto_order[index] = "day"
                            self._token_day = self._token_month
                            self._token_month = token, token_type
                            return [
                                (component, getattr(do, component)),
                                ("day", prev_value),
                            ]
            raise ValueError(f"Unable to parse: {token}")

        handlers = {0: parse_number, 1: parse_alpha}
        return handlers[token_type](token, skip_component)


class tokenizer:
    digits = "0123456789:"
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def _isletter(self, tkn):
        return tkn in self.letters

    def _isdigit(self, tkn):
        return tkn in self.digits

    def __init__(self, ds):
        self.instream = StringIO(ds)

    def _switch(self, chara, charb):
        if self._isdigit(chara):
            return 0, not self._isdigit(charb)

        if self._isletter(chara):
            return 1, not self._isletter(charb)

        return 2, self._isdigit(charb) or self._isletter(charb)

    def tokenize(self):
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
