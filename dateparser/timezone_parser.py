from datetime import datetime, timedelta, timezone, tzinfo

import regex as re

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


def _search_tz(date_string):
    if _search_regex_ignorecase.search(date_string):
        for name, info in _tz_offsets:
            timezone_match = info["regex"].search(date_string)
            if timezone_match:
                return name, info, timezone_match
    return None


def pop_tz_offset_from_string(date_string, as_offset=True):
    found = _search_tz(date_string)
    if found:
        name, info, timezone_match = found
        start, stop = timezone_match.span()
        date_string = date_string[: start + 1] + date_string[stop:]
        return (
            date_string,
            StaticTzInfo(name, info["offset"]) if as_offset else name,
        )
    return date_string, None


_time_suffix_regex = re.compile(
    r"(?:\d:\d{2}(?::\d{2})?(?:\s*[ap]\.?m\.?)?|\d\s*[ap]\.?m\.?)\s*$",
    re.IGNORECASE,
)


def _strip_tz(date_string):
    """Return *date_string* without its timezone, or ``None`` if it has none,
    and whether that timezone is unambiguous, i.e. unlikely to be a word of
    some language instead: written in uppercase, like ``MART``, or right after
    a time, like ``4:30 pm est``, as opposed to the Turkish month ``Mart``."""
    found = _search_tz(date_string)
    if not found:
        return None, False
    start, stop = found[2].span()
    before, tz = date_string[: start + 1], date_string[start + 1 : stop]
    unambiguous = tz.isupper() or bool(_time_suffix_regex.search(before))
    return before + date_string[stop:], unambiguous


def word_is_tz(word):
    return bool(_search_regex.match(word))


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
    return bool(_search_regex_ignorecase.fullmatch(token.strip()))


def convert_to_local_tz(datetime_obj, datetime_tz_offset):
    return datetime_obj - datetime_tz_offset + local_tz_offset


def build_tz_offsets(search_regex_parts):
    def get_offset(tz_obj, regex, repl="", replw=""):
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


def get_local_tz_offset():
    offset = datetime.now() - datetime.now(tz=timezone.utc).replace(tzinfo=None)
    offset = timedelta(days=offset.days, seconds=round(offset.seconds, -1))
    return offset


_search_regex_parts = []
_tz_offsets = list(build_tz_offsets(_search_regex_parts))
_search_regex = re.compile("|".join(_search_regex_parts))
_search_regex_ignorecase = re.compile("|".join(_search_regex_parts), re.IGNORECASE)
local_tz_offset = get_local_tz_offset()
