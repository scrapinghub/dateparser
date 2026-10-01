import collections
import functools
import itertools
import threading
from collections.abc import Callable, Iterable, Iterator
from collections.abc import Set as AbstractSet
from datetime import date, datetime, timedelta, tzinfo
from itertools import count
from typing import TYPE_CHECKING, Any, ClassVar, TypeGuard, TypeVar

import regex as re
from dateutil.relativedelta import relativedelta

from dateparser._parts_of_day import PartOfDay, _replace_part_of_day
from dateparser.conf import Settings, apply_settings, check_settings
from dateparser.custom_language_detection.language_mapping import map_languages
from dateparser.date_parser import date_parser
from dateparser.freshness_date_parser import freshness_date_parser
from dateparser.languages.loader import LocaleDataLoader
from dateparser.parser import _parse_absolute, _parse_nospaces
from dateparser.timezone_parser import pop_tz_offset_from_string
from dateparser.utils import (
    _get_localzone,
    _get_missing_parts,
    _get_parts,
    _now,
    apply_timezone_from_settings,
    get_next_leap_year,
    get_previous_leap_year,
    get_timezone_from_tz_string,
    set_correct_day_from_settings,
    set_correct_month_from_settings,
)
from dateparser.utils.strptime import strptime as patched_strptime

if TYPE_CHECKING:
    from dateparser.languages.locale import Locale

_D = TypeVar("_D", bound=date)

APOSTROPHE_LOOK_ALIKE_CHARS = [
    "\N{RIGHT SINGLE QUOTATION MARK}",  # '\u2019'
    "\N{MODIFIER LETTER APOSTROPHE}",  # '\u02bc'
    "\N{MODIFIER LETTER TURNED COMMA}",  # '\u02bb'
    "\N{ARMENIAN APOSTROPHE}",  # '\u055a'
    "\N{LATIN SMALL LETTER SALTILLO}",  # '\ua78c'
    "\N{PRIME}",  # '\u2032'
    "\N{REVERSED PRIME}",  # '\u2035'
    "\N{MODIFIER LETTER PRIME}",  # '\u02b9'
    "\N{FULLWIDTH APOSTROPHE}",  # '\uff07'
]

# Unicode Dash Characters, per the "Dash" property table in the Unicode Standard
# (https://www.unicode.org/versions/latest/core-spec/chapter-6/#G9697), excluding
# U+002D HYPHEN-MINUS itself. Written as \u/\U escapes rather than \N{...} names
# since some of these (e.g. Garay Hyphen, Yezidi Hyphenation Mark) are recent
# Unicode additions not present in the unicodedata name tables of older Pythons.
DASH_LOOK_ALIKE_CHARS = [
    "\u058a",  # ARMENIAN HYPHEN
    "\u05be",  # HEBREW PUNCTUATION MAQAF
    "\u1400",  # CANADIAN SYLLABICS HYPHEN
    "\u1806",  # MONGOLIAN TODO SOFT HYPHEN
    "\u2010",  # HYPHEN
    "\u2011",  # NON-BREAKING HYPHEN
    "\u2012",  # FIGURE DASH
    "\u2013",  # EN DASH
    "\u2014",  # EM DASH
    "\u2015",  # HORIZONTAL BAR
    "\u2053",  # SWUNG DASH
    "\u207b",  # SUPERSCRIPT MINUS
    "\u208b",  # SUBSCRIPT MINUS
    "\u2212",  # MINUS SIGN
    "\u2e17",  # DOUBLE OBLIQUE HYPHEN
    "\u2e1a",  # HYPHEN WITH DIAERESIS
    "\u2e3a",  # TWO-EM DASH
    "\u2e3b",  # THREE-EM DASH
    "\u2e40",  # DOUBLE HYPHEN
    "\u2e5d",  # OBLIQUE HYPHEN
    "\u301c",  # WAVE DASH
    "\u3030",  # WAVY DASH
    "\u30a0",  # KATAKANA-HIRAGANA DOUBLE HYPHEN
    "\ufe31",  # PRESENTATION FORM FOR VERTICAL EM DASH
    "\ufe32",  # PRESENTATION FORM FOR VERTICAL EN DASH
    "\ufe58",  # SMALL EM DASH
    "\ufe63",  # SMALL HYPHEN-MINUS
    "\uff0d",  # FULLWIDTH HYPHEN-MINUS
    "\U00010d6e",  # GARAY HYPHEN
    "\U00010ead",  # YEZIDI HYPHENATION MARK
]

RE_NBSP = re.compile("\xa0", flags=re.UNICODE)
RE_SPACES = re.compile(r"\s+")
RE_TRIM_SPACES = re.compile(r"^\s+(\S.*?)\s+$")
RE_TRIM_COLONS = re.compile(r"(\S.*?):*$")

RE_SANITIZE_SKIP = re.compile(
    r"\t|\n|\r|\u00bb|,\s\u0432\b|\u200e|\xb7|\u200f|\u064e|\u064f", flags=re.M
)
RE_SANITIZE_RUSSIAN = re.compile(r"([\W\d])\u0433\.", flags=re.I | re.U)
RE_SANITIZE_CROATIAN = re.compile(
    r"(\d+)\.\s?(\d+)\.\s?(\d+)\.( u)?", flags=re.I | re.U
)
RE_SANITIZE_PERIOD = re.compile(r"(?<=[^0-9\s])\.", flags=re.U)
RE_SANITIZE_DECIMAL_COMMA = re.compile(r"(?<=\d:\d{2}:\d{2}),(?=\d{3})")
RE_SANITIZE_ON = re.compile(r"^.*?on:\s+(.*)")
RE_SANITIZE_APOSTROPHE = re.compile("|".join(APOSTROPHE_LOOK_ALIKE_CHARS))
RE_SANITIZE_DASH = re.compile("|".join(DASH_LOOK_ALIKE_CHARS))
# Uppercase Roman numerals from 1000 on, allowing the additive IIII, XXXX and
# CCCC of old prints.
_RE_ROMAN_YEAR = re.compile(
    r"\bM{1,3}(?:CM|CD|D?C{0,4})(?:XC|XL|L?X{0,4})(?:IX|IV|V?I{0,4})\b"
)
_ROMAN_NUMERAL_VALUES = {
    "M": 1000,
    "D": 500,
    "C": 100,
    "L": 50,
    "X": 10,
    "V": 5,
    "I": 1,
}

RE_SEARCH_TIMESTAMP = re.compile(r"^(\d{10})(\d{3})?(\d{3})?(?![^.])")
RE_SEARCH_NEGATIVE_TIMESTAMP = re.compile(r"^([-]\d{10})(\d{3})?(\d{3})?(?![^.])")


def sanitize_spaces(date_string: str) -> str:
    date_string = RE_NBSP.sub(" ", date_string)
    date_string = RE_SPACES.sub(" ", date_string)
    return RE_TRIM_SPACES.sub(r"\1", date_string)


def date_range(begin: _D, end: _D, **kwargs: Any) -> Iterator[_D]:
    dateutil_error_prone_args = [
        "year",
        "month",
        "week",
        "day",
        "hour",
        "minute",
        "second",
    ]
    for arg in dateutil_error_prone_args:
        if arg in kwargs:
            raise ValueError(f"Invalid argument: {arg}")

    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

    date = begin
    while date < end:
        yield date
        date += step

    # handles edge-case when iterating months and last interval is < 30 days
    if kwargs.get("months", 0) > 0 and (date.year, date.month) == (end.year, end.month):
        yield end


def get_intersecting_periods(low: _D, high: _D, period: str = "day") -> Iterator[_D]:
    if period not in [
        "year",
        "month",
        "week",
        "day",
        "hour",
        "minute",
        "second",
        "microsecond",
    ]:
        raise ValueError(f"Invalid period: {period}")

    if high <= low:
        return

    step_kwargs: dict[str, Any] = {period + "s": 1}
    step = relativedelta(**step_kwargs)

    current_period_start = low
    if isinstance(current_period_start, datetime):
        reset_arguments: dict[str, Any] = {}
        for test_period in ["microsecond", "second", "minute", "hour"]:
            if test_period == period:
                break
            else:
                reset_arguments[test_period] = 0
        current_period_start = current_period_start.replace(**reset_arguments)

    if period == "week":
        current_period_start = current_period_start - timedelta(
            days=current_period_start.weekday()
        )
    elif period == "month":
        current_period_start = current_period_start.replace(day=1)
    elif period == "year":
        current_period_start = current_period_start.replace(month=1, day=1)

    while current_period_start < high:
        yield current_period_start
        current_period_start += step


def sanitize_date(date_string: str) -> str:
    date_string = RE_SANITIZE_SKIP.sub(" ", date_string)
    date_string = RE_SANITIZE_RUSSIAN.sub(
        r"\1 ", date_string
    )  # remove 'г.' (Russian for year) but not in words
    date_string = RE_SANITIZE_CROATIAN.sub(
        r"\1.\2.\3 ", date_string
    )  # extra '.' and 'u' interferes with parsing relative fractional dates
    date_string = sanitize_spaces(date_string)
    date_string = RE_SANITIZE_PERIOD.sub("", date_string)
    date_string = _RE_ROMAN_YEAR.sub(_roman_year_to_digits, date_string)
    date_string = RE_SANITIZE_DECIMAL_COMMA.sub(".", date_string)
    date_string = RE_SANITIZE_ON.sub(r"\1", date_string)
    date_string = RE_TRIM_COLONS.sub(r"\1", date_string)
    date_string = RE_SANITIZE_APOSTROPHE.sub("'", date_string)
    date_string = RE_SANITIZE_DASH.sub("-", date_string)
    return date_string.strip()


def _roman_year_to_digits(match: re.Match[str]) -> str:
    numeral = match[0]
    # Too ambiguous with abbreviations like MD or MC.
    if len(numeral) < 3:
        return numeral
    values = [_ROMAN_NUMERAL_VALUES[char] for char in numeral]
    return str(
        sum(
            -value if value < next_value else value
            for value, next_value in zip(values, [*values[1:], 0], strict=True)
        )
    )


def get_date_from_timestamp(
    date_string: str, settings: Settings | None, negative: bool = False
) -> datetime | None:
    if negative:
        match = RE_SEARCH_NEGATIVE_TIMESTAMP.search(date_string)
    else:
        match = RE_SEARCH_TIMESTAMP.search(date_string)

    if match:
        if (
            settings is None
            or settings.TIMEZONE is None
            or "local" in settings.TIMEZONE.lower()
        ):
            # If the timezone in settings is unset, or it's 'local', use the
            # local timezone
            timezone: tzinfo = _get_localzone()
        else:
            # Otherwise, use the timezone given in settings
            timezone = get_timezone_from_tz_string(settings.TIMEZONE)

        seconds = int(match.group(1))
        millis = int(match.group(2) or 0)
        micros = int(match.group(3) or 0)
        date_obj = datetime.fromtimestamp(seconds, timezone).replace(
            microsecond=millis * 1000 + micros, tzinfo=None
        )
        return apply_timezone_from_settings(date_obj, settings)
    return None


def _apply_century_preference(
    date_obj: datetime, now: datetime, prefer_from: str
) -> datetime:
    """Shift *date_obj* by ±100 years to satisfy PREFER_DATES_FROM.

    *now* is normalised to naive so a tz-aware RELATIVE_BASE does not raise
    TypeError.  When the shifted year falls on Feb 29 in a non-leap year, the
    nearest valid leap year in the preferred direction is used — matching the
    behaviour of the NLP path in ``parser.py``.

    Returns the adjusted datetime, or the original when no shift is needed.
    """
    now_naive = now.replace(tzinfo=None) if now.tzinfo is not None else now

    if now_naive < date_obj and prefer_from == "past":
        target_year = date_obj.year - 100
    elif now_naive >= date_obj and prefer_from == "future":
        target_year = date_obj.year + 100
    else:
        return date_obj

    try:
        return date_obj.replace(year=target_year)
    except ValueError:
        # Feb 29 shifted into a non-leap year — find the nearest valid one
        target_year = (
            get_next_leap_year(target_year)
            if prefer_from == "future"
            else get_previous_leap_year(target_year)
        )
        return date_obj.replace(year=target_year)


def parse_with_formats(
    date_string: str, date_formats: Iterable[str], settings: Settings
) -> "DateData":
    """Parse with formats and return a dictionary with 'period' and 'obj_date'.

    :returns: :class:`datetime.datetime`, dict or None

    """
    period = "day"
    for date_format in date_formats:
        try:
            date_obj = patched_strptime(date_string, date_format)
        except ValueError:
            continue
        else:
            _missing = _get_missing_parts(date_format)
            missing_month = "month" in _missing
            missing_day = "day" in _missing
            if missing_month and missing_day:
                period = "year"
                date_obj = set_correct_month_from_settings(date_obj, settings)
                date_obj = set_correct_day_from_settings(date_obj, settings)

            elif missing_month:
                period = "year"
                date_obj = set_correct_month_from_settings(date_obj, settings)

            elif missing_day:
                period = "month"
                date_obj = set_correct_day_from_settings(date_obj, settings)

            now = settings.RELATIVE_BASE or _now(settings)
            if "year" in _missing:
                date_obj = date_obj.replace(year=now.year)
            elif "%y" in date_format and "%Y" not in date_format:
                date_obj = _apply_century_preference(
                    date_obj, now, settings.PREFER_DATES_FROM
                )

            date_obj = apply_timezone_from_settings(date_obj, settings)

            return DateData(
                date_obj=date_obj, period=period, parts=_get_parts(date_format)
            )
    return DateData(date_obj=None, period=period)


_MONTHS = (
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
)
_WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


@functools.cache
def _get_name_translations(
    locale: "Locale", month_form: str | None, weekday_form: str | None
) -> tuple[re.Pattern[str], dict[str, list[str]]] | None:
    """Return a pattern matching the month and weekday names of *locale*, and
    a mapping of each lowercase name to the English names it can stand for, or
    ``None`` if there are no such names.

    *month_form* and *weekday_form* are ``"full"``, ``"abbr"`` or ``None``,
    the English form to translate each kind of name into, or ``None`` to leave
    that kind of name untranslated.
    """
    translations: dict[str, list[str]] = collections.defaultdict(list)
    for words, form in ((_MONTHS, month_form), (_WEEKDAYS, weekday_form)):
        if form is None:
            continue
        for word in words:
            english = word if form == "full" else word[:3]
            for name in map(str.lower, locale.info.get(word, ())):
                if english not in translations[name]:
                    translations[name].append(english)
    if not translations:
        return None
    names = sorted(translations, key=len, reverse=True)
    pattern = re.compile(
        r"(?<!\w)(?:{})(?!\w)".format("|".join(map(re.escape, names))),
        flags=re.IGNORECASE,
    )
    return pattern, dict(translations)


def _translate_names(
    date_string: str, date_format: str, locale: "Locale"
) -> Iterator[str]:
    """Yield the variants of *date_string* that result from replacing the
    month and weekday names of *locale* with the English names that the
    directives of *date_format* expect."""
    month_form = (
        "full" if "%B" in date_format else "abbr" if "%b" in date_format else None
    )
    weekday_form = (
        "full" if "%A" in date_format else "abbr" if "%a" in date_format else None
    )
    name_translations = _get_name_translations(locale, month_form, weekday_form)
    if name_translations is None:
        return
    pattern, translations = name_translations
    matches = pattern.findall(date_string)
    if not matches:
        return
    parts = pattern.split(date_string)
    # A name can stand for several English names, e.g. "mar" is both "martes"
    # and "marzo" in Spanish, so every combination is yielded.
    for combination in itertools.product(
        *(translations[match.lower()] for match in matches)
    ):
        yield "".join(
            part + name for part, name in zip(parts, (*combination, ""), strict=True)
        )


class _DateLocaleParser:
    _parsers: ClassVar[dict[str, str]] = {
        "timestamp": "_try_timestamp",
        "negative-timestamp": "_try_negative_timestamp",
        "relative-time": "_try_freshness_parser",
        "custom-formats": "_try_given_formats",
        "absolute-time": "_try_absolute_parser",
        "no-spaces-time": "_try_nospaces_parser",
    }

    def __init__(
        self,
        locale: "Locale",
        date_string: str,
        date_formats: Iterable[str] | None,
        settings: Settings | None = None,
        ignore_surrounding_text: bool = False,
        alternatives: bool = False,
    ) -> None:
        assert settings is not None
        self._settings = settings
        if not (
            date_formats is None or isinstance(date_formats, (list, tuple, AbstractSet))
        ):
            raise TypeError("Date formats should be list, tuple or set of strings")

        self.locale = locale
        self.date_string = date_string
        self.date_formats = date_formats
        self._ignore_surrounding_text = ignore_surrounding_text
        self._alternatives = alternatives
        self._alternative = 0
        self._translated_date: str | None = None
        self._translated_date_with_formatting: str | None = None
        self._part_of_day: PartOfDay | None = None
        self._part_of_day_sets_time = False

    @classmethod
    def parse(
        cls,
        locale: "Locale",
        date_string: str,
        date_formats: Iterable[str] | None = None,
        settings: Settings | None = None,
        ignore_surrounding_text: bool = False,
        alternatives: bool = False,
    ) -> "DateData | None":
        instance = cls(
            locale,
            date_string,
            date_formats,
            settings,
            ignore_surrounding_text,
            alternatives,
        )
        return instance._parse()

    def _parse(self) -> "DateData | None":
        if not self._alternatives:
            return self._parse_translation()
        for self._alternative in count(1):
            self._set_translated_date()
            if self._translated_date is None:
                return None
            self._translated_date_with_formatting = None
            date_data = self._parse_translation()
            if date_data:
                return date_data
        return None

    def _parse_translation(self) -> "DateData | None":
        for parser_name in self._settings.PARSERS:
            date_data = getattr(self, self._parsers[parser_name])()
            if self._is_valid_date_data(date_data):
                if self._part_of_day:
                    date_data.part_of_day = self._part_of_day
                    if (
                        self._part_of_day_sets_time
                        and self._settings.RETURN_TIME_AS_PERIOD
                    ):
                        date_data.period = "part_of_day"
                return date_data
        return None

    def _try_timestamp_parser(self, negative: bool = False) -> "DateData":
        return DateData(
            date_obj=get_date_from_timestamp(
                self.date_string, self._settings, negative=negative
            ),
            period="time" if self._settings.RETURN_TIME_AS_PERIOD else "day",
            parts=("year", "month", "day", "time"),
        )

    def _try_timestamp(self) -> "DateData":
        return self._try_timestamp_parser()

    def _try_negative_timestamp(self) -> "DateData":
        return self._try_timestamp_parser(negative=True)

    def _try_freshness_parser(self) -> "DateData | None":
        try:
            return freshness_date_parser.get_date_data(
                self._get_translated_date(), self._settings
            )
        except (OverflowError, ValueError):
            return None

    def _try_absolute_parser(self) -> "DateData | None":
        return self._try_parser(parse_method=_parse_absolute)

    def _try_nospaces_parser(self) -> "DateData | None":
        return self._try_parser(parse_method=_parse_nospaces)

    def _try_parser(
        self, parse_method: Callable[..., tuple[datetime, str | None, tuple[str, ...]]]
    ) -> "DateData | None":
        original_order = self._settings.DATE_ORDER

        # Use locale date order unless DATE_ORDER was explicitly set by the caller.
        if (
            self._settings.PREFER_LOCALE_DATE_ORDER
            and "DATE_ORDER" not in self._settings._mod_settings
        ):
            first_order = self.locale.info.get("date_order", original_order)
        else:
            first_order = original_order

        candidates = [first_order]

        # If the caller requires a year (and not a day) and did not set DATE_ORDER,
        # retry once or twice with year-biased orders to resolve month-number ambiguity.
        require_parts = set(getattr(self._settings, "REQUIRE_PARTS", None) or [])
        if (
            "DATE_ORDER" not in self._settings._mod_settings
            and "year" in require_parts
            and "day" not in require_parts
        ):
            for order in ("MYD", "YMD"):
                if order not in candidates:
                    candidates.append(order)

        translated = self._get_translated_date()

        for order in candidates:
            try:
                date_obj, period, parts = date_parser.parse(
                    translated,
                    parse_method=parse_method,
                    settings=self._settings,
                    date_order=order,
                )
                return DateData(date_obj=date_obj, period=period, parts=parts)
            except ValueError:
                continue
        return None

    def _try_given_formats(self) -> "DateData | None":
        if not self.date_formats:
            return None

        return parse_with_formats(
            self._get_translated_date_with_formatting(),
            self.date_formats,
            settings=self._settings,
        )

    def _translate(self, keep_formatting: bool) -> str | None:
        return self.locale._translate(
            self.date_string,
            keep_formatting=keep_formatting,
            settings=self._settings,
            ignore_surrounding_text=self._ignore_surrounding_text,
            alternative=self._alternative,
        )

    def _set_translated_date(self) -> None:
        translated = self._translate(keep_formatting=False)
        if translated is None:
            self._translated_date = None
            return
        (
            self._translated_date,
            self._part_of_day,
            self._part_of_day_sets_time,
        ) = _replace_part_of_day(translated, self._settings.PARTS_OF_DAY)

    def _get_translated_date(self) -> str:
        if self._translated_date is None:
            self._set_translated_date()
        assert self._translated_date is not None
        return self._translated_date

    def _get_translated_date_with_formatting(self) -> str:
        if self._translated_date_with_formatting is None:
            self._translated_date_with_formatting = self._translate(
                keep_formatting=True
            )
        assert self._translated_date_with_formatting is not None
        return self._translated_date_with_formatting

    def _is_valid_date_data(self, date_data: object) -> TypeGuard["DateData"]:
        if not isinstance(date_data, DateData):
            return False
        if not date_data["date_obj"] or not date_data["period"]:
            return False
        if date_data["date_obj"] and not isinstance(date_data["date_obj"], datetime):
            return False
        return date_data["period"] in ("time", "day", "week", "month", "year")


class DateData:
    """
    Class that represents the parsed data with useful information.
    It can be accessed with square brackets like a dict object.
    """

    part_of_day: PartOfDay | None = None
    """:class:`~dateparser.PartOfDay` that the date string refers to, e.g.
    :attr:`~dateparser.PartOfDay.NIGHT` for ``"tonight"``, or ``None``.

    .. versionadded:: VERSION

    Its time comes from the ``PARTS_OF_DAY`` :ref:`setting <settings>`, unless
    the date string also has a time, e.g. ``"tonight at 11pm"``. If it does
    not, and the ``RETURN_TIME_AS_PERIOD`` setting is enabled, ``period`` is
    ``"part_of_day"``.
    """

    def __init__(
        self,
        *,
        date_obj: datetime | None = None,
        period: str | None = None,
        locale: str | None = None,
        parts: tuple[str, ...] = (),
    ) -> None:
        self.date_obj = date_obj
        self.period = period
        self.locale = locale
        self.parts = parts
        """Parts of :attr:`date_obj` determined by the parsed string, as a
        tuple with some or all of ``"year"``, ``"month"``, ``"day"`` and
        ``"time"``, in that order. The remaining parts come from
        :ref:`settings`, e.g. ``RELATIVE_BASE`` or ``PREFER_DAY_OF_MONTH``."""

    def __getitem__(self, k: str) -> Any:
        if not hasattr(self, k):
            raise KeyError(k)
        return getattr(self, k)

    def __setitem__(self, k: str, v: Any) -> None:
        if not hasattr(self, k):
            raise KeyError(k)
        setattr(self, k, v)

    def __repr__(self) -> str:
        properties_text = ", ".join(
            f"{prop}={val!r}" for prop, val in self.__dict__.items()
        )

        return f"{self.__class__.__name__}({properties_text})"


class DateDataParser:
    """
    Class which handles language detection, translation and subsequent generic parsing of
    string representing date and/or time.

    :param languages:
        A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type languages: list

    :param locales:
        A list of locale codes, e.g. ['fr-PF', 'qu-EC', 'af-NA'].
        The parser uses only these locales to translate date string.
    :type locales: list

    :param region:
        A region code, e.g. 'IN', '001', 'NE'.
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type region: str

    :param try_previous_locales:
        If True, locales previously used to translate date are tried first.
    :type try_previous_locales: bool

    :param use_given_order:
        If True, locales are tried for translation of date string
        in the order in which they are given. This is equivalent to the
        ``USE_GIVEN_LANGUAGE_ORDER`` setting; the given order is preserved if
        either is enabled.
    :type use_given_order: bool

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :param detect_languages_function:
        A function for language detection that takes as input a `text` and a `confidence_threshold`,
        and returns a list of detected language codes.
        Note: this function is only used if ``languages`` and ``locales`` are not provided.
    :type detect_languages_function: function

    :return: A parser instance

    :raises:
         ``ValueError``: Unknown Language, ``TypeError``: Languages argument must be a list,
         ``SettingValidationError``: A provided setting is not valid.
    """

    locale_loader: LocaleDataLoader | None = None

    @apply_settings
    def __init__(
        self,
        languages: Iterable[str] | None = None,
        locales: Iterable[str] | None = None,
        region: str | None = None,
        try_previous_locales: bool = False,
        use_given_order: bool = False,
        settings: Settings | dict[str, Any] | None = None,
        detect_languages_function: Callable[..., list[str]] | None = None,
    ) -> None:
        assert isinstance(settings, Settings)
        if languages is not None and not isinstance(
            languages, (list, tuple, AbstractSet)
        ):
            raise TypeError(
                f"languages argument must be a list ({type(languages)!r} given)"
            )

        if locales is not None and not isinstance(locales, (list, tuple, AbstractSet)):
            raise TypeError(
                f"locales argument must be a list ({type(locales)!r} given)"
            )

        if region is not None and not isinstance(region, str):
            raise TypeError(f"region argument must be str ({type(region)!r} given)")

        if not isinstance(try_previous_locales, bool):
            raise TypeError(
                f"try_previous_locales argument must be a boolean ({type(try_previous_locales)!r} given)"
            )

        if not isinstance(use_given_order, bool):
            raise TypeError(
                f"use_given_order argument must be a boolean ({type(use_given_order)!r} given)"
            )

        if not locales and not languages and use_given_order:
            raise ValueError(
                "locales or languages must be given if use_given_order is True"
            )

        check_settings(settings)

        self._settings = settings
        self.try_previous_locales = try_previous_locales
        self.use_given_order = use_given_order
        self.languages = list(languages) if languages else None
        self.locales = locales
        self.region = region
        self.detect_languages_function = detect_languages_function
        self.previous_locales: collections.OrderedDict[Locale, None] = (
            collections.OrderedDict()
        )
        # Guards the per-instance state mutated when a parser is shared by
        # multiple threads (previous_locales and the lazily detected languages).
        self._lock = threading.RLock()

    def get_date_data(
        self, date_string: str, date_formats: Iterable[str] | None = None
    ) -> DateData:
        """
        Parse string representing date and/or time in recognizable localized formats.
        Supports parsing multiple languages and timezones.

        :param date_string:
            A string representing date and/or time in a recognizably valid format.
        :type date_string: str
        :param date_formats:
            A list of format strings using directives as given
            `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
            The parser applies formats one by one, taking into account the detected languages.
        :type date_formats: list

        :return: a ``DateData`` object.

        :raises: ValueError - Unknown Language

        .. note:: *Period* values can be a 'day' (default), 'week', 'month', 'year', 'time',
            'part_of_day'.

        *Period* represents the granularity of date parsed from the given string.

        In the example below, since no day information is present, the day is assumed to be current
        day ``16`` from *current date* (which is June 16, 2015, at the moment of writing this).
        Hence, the level of precision is ``month``:

            >>> DateDataParser().get_date_data('March 2015')
            DateData(date_obj=datetime.datetime(2015, 3, 16, 0, 0), period='month', locale='en',
            parts=('year', 'month'))

        Similarly, for date strings with no day and month information present, level of precision
        is ``year`` and day ``16`` and month ``6`` are from *current_date*.

            >>> DateDataParser().get_date_data('2014')
            DateData(date_obj=datetime.datetime(2014, 6, 16, 0, 0), period='year', locale='en',
            parts=('year',))

        *Parts* lists the parts of the date that the given string determines,
        including those that *period* cannot tell apart, like a missing year:

            >>> DateDataParser().get_date_data('16 March')
            DateData(date_obj=datetime.datetime(2015, 3, 16, 0, 0), period='day', locale='en',
            parts=('month', 'day'))

        Dates with time zone indications or UTC offsets are returned in UTC time unless
        specified using `Settings <https://dateparser.readthedocs.io/en/latest/settings.html#settings>`__.

            >>> DateDataParser().get_date_data('23 March 2000, 1:21 PM CET')
            DateData(date_obj=datetime.datetime(2000, 3, 23, 13, 21, tzinfo=<StaticTzInfo 'CET'>),
            period='day', locale='en', parts=('year', 'month', 'day', 'time'))

        """
        if not isinstance(date_string, str):
            raise TypeError("Input type must be str")

        res = parse_with_formats(date_string, date_formats or [], self._settings)
        if res["date_obj"]:
            return res
        if date_formats:
            localized_res = self._parse_with_localized_formats(
                date_string, date_formats
            )
            if localized_res:
                return localized_res

        date_string = sanitize_date(date_string)

        parsed_date = self._parse_using_applicable_locales(date_string, date_formats)
        if not parsed_date and self._settings.IGNORE_SURROUNDING_TEXT:
            # The whole string could not be parsed as a date. Retry, ignoring
            # unrecognized words at the edges of the string, so that a date
            # wrapped in harmless extra text is still parsed (issue #518),
            # e.g. "Actualisé le 17 avril 2019". Strings that can be parsed as
            # a whole never reach this fallback, so they are unaffected.
            parsed_date = self._parse_using_applicable_locales(
                date_string, date_formats, ignore_surrounding_text=True
            )
        return parsed_date or DateData(date_obj=None, period="day", locale=None)

    def _parse_with_localized_formats(
        self, date_string: str, date_formats: Iterable[str]
    ) -> DateData | None:
        for locale in self._get_locale_loader().get_locales(
            languages=self.languages,
            locales=self.locales,
            region=self.region,
            use_given_order=self.use_given_order
            or self._settings.USE_GIVEN_LANGUAGE_ORDER,
        ):
            for date_format in date_formats:
                for translated in _translate_names(date_string, date_format, locale):
                    res = parse_with_formats(translated, [date_format], self._settings)
                    if res["date_obj"]:
                        res["locale"] = locale.shortname
                        return res
        return None

    def _parse_using_applicable_locales(
        self,
        date_string: str,
        date_formats: Iterable[str] | None,
        ignore_surrounding_text: bool = False,
    ) -> DateData | None:
        locales = []
        for locale in self._get_applicable_locales(
            date_string, ignore_surrounding_text=ignore_surrounding_text
        ):
            locales.append(locale)
            parsed_date = self._parse_using_locale(
                locale, date_string, date_formats, ignore_surrounding_text
            )
            if parsed_date:
                return parsed_date
        # Words with several meanings (e.g. Spanish "mar", Tuesday or March)
        # get their other meanings only once no locale can parse the string
        # with the default ones.
        for locale in locales:
            parsed_date = self._parse_using_locale(
                locale,
                date_string,
                date_formats,
                ignore_surrounding_text,
                alternatives=True,
            )
            if parsed_date:
                return parsed_date
        return None

    def _parse_using_locale(
        self,
        locale: "Locale",
        date_string: str,
        date_formats: Iterable[str] | None,
        ignore_surrounding_text: bool,
        alternatives: bool = False,
    ) -> DateData | None:
        parsed_date = _DateLocaleParser.parse(
            locale,
            date_string,
            date_formats,
            settings=self._settings,
            ignore_surrounding_text=ignore_surrounding_text,
            alternatives=alternatives,
        )
        if parsed_date:
            parsed_date["locale"] = locale.shortname
            if self.try_previous_locales:
                with self._lock:
                    self.previous_locales[locale] = None
        return parsed_date

    def get_date_tuple(self, *args: Any, **kwargs: Any) -> tuple[Any, ...]:
        date_data = self.get_date_data(*args, **kwargs)
        fields = {k: v for k, v in date_data.__dict__.items() if k != "parts"}
        date_tuple = collections.namedtuple("DateData", fields)  # type: ignore[misc]  # noqa: PYI024
        result: tuple[Any, ...] = date_tuple(**fields)
        return result

    def _get_applicable_locales(
        self, date_string: str, ignore_surrounding_text: bool = False
    ) -> Iterator["Locale"]:
        # The given order is preserved if requested either through the
        # ``use_given_order`` constructor argument or the
        # ``USE_GIVEN_LANGUAGE_ORDER`` setting (which also reaches the
        # top-level :func:`dateparser.parse`). When no languages or locales are
        # given there is nothing to order, so the default order is used.
        use_given_order = (
            self.use_given_order or self._settings.USE_GIVEN_LANGUAGE_ORDER
        )

        pop_tz_cache: list[str | None] = []

        def date_strings() -> Iterator[str]:
            """A generator instead of a static list to avoid calling
            pop_tz_offset_from_string if the first locale matches on unmodified
            date_string.
            """
            stripped_date_string: str | None
            yield date_string
            if not pop_tz_cache:
                stripped_date_string, _ = pop_tz_offset_from_string(
                    date_string, as_offset=False
                )
                if stripped_date_string == date_string:
                    stripped_date_string = None
                pop_tz_cache[:] = [stripped_date_string]
            (stripped_date_string,) = pop_tz_cache
            if stripped_date_string is not None:
                yield stripped_date_string

        if self.try_previous_locales:
            with self._lock:
                previous_locales = list(self.previous_locales.keys())
            for locale in previous_locales:
                for s in date_strings():
                    if self._is_applicable_locale(locale, s, ignore_surrounding_text):
                        yield locale

        if self.detect_languages_function and not self.languages and not self.locales:
            detected_languages = self.detect_languages_function(
                text=date_string,
                confidence_threshold=self._settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD,
            )

            self.languages = map_languages(detected_languages)

        for locale in self._get_locale_loader().get_locales(
            languages=self.languages,
            locales=self.locales,
            region=self.region,
            use_given_order=use_given_order,
        ):
            for s in date_strings():
                if self._is_applicable_locale(locale, s, ignore_surrounding_text):
                    yield locale

        if self._settings.DEFAULT_LANGUAGES:
            for locale in self._get_locale_loader().get_locales(
                languages=self._settings.DEFAULT_LANGUAGES,
                locales=None,
                region=self.region,
                use_given_order=use_given_order,
            ):
                yield locale

    def _is_applicable_locale(
        self,
        locale: "Locale",
        date_string: str,
        ignore_surrounding_text: bool = False,
    ) -> bool:
        return locale.is_applicable(
            date_string,
            strip_timezone=False,  # it is stripped outside
            settings=self._settings,
            ignore_surrounding_text=ignore_surrounding_text,
        )

    _locale_loader_lock = threading.Lock()

    @classmethod
    def _get_locale_loader(cls) -> LocaleDataLoader:
        if not cls.locale_loader:
            with cls._locale_loader_lock:
                if not cls.locale_loader:
                    cls.locale_loader = LocaleDataLoader()
        return cls.locale_loader
