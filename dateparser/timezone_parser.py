import warnings
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone, tzinfo
from typing import TYPE_CHECKING, Literal, TypedDict, overload

import regex as re

from .timezones import timezone_info_list

if TYPE_CHECKING:
    from .conf import Settings


class _TzOffsetInfo(TypedDict):
    regex: re.Pattern[str]
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


def _search_and_pop_tz(date_string: str) -> tuple[str, str, _TzOffsetInfo] | None:
    """Find and remove the first timezone token from ``date_string``.

    Returns a ``(new_string, name, info)`` tuple, or ``None`` if no timezone
    token is present.
    """
    if not _search_regex_ignorecase.search(date_string):
        return None
    for name, info in _tz_offsets:
        timezone_match = info["regex"].search(date_string)
        if timezone_match:
            start, stop = timezone_match.span()
            # A token glued to the digits that follow, as in
            # 2019-09-28WIB19:17:34, leaves a space so that the date and time
            # digits stay apart.
            glued = stop < len(date_string) and date_string[stop - 1].isalpha()
            separator = " " if glued else ""
            return (
                date_string[: start + 1] + separator + date_string[stop:],
                name,
                info,
            )
    return None


@overload
def pop_tz_offset_from_string(
    date_string: str,
    as_offset: Literal[True] = True,
    settings: "Settings | None" = None,
) -> tuple[str, StaticTzInfo | None]: ...


@overload
def pop_tz_offset_from_string(
    date_string: str,
    as_offset: Literal[False],
    settings: "Settings | None" = None,
) -> tuple[str, str | None]: ...


def pop_tz_offset_from_string(
    date_string: str, as_offset: bool = True, settings: "Settings | None" = None
) -> tuple[str, StaticTzInfo | str | None]:
    def offset_of(name: str, info: _TzOffsetInfo) -> timedelta:
        if settings is None:
            return info["offset"]
        return settings.TIMEZONE_ABBREVIATIONS.get(name, info["offset"])

    match = _search_and_pop_tz(date_string)
    if match is None:
        return date_string, None

    date_string, name, info = match
    offset = offset_of(name, info)
    result = StaticTzInfo(name, offset) if as_offset else name

    # A date string may carry both a numeric UTC offset and a redundant,
    # equivalent timezone abbreviation, e.g. the RFC 2822 email form
    # ``-0500 (CDT)`` (the parenthesised name is informational and the numeric
    # offset is authoritative). Only one token is removed above; strip a second,
    # equivalent one so the leftover does not break the rest of the parser.
    # The remainder is right-stripped first because the numeric-offset regexes
    # are anchored at the end of the string.
    while True:
        extra = _search_and_pop_tz(date_string.rstrip())
        if extra is None or offset_of(extra[1], extra[2]) != offset:
            break
        date_string = extra[0]

    return date_string, result


def word_is_tz(word: str) -> bool:
    return bool(_search_regex.match(word))


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
    return bool(_search_regex_ignorecase.fullmatch(token.strip()))


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
) -> Iterator[tuple[str, _TzOffsetInfo]]:
    def get_offset(
        tz_obj: tuple[str, int], regex: str, repl: str = "", replw: str = ""
    ) -> tuple[str, _TzOffsetInfo]:
        return (
            tz_obj[0],
            {
                "regex": re.compile(
                    re.sub(repl, replw, regex % tz_obj[0]), re.IGNORECASE
                ),
                "offset": timedelta(seconds=tz_obj[1]),
            },
        )

    for tz_info in timezone_info_list:
        for regex in tz_info["regex_patterns"]:
            for tz_obj in tz_info["timezones"]:
                search_regex_parts.append(tz_obj[0])
                yield get_offset(tz_obj, regex)

                # alternate patterns
                for replace, replacewith in tz_info.get("replace", []):
                    search_regex_parts.append(re.sub(replace, replacewith, tz_obj[0]))
                    yield get_offset(tz_obj, regex, repl=replace, replw=replacewith)


def get_local_tz_offset() -> timedelta:
    offset = datetime.now() - datetime.now(tz=timezone.utc).replace(tzinfo=None)
    return timedelta(days=offset.days, seconds=round(offset.seconds, -1))


_search_regex_parts: list[str] = []
_tz_offsets = list(build_tz_offsets(_search_regex_parts))
_search_regex = re.compile("|".join(_search_regex_parts))
_search_regex_ignorecase = re.compile("|".join(_search_regex_parts), re.IGNORECASE)
local_tz_offset = get_local_tz_offset()
