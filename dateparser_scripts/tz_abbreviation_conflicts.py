"""Cross-check dateparser's timezone-abbreviation table against the tz database.

Many timezone abbreviations are genuinely ambiguous: several IANA tz database
zones use the same letters for different UTC offsets ("CST" is both US Central
Standard Time and China Standard Time). The tz database provides no preferred
answer for those, so ``dateparser/timezones.py`` keeps one arbitrary offset per
abbreviation, originally taken from a Wikipedia scrape.

Some abbreviations are *not* ambiguous, though: every zone the tz database
names with those letters agrees on a single UTC offset. When dateparser's table
disagrees with that offset, its value is not "another valid reading" -- no zone
goes by that name at that offset. That was the case for "BST", which resolved
to +11 although the only zones named "BST" today are the UK ones, at +1 (see
#1321 and #1322). This script finds every such case generically, so the table
can be kept in sync without a one-off patch per abbreviation.

Two kinds of conflict are reported:

``unambiguous``
    The tz database maps the abbreviation to exactly one offset and dateparser
    disagrees. The tz database offset should be preferred.
``unsupported``
    The tz database maps the abbreviation to several offsets and dateparser's
    value is none of them. There is no single offset to prefer, so this needs a
    human decision, but the current value is still unsupported by any zone.

Zone data comes from ``pytz``, which is already a dateparser dependency and
bundles its own copy of the tz database. That keeps results identical on every
platform, unlike the standard library ``zoneinfo`` module, whose data comes
from the operating system and is missing entirely on Windows unless the
separate ``tzdata`` package is installed.

What this can and cannot see
----------------------------

Only the abbreviations the tz database still prints are checked, around 50 of
the 400-odd in dateparser's table. The rest are invisible here and are left to
dateparser:

* Modern tz database releases name a zone after its offset ("+11", "-0930")
  unless the abbreviation is in common English use, so a zone can drop out of
  this comparison without the abbreviation falling out of use. "BST" for
  Bougainville is exactly that: the zone now prints "+11". What the check
  really shows is that no zone *is named* "BST" at +11 any more, which is the
  practical question for a parser.
* Abbreviations no zone uses in the reference window at all, such as ``AHST``
  or ``LMT``, are kept by dateparser so that historical text still parses.
* pytz ships ``MET`` as a copy of ``CET``, so it prints "CET"/"CEST" and the
  ``MET``/``MEST`` abbreviations never reach this comparison.

Run it to print a report; it exits non-zero when it finds anything::

    python -m dateparser_scripts.tz_abbreviation_conflicts
"""

from collections import namedtuple
from datetime import datetime

import pytz
import regex as re

from dateparser.timezones import timezone_info_list

# Years sampled to determine what an abbreviation means *today*. Both bounds
# are load-bearing, and the window is pinned deliberately, like the CLDR
# version in ``dateparser_scripts/utils.py``.
#
# The upper bound stays in settled years: the tz database records future
# daylight-saving rules as predictions that change between releases, so
# sampling them would make the result depend on the installed tz database
# version rather than on real usage.
#
# The lower bound keeps retired meanings out. Slide this window forward when
# refreshing the table, and do not widen it backwards: reaching further back
# re-admits abbreviations the tz database has since dropped and reports them as
# if they were current. Reaching back to 1999 picks up Guam's old "GST", which
# would report dateparser's "GST" (+4, Gulf Standard Time) as an unambiguous
# conflict against +10, even though Guam has used "ChST" since 2000.
REFERENCE_YEARS = range(2021, 2026)

# Sampling January, April, July and October catches both the standard-time and
# the daylight-saving abbreviation of every zone, in either hemisphere.
REFERENCE_MONTHS = (1, 4, 7, 10)

# The tz database uses names such as "+11" or "-0930" for zones that have no
# real abbreviation. They are not abbreviations, and dateparser matches numeric
# offsets through separate UTC/GMT patterns, so they are ignored here.
_NUMERIC_ZONE_NAME = re.compile(r"[+-]\d{2,4}")

Conflict = namedtuple(
    "Conflict", ["abbreviation", "kind", "dateparser_offset", "tz_database_offsets"]
)


def static_tz_abbreviations():
    """Return ``{abbreviation: offset_in_seconds}`` as dateparser resolves it.

    A few abbreviations are listed more than once in ``timezone_info_list``
    (``LMT`` appears four times with four different offsets). Only the first
    entry can ever win: ``build_tz_offsets`` keeps the table order and
    ``pop_tz_offset_from_string`` returns the first pattern that matches. So
    the first entry, not the set of all of them, is what this comparison has
    to use -- otherwise a wrong first entry would be masked by a correct later
    one.

    Keys are upper-cased because dateparser matches abbreviations
    case-insensitively, so a differently-cased entry such as ``ChST`` is the
    same abbreviation and has to be compared as one.
    """
    effective = {}
    for group in timezone_info_list:
        for name, offset in group["timezones"]:
            effective.setdefault(name.upper(), offset)
    return effective


def tz_database_abbreviations():
    """Return ``{abbreviation: {offset_in_seconds, ...}}`` from the tz database.

    Every zone is sampled, including the deprecated aliases (``US/Pacific``,
    ``Asia/Calcutta``) that ``pytz.all_timezones`` lists alongside canonical
    zones. Aliases resolve to the same rules as the zones they link to, so they
    only ever repeat offsets a canonical zone already contributed; including
    them costs nothing and keeps the scan independent of how pytz classifies
    any individual zone.
    """
    samples = [
        datetime(year, month, 15, 12, 0, 0)
        for year in REFERENCE_YEARS
        for month in REFERENCE_MONTHS
    ]
    abbreviations = {}
    for zone_name in pytz.all_timezones:
        zone = pytz.timezone(zone_name)
        for naive in samples:
            localized = zone.localize(naive)
            abbreviation = localized.tzname()
            if not abbreviation or _NUMERIC_ZONE_NAME.fullmatch(abbreviation):
                continue
            offset = int(localized.utcoffset().total_seconds())
            abbreviations.setdefault(abbreviation.upper(), set()).add(offset)
    return abbreviations


def find_conflicts(static=None, tz_database=None):
    """Return the sorted list of :class:`Conflict` between both tables.

    ``static`` and ``tz_database`` default to the real tables and are only
    meant to be passed in by the tests.

    Abbreviations the tz database no longer uses at all are skipped: dateparser
    deliberately keeps obsolete abbreviations such as ``AHST`` or ``LMT`` so
    that historical text still parses, and the tz database has nothing to say
    about them.
    """
    static = static_tz_abbreviations() if static is None else static
    tz_database = tz_database_abbreviations() if tz_database is None else tz_database

    conflicts = []
    for abbreviation, tz_database_offsets in tz_database.items():
        if abbreviation not in static:
            continue
        dateparser_offset = static[abbreviation]
        if dateparser_offset in tz_database_offsets:
            continue
        kind = "unambiguous" if len(tz_database_offsets) == 1 else "unsupported"
        conflicts.append(
            Conflict(abbreviation, kind, dateparser_offset, sorted(tz_database_offsets))
        )
    return sorted(conflicts)


def main():
    found = find_conflicts()
    if not found:
        print(
            "No conflicts: every abbreviation dateparser shares with the tz "
            "database resolves to an offset some zone actually uses."
        )
        return 0
    for conflict in found:
        if conflict.kind == "unambiguous":
            detail = f"the tz database only ever uses {conflict.tz_database_offsets[0]}"
        else:
            detail = f"no zone uses it; options are {conflict.tz_database_offsets}"
        print(
            f"{conflict.abbreviation}: dateparser uses {conflict.dateparser_offset}, {detail}"
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
