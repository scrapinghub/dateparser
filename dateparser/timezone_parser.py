import re
from datetime import datetime, timedelta, timezone, tzinfo
from functools import cache
from typing import TYPE_CHECKING, Literal, overload

import regex

from .timezones import timezone_info_list

if TYPE_CHECKING:
    from collections.abc import Iterable


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


def _search_and_pop_tz(date_string: str) -> tuple[str, str, timedelta] | None:
    """Find and remove the first timezone token from ``date_string``.

    Returns a ``(new_string, name, offset)`` tuple, or ``None`` if no timezone
    token is present.
    """
    found = _find_tz(date_string)
    if found is None:
        return None
    (start, stop), name, offset = found
    # A token glued to the digits that follow, as in
    # 2019-09-28WIB19:17:34, leaves a space so that the date and time
    # digits stay apart.
    glued = stop < len(date_string) and date_string[stop - 1].isalpha()
    separator = " " if glued else ""
    return date_string[: start + 1] + separator + date_string[stop:], name, offset


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
    match = _search_and_pop_tz(date_string)
    if match is None:
        return date_string, None

    date_string, name, offset = match
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
        if extra is None or extra[2] != offset:
            break
        date_string = extra[0]

    return date_string, result


def word_is_tz(word: str) -> bool:
    return bool(_tz_regexes()[1].match(word))


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
    return bool(_tz_regexes()[2].fullmatch(token.strip()))


def convert_to_local_tz(
    datetime_obj: datetime, datetime_tz_offset: timedelta
) -> datetime:
    return datetime_obj - datetime_tz_offset + local_tz_offset


@cache
def _tz_regexes() -> tuple[
    list[tuple[regex.Pattern[str], list[tuple[str, timedelta]]]],
    re.Pattern[str],
    re.Pattern[str],
]:
    """Return the timezone regexes, compiled on first use.

    The first item is a list of ``(pattern, timezones)`` pairs, one per
    pattern template of :data:`~dateparser.timezones.timezone_info_list`,
    where group ``tz<i>`` of *pattern* matching means that ``timezones[i]``, a
    ``(name, offset)`` pair, was found. The other two items match any timezone
    name, case-sensitively and case-insensitively.
    """
    families: list[tuple[regex.Pattern[str], list[tuple[str, timedelta]]]] = []
    names: list[str] = []
    for tz_info in timezone_info_list:
        for template in tz_info["regex_patterns"]:
            alternatives: list[str] = []
            timezones: list[tuple[str, timedelta]] = []
            for name, offset in tz_info["timezones"]:
                variants = [name] + [
                    regex.sub(replace, replacewith, name)
                    for replace, replacewith in tz_info.get("replace", [])
                ]
                for variant in variants:
                    names.append(variant)
                    alternatives.append(f"(?P<tz{len(timezones)}>{variant})")
                    timezones.append((name, timedelta(seconds=offset)))
            flags = regex.IGNORECASE
            if template.endswith("$"):
                # Every match ends at the end of the string, so searching
                # backwards finds the same match much faster.
                flags |= regex.REVERSE
            pattern = regex.compile(template % f"(?:{'|'.join(alternatives)})", flags)
            families.append((pattern, timezones))
    # Only used for anchored matching, which re compiles and runs faster.
    names_pattern = "|".join(names)
    return (
        families,
        re.compile(names_pattern),
        re.compile(names_pattern, re.IGNORECASE),
    )


def _find_tz(
    string: str,
) -> tuple[tuple[int, int], str, timedelta] | None:
    """Return the span, name and offset of the timezone found in *string*,
    or ``None``.

    Earlier pattern templates take precedence over later ones. Within a
    template, the earliest timezone wins, and ties go to the leftmost match.
    """
    for pattern, timezones in _tz_regexes()[0]:
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
            name, offset = timezones[best[0]]
            return best[1], name, offset
    return None


def get_local_tz_offset() -> timedelta:
    offset = datetime.now() - datetime.now(tz=timezone.utc).replace(tzinfo=None)
    return timedelta(days=offset.days, seconds=round(offset.seconds, -1))


local_tz_offset = get_local_tz_offset()
