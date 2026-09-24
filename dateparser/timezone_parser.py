from datetime import datetime, timedelta, timezone, tzinfo
from functools import cache

import re

import regex

from .timezones import timezone_info_list


class StaticTzInfo(tzinfo):
    def __init__(self, name, offset):
        self.__offset = offset
        self.__name = name

    def tzname(self, dt):
        return self.__name

    def utcoffset(self, dt):
        return self.__offset

    def dst(self, dt):
        return timedelta(0)

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.__name)

    def localize(self, dt, is_dst=False):
        if dt.tzinfo is not None:
            raise ValueError("Not naive datetime (tzinfo is already set)")
        return dt.replace(tzinfo=self)

    def __getinitargs__(self):
        return self.__name, self.__offset


def pop_tz_offset_from_string(date_string, as_offset=True):
    found = _find_tz(date_string)
    if found:
        (start, stop), name, offset = found
        date_string = date_string[: start + 1] + date_string[stop:]
        return (
            date_string,
            StaticTzInfo(name, offset) if as_offset else name,
        )
    return date_string, None


def word_is_tz(word):
    return bool(_tz_regexes()[1].match(word))


def is_timezone_token(token):
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


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


@cache
def _tz_regexes():
    """Return the timezone regexes, compiled on first use.

    The first item is a list of ``(pattern, timezones)`` pairs, one per
    pattern template of :data:`~dateparser.timezones.timezone_info_list`,
    where group ``tz<i>`` of *pattern* matching means that ``timezones[i]``, a
    ``(name, offset)`` pair, was found. The other two items match any timezone
    name, case-sensitively and case-insensitively.
    """
    families = []
    names = []
    for tz_info in timezone_info_list:
        for template in tz_info["regex_patterns"]:
            alternatives = []
            timezones = []
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


def _find_tz(string):
    """Return the span, name and offset of the timezone found in *string*,
    or ``None``.

    Earlier pattern templates take precedence over later ones. Within a
    template, the leftmost match wins, and ties go to the earliest timezone.
    """
    for pattern, timezones in _tz_regexes()[0]:
        match = pattern.search(string)
        if match:
            group = next(k for k, v in match.groupdict().items() if v is not None)
            name, offset = timezones[int(group[2:])]
            return match.span(), name, offset
    return None


def get_local_tz_offset():
    offset = datetime.now() - datetime.now(tz=timezone.utc).replace(tzinfo=None)
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


local_tz_offset = get_local_tz_offset()
