import re
import threading
import warnings
from datetime import datetime, timedelta, timezone, tzinfo
from functools import cache
from typing import TYPE_CHECKING, Literal, NamedTuple, TypedDict, overload

import pytz
import regex
from pytz.tzinfo import BaseTzInfo

from .timezones import timezone_info_list

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .conf import Settings


class _TzOffsetInfo(TypedDict):
    regex: regex.Pattern[str]
    offset: timedelta


class StaticTzInfo(tzinfo):
    def __init__(self, name: str, offset: timedelta) -> None:
        self.__offset = offset
        self.__name = name

    def tzname(self, dt: datetime | None) -> str:
        return self.__name

    def utcoffset(self, dt: datetime | None) -> timedelta:
        return self.__offset

    def dst(self, dt: datetime | None) -> timedelta:
        return timedelta(0)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.__name}'>"

    def localize(self, dt: datetime, is_dst: bool = False) -> datetime:
        if dt.tzinfo is not None:
            raise ValueError("Not naive datetime (tzinfo is already set)")
        return dt.replace(tzinfo=self)

    def __getinitargs__(self) -> tuple[str, timedelta]:
        return self.__name, self.__offset


def _search_and_pop_tz(
    date_string: str,
) -> tuple[str, str, StaticTzInfo | BaseTzInfo] | None:
    """Find and remove the first timezone token from ``date_string``.

    Returns a ``(new_string, name, tz)`` tuple, or ``None`` if no timezone
    token is present.
    """
    found = _find_tz(date_string)
    if found is None:
        return None
    (start, stop), name, tz = found
    # A token glued to the digits that follow, as in
    # 2019-09-28WIB19:17:34, leaves a space so that the date and time
    # digits stay apart.
    glued = stop < len(date_string) and date_string[stop - 1].isalpha()
    separator = " " if glued else ""
    return date_string[: start + 1] + separator + date_string[stop:], name, tz


def _same_offset(a: StaticTzInfo | BaseTzInfo, b: StaticTzInfo | BaseTzInfo) -> bool:
    if isinstance(a, StaticTzInfo) and isinstance(b, StaticTzInfo):
        return a.utcoffset(None) == b.utcoffset(None)
    if isinstance(a, StaticTzInfo):
        a, b = b, a
    if isinstance(b, StaticTzInfo):
        # January and July cover both the standard and the daylight saving
        # offset of a zone, in either hemisphere.
        return b.utcoffset(None) in {
            a.utcoffset(datetime(2000, month, 1)) for month in (1, 7)
        }
    return a is b


@overload
def pop_tz_offset_from_string(
    date_string: str,
    as_offset: Literal[True] = True,
    settings: "Settings | None" = None,
) -> tuple[str, StaticTzInfo | BaseTzInfo | None]: ...


@overload
def pop_tz_offset_from_string(
    date_string: str,
    as_offset: Literal[False],
    settings: "Settings | None" = None,
) -> tuple[str, str | None]: ...


def pop_tz_offset_from_string(
    date_string: str, as_offset: bool = True, settings: "Settings | None" = None
) -> tuple[str, StaticTzInfo | BaseTzInfo | str | None]:
    overrides = settings.TIMEZONE_ABBREVIATIONS if settings else {}

    def override(name: str, tz: StaticTzInfo | BaseTzInfo) -> StaticTzInfo | BaseTzInfo:
        return StaticTzInfo(name, overrides[name]) if name in overrides else tz

    match = _search_and_pop_tz(date_string)
    if match is None:
        return date_string, None

    date_string, name, tz = match
    tz = override(name, tz)
    result = tz if as_offset else name

    # A date string may carry both a numeric UTC offset and a redundant,
    # equivalent timezone abbreviation, e.g. the RFC 2822 email form
    # ``-0500 (CDT)`` (the parenthesised name is informational and the numeric
    # offset is authoritative). Only one token is removed above; strip a second,
    # equivalent one so the leftover does not break the rest of the parser.
    # The remainder is right-stripped first because the numeric-offset regexes
    # are anchored at the end of the string. An abbreviation that follows
    # daylight saving time, such as ``CT``, is equivalent to both of its
    # offsets, so the numeric offset decides which one applies.
    while True:
        extra = _search_and_pop_tz(date_string.rstrip())
        if extra is None:
            break
        extra_tz = override(extra[1], extra[2])
        if not _same_offset(extra_tz, tz):
            break
        date_string = extra[0]
        if not isinstance(tz, StaticTzInfo):
            tz = extra_tz
            if as_offset:
                result = tz

    return date_string, result


def word_is_tz(word: str) -> bool:
    return bool(_tz_regexes().names.match(word))


def is_timezone_token(token: str) -> bool:
    """Whether ``token`` is, on its own, a recognized timezone abbreviation.

    Unlike :func:`word_is_tz` (a case-sensitive prefix match used while
    scanning original-cased text), this trims surrounding whitespace and does a
    case-insensitive *full* match, so it recognizes an already-lowercased,
    space-padded token such as ``" est"``. Because the match is anchored, an
    ordinary word that merely begins with a timezone abbreviation is not
    treated as a timezone (e.g. ``"actualisé"`` is not the ``ACT`` zone). This
    is used only on single edge tokens, so the trailing ``.*`` in the UTC/GMT
    numeric-offset patterns (which a full match would otherwise let absorb
    following text) is not a concern here.
    """
    return bool(_tz_regexes().names_ignorecase.fullmatch(token.strip()))


def convert_to_local_tz(
    datetime_obj: datetime, datetime_tz_offset: timedelta
) -> datetime:
    warnings.warn(
        "dateparser.timezone_parser.convert_to_local_tz is deprecated and "
        "will be removed in a future version.",
        FutureWarning,
        stacklevel=2,
    )
    return datetime_obj - datetime_tz_offset + local_tz_offset


def build_tz_offsets(
    search_regex_parts: list[str],
) -> "Iterator[tuple[str, _TzOffsetInfo]]":
    warnings.warn(
        "dateparser.timezone_parser.build_tz_offsets() is deprecated and "
        "will be removed in a future version.",
        FutureWarning,
        stacklevel=2,
    )

    def get_offset(
        tz_obj: tuple[str, int | str], pattern: str, repl: str = "", replw: str = ""
    ) -> tuple[str, _TzOffsetInfo]:
        offset = _build_tz(*tz_obj).utcoffset(datetime(2000, 1, 1))
        assert offset is not None
        return (
            tz_obj[0],
            {
                "regex": regex.compile(
                    regex.sub(repl, replw, pattern % tz_obj[0]), regex.IGNORECASE
                ),
                "offset": offset,
            },
        )

    def offsets() -> "Iterator[tuple[str, _TzOffsetInfo]]":
        for tz_info in timezone_info_list:
            for pattern in tz_info["regex_patterns"]:
                for tz_obj in tz_info["timezones"]:
                    search_regex_parts.append(tz_obj[0])
                    yield get_offset(tz_obj, pattern)
                    for replace, replacewith in tz_info.get("replace", []):
                        search_regex_parts.append(
                            regex.sub(replace, replacewith, tz_obj[0])
                        )
                        yield get_offset(tz_obj, pattern, replace, replacewith)

    return offsets()


class _TzRegexes(NamedTuple):
    families: list[
        tuple[regex.Pattern[str], list[tuple[str, StaticTzInfo | BaseTzInfo]]]
    ]
    """``(pattern, timezones)`` pairs, one per pattern template of
    :data:`~dateparser.timezones.timezone_info_list`, where group ``tz<i>`` of
    *pattern* matching means that ``timezones[i]``, a ``(name, tz)`` pair, was
    found."""
    names: re.Pattern[str]
    """Matches any timezone name, unless it is part of a possessive or of a
    per-second unit."""
    names_ignorecase: re.Pattern[str]
    """Matches any timezone name, case-insensitively."""


_tz_regexes_lock = threading.Lock()


def _tz_regexes() -> _TzRegexes:
    """Return the timezone regexes, compiled on first use."""
    with _tz_regexes_lock:
        return _build_tz_regexes()


def _build_tz(name: str, offset: int | str) -> StaticTzInfo | BaseTzInfo:
    if isinstance(offset, str):
        return pytz.timezone(offset)
    return StaticTzInfo(name, timedelta(seconds=offset))


@cache
def _build_tz_regexes() -> _TzRegexes:
    families: list[
        tuple[regex.Pattern[str], list[tuple[str, StaticTzInfo | BaseTzInfo]]]
    ] = []
    names: list[str] = []
    for tz_info in timezone_info_list:
        for template in tz_info["regex_patterns"]:
            alternatives: list[str] = []
            timezones: list[tuple[str, StaticTzInfo | BaseTzInfo]] = []
            for name, offset in tz_info["timezones"]:
                tz = _build_tz(name, offset)
                variants = [name] + [
                    regex.sub(replace, replacewith, name)
                    for replace, replacewith in tz_info.get("replace", [])
                ]
                for variant in variants:
                    names.append(variant)
                    alternatives.append(f"(?P<tz{len(timezones)}>{variant})")
                    timezones.append((name, tz))
            flags = regex.IGNORECASE
            if template.endswith("$"):
                # Every match ends at the end of the string, so searching
                # backwards finds the same match much faster.
                flags |= regex.REVERSE
            pattern = regex.compile(
                template % f"(?:{'|'.join(alternatives)})", flags, cache_pattern=False
            )
            families.append((pattern, timezones))
    # Only used for anchored matching, which re compiles and runs faster.
    names_pattern = "|".join(names)
    return _TzRegexes(
        families,
        re.compile(rf"(?:{names_pattern})(?!['’][^\W\d_]|/s\b)"),
        re.compile(names_pattern, re.IGNORECASE),
    )


def _find_tz(
    string: str,
) -> tuple[tuple[int, int], str, StaticTzInfo | BaseTzInfo] | None:
    """Return the span, name and tzinfo of the timezone found in *string*,
    or ``None``.

    Earlier pattern templates take precedence over later ones. Within a
    template, the earliest timezone wins, and ties go to the leftmost match.
    """
    for pattern, timezones in _tz_regexes().families:
        matches: Iterable[regex.Match[str]]
        if pattern.flags & regex.REVERSE:
            match = pattern.search(string)
            matches = [match] if match else []
        else:
            # overlapped: in "EST/EDT" both matches share the "/"
            matches = pattern.finditer(string, overlapped=True)
        best: tuple[int, tuple[int, int]] | None = None
        for match in matches:
            group = next(k for k, v in match.groupdict().items() if v is not None)
            index = int(group[2:])
            if best is None or index < best[0]:
                best = (index, match.span())
        if best:
            name, tz = timezones[best[0]]
            return best[1], name, tz
    return None


def get_local_tz_offset() -> timedelta:
    offset = datetime.now() - datetime.now(tz=timezone.utc).replace(tzinfo=None)
    return timedelta(days=offset.days, seconds=round(offset.seconds, -1))


local_tz_offset = get_local_tz_offset()
