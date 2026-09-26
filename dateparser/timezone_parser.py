from collections.abc import Iterator
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Literal, TypedDict, overload

import regex as re

from .timezones import timezone_info_list


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
        return "<%s '%s'>" % (self.__class__.__name__, self.__name)

    def localize(self, dt: datetime, is_dst: bool = False) -> datetime:
        if dt.tzinfo is not None:
            raise ValueError("Not naive datetime (tzinfo is already set)")
        return dt.replace(tzinfo=self)

    def __getinitargs__(self) -> tuple[str, timedelta]:
        return self.__name, self.__offset


@overload
def pop_tz_offset_from_string(
    date_string: str, as_offset: Literal[True] = True
) -> tuple[str, StaticTzInfo | None]: ...


@overload
def pop_tz_offset_from_string(
    date_string: str, as_offset: Literal[False]
) -> tuple[str, str | None]: ...


def pop_tz_offset_from_string(
    date_string: str, as_offset: bool = True
) -> tuple[str, StaticTzInfo | str | None]:
    if _search_regex_ignorecase.search(date_string):
        for name, info in _tz_offsets:
            timezone_re = info["regex"]
            timezone_match = timezone_re.search(date_string)
            if timezone_match:
                start, stop = timezone_match.span()
                date_string = date_string[: start + 1] + date_string[stop:]
                return (
                    date_string,
                    StaticTzInfo(name, info["offset"]) if as_offset else name,
                )
    return date_string, None


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
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


_search_regex_parts: list[str] = []
_tz_offsets = list(build_tz_offsets(_search_regex_parts))
_search_regex = re.compile("|".join(_search_regex_parts))
_search_regex_ignorecase = re.compile("|".join(_search_regex_parts), re.IGNORECASE)
local_tz_offset = get_local_tz_offset()
