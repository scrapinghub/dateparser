import datetime as dt
from datetime import datetime, timedelta
from unittest import SkipTest
from unittest.mock import Mock, patch

from parameterized import param, parameterized
from pytz import timezone

import dateparser.timezone_parser
from dateparser import parse
from dateparser.timezone_parser import (
    StaticTzInfo,
    get_local_tz_offset,
    is_timezone_token,
    pop_tz_offset_from_string,
    word_is_tz,
)
from tests import BaseTestCase


class TestTZPopping(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.initial_string = self.datetime_string = self.timezone_offset = (
            NotImplemented
        )

    @parameterized.expand(
        [
            param("Sep 03 2014 | 4:32 pm EDT", -4),
            param("17th October, 2034 @ 01:08 am PDT", -7),
            param("17th October, 2034 @ 01:08 am (PDT)", -7),
            param("October 17, 2014 at 7:30 am PST", -8),
            param("20 Oct 2014 13:08 CET", +1),
            param("20 Oct 2014 13:08cet", +1),
            param("Nov 25 2014 | 10:17 pm EST", -5),
            param("Nov 25 2014 | 10:17 pm +0600", +6),
            param("Nov 25 2014 | 10:17 pm -0930", -9.5),
            param("20 Oct 2014 | 05:17 am -1200", -12),
            param("20 Oct 2014 | 05:17 am +0000", 0),
            param("20 Oct 2014 | 05:17 am -0000", 0),
            param("15 May 2004", None),
            param("Wed Aug 05 12:00:00 EDTERR 2015", None),
            param("Wed Aug 05 12:00:00 EDT 2015", -4),
            param("April 10, 2016 at 12:00:00 UTC", 0),
            param("April 10, 2016 at 12:00:00 MEZ", 1),
            param("April 10, 2016 at 12:00:00 MESZ", 2),
            param("April 10, 2016 at 12:00:00 GMT+2", 2),
            param("April 10, 2016 at 12:00:00 UTC+2:00", 2),
            param("April 10, 2016 at 12:00:00 GMT+02:00", 2),
            param("April 10, 2016 at 12:00:00 UTC+5:30", 5.5),
            param("April 10, 2016 at 12:00:00 GMT+05:30", 5.5),
            param("April 10, 2016 at 12:00:00 UTC-2", -2),
            param("April 10, 2016 at 12:00:00 GMT-2:00", -2),
            param("April 10, 2016 at 12:00:00 UTC-02:00", -2),
            param("April 10, 2016 at 12:00:00 GMT-9:30", -9.5),
            param("April 10, 2016 at 12:00:00 UTC-09:30", -9.5),
            param("Thu, 24 Nov 2016 16:03:00 UT", 0),
            param("Fri Sep 23 2016 10:34:51 GMT+0800 (CST)", 8),
            param("Fri Sep 23 2016 10:34:51 GMT+12", 12),
            param("Fri Sep 23 2016 10:34:51 UTC+13", 13),
            param("Fri Sep 23 2016 10:34:51 GMT+1245 (CST)", 12.75),
            param("Fri Sep 23 2016 10:34:51 UTC+1245", 12.75),
            param("2019-07-17T12:30:00.000-03:30", -3.5),
            param("2019-07-17T12:30:00.000-02:30", -2.5),
            param("16. srpna 2021 9:59:44 SELČ", 2),
            param("16. srpna 2021 9:59:44 SEČ", 1),
            param("16. srpna 2021 9:59:44 ZEČ", 0),
            param("16. srpna 2021 9:59:44 VEČ", 2),
        ]
    )
    def test_extracting_valid_offset(self, initial_string, expected_offset):
        self.given_string(initial_string)
        self.when_offset_popped_from_string()
        self.then_offset_is(expected_offset)

    @parameterized.expand(
        [
            param("Sep 03 2014 | 4:32 pm EDT", "Sep 03 2014 | 4:32 pm "),
            param(
                "17th October, 2034 @ 01:08 am PDT", "17th October, 2034 @ 01:08 am "
            ),
            param("October 17, 2014 at 7:30 am PST", "October 17, 2014 at 7:30 am "),
            param("20 Oct 2014 13:08 CET", "20 Oct 2014 13:08 "),
            param("20 Oct 2014 13:08cet", "20 Oct 2014 13:08"),
            param("Nov 25 2014 | 10:17 pm EST", "Nov 25 2014 | 10:17 pm "),
            param(
                "17th October, 2034 @ 01:08 am +0700", "17th October, 2034 @ 01:08 am "
            ),
            param("Sep 03 2014 4:32 pm +0630", "Sep 03 2014 4:32 pm "),
        ]
    )
    def test_timezone_deleted_from_string(self, initial_string, result_string):
        self.given_string(initial_string)
        self.when_offset_popped_from_string()
        self.then_string_modified_to(result_string)

    def test_string_not_changed_if_no_timezone(self):
        self.given_string("15 May 2004")
        self.when_offset_popped_from_string()
        self.then_string_modified_to("15 May 2004")

    def given_string(self, string_):
        self.initial_string = string_

    def when_offset_popped_from_string(self):
        self.datetime_string, timezone_offset = pop_tz_offset_from_string(
            self.initial_string
        )
        if timezone_offset:
            self.timezone_offset = timezone_offset.utcoffset("")
        else:
            self.timezone_offset = timezone_offset

    def then_string_modified_to(self, expected_string):
        self.assertEqual(expected_string, self.datetime_string)

    def then_offset_is(self, expected_offset):
        delta = (
            timedelta(hours=expected_offset) if expected_offset is not None else None
        )
        self.assertEqual(delta, self.timezone_offset)


class TestLocalTZOffset(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.timezone_offset = NotImplemented

    @parameterized.expand(
        [
            param(utc="2014-08-20 4:32", local="2014-08-20 8:32", offset=+4),
            param(utc="2052-01-02 11:07", local="2052-01-02 10:07", offset=-1),
            param(utc="2013-12-31 23:59", local="2014-01-01 00:29", offset=+0.5),
            param(utc="2011-07-14 11:59", local="2011-07-13 23:59", offset=-12),
            param(utc="2014-10-18 17:41", local="2014-10-18 17:41", offset=0),
        ]
    )
    def test_timezone_offset_calculation(self, utc, local, offset):
        try:
            self.given_time(utc, local)
        except OverflowError:
            raise SkipTest("Unsupported with 32-bit time_t")
        self.when_offset_popped_from_string()
        self.then_offset_is(offset)

    def when_offset_popped_from_string(self):
        self.timezone_offset = get_local_tz_offset()

    def then_offset_is(self, expected_offset):
        delta = (
            timedelta(seconds=3600 * expected_offset)
            if expected_offset is not None
            else None
        )
        self.assertEqual(delta, self.timezone_offset)

    def given_time(self, utc_dt_string, local_dt_string):
        datetime_cls = dateparser.timezone_parser.datetime
        if not isinstance(datetime_cls, Mock):
            datetime_cls = Mock(wraps=datetime)
        utc_dt_obj = datetime.strptime(utc_dt_string, "%Y-%m-%d %H:%M").replace(
            tzinfo=dt.timezone.utc
        )
        local_dt_obj = datetime.strptime(local_dt_string, "%Y-%m-%d %H:%M")

        def _dt_now(tz=None):
            if tz == dt.timezone.utc:
                return utc_dt_obj
            return local_dt_obj

        datetime_cls.now = Mock(side_effect=_dt_now)
        self.add_patch(patch("dateparser.timezone_parser.datetime", new=datetime_cls))


class TestTimeZoneConversion(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.settings = {}
        self.parser = parse
        self.result = NotImplemented

    @parameterized.expand(
        [
            param(
                "2015-12-31 10:04 AM",
                "Asia/Karachi",
                "UTC",
                datetime(2015, 12, 31, 5, 4),
            ),
            param(
                "2015-12-30 10:04 AM",
                "Asia/Karachi",
                "+0200",
                datetime(2015, 12, 30, 7, 4),
            ),
        ]
    )
    def test_timezone_conversion(self, datestring, from_tz, to_tz, expected):
        self.given_from_timezone(from_tz)
        self.given_to_timezone(to_tz)
        self.when_date_is_parsed(datestring)
        self.then_date_is(expected)

    def given_from_timezone(self, timezone):
        self.settings["TIMEZONE"] = timezone

    def given_to_timezone(self, timezone):
        self.settings["TO_TIMEZONE"] = timezone

    def when_date_is_parsed(self, datestring):
        self.result = self.parser(datestring, settings=self.settings)

    def then_date_is(self, date):
        self.assertEqual(date, self.result)


class TestStaticTzInfo(BaseTestCase):
    def setUp(self):
        super().setUp()

    @parameterized.expand(
        [
            param(given_date=datetime(2007, 1, 18, tzinfo=timezone("UTC"))),
            param(given_date=datetime(2003, 3, 31, tzinfo=timezone("US/Arizona"))),
            param(given_date=datetime(2000, 2, 20, tzinfo=timezone("Pacific/Samoa"))),
        ]
    )
    def test_localize_raises_error_if_date_has_tzinfo(self, given_date):
        self.timezone_info = StaticTzInfo("UTC\\+00:00", timedelta(0))
        self.when_date_is_localized(given_date)
        self.then_error_was_raised(
            ValueError, ["Not naive datetime (tzinfo is already set)"]
        )

    def when_date_is_localized(self, given_date):
        try:
            self.localized_date = self.timezone_info.localize(given_date)
        except Exception as error:
            self.error = error

    def then_localized_date_is(self, expected_date, expected_tzname):
        self.assertEqual(self.localized_date.date(), expected_date.date())
        self.assertEqual(self.localized_date.tzname(), expected_tzname)


class TestIsTimezoneToken(BaseTestCase):
    """Unit tests for ``is_timezone_token``, used to keep a trailing timezone
    when ``IGNORE_SURROUNDING_TEXT`` strips edge tokens."""

    @parameterized.expand(
        [
            param(token="EST", expected=True),
            # Already-lowercased and space-padded tokens (as produced by the
            # translation pipeline) are recognized too.
            param(token="est", expected=True),
            param(token=" est", expected=True),
            param(token="cet", expected=True),
            param(token="pst", expected=True),
            param(token="utc", expected=True),
            # A longer word that merely starts with a timezone abbreviation must
            # not be treated as a timezone.
            param(token="actualisé", expected=False),
            param(token="ACTUALISÉ", expected=False),
            param(token="updated", expected=False),
            param(token="", expected=False),
            param(token="   ", expected=False),
        ]
    )
    def test_is_timezone_token(self, token, expected):
        self.assertEqual(expected, is_timezone_token(token))

    def test_anchored_match_unlike_word_is_tz(self):
        # word_is_tz prefix-matches ("ACT" of "ACTUALISÉ"); is_timezone_token is
        # anchored, so it does not — this is what keeps a noise word from
        # surviving as a timezone when edges are stripped.
        self.assertTrue(word_is_tz("ACTUALISÉ"))
        self.assertFalse(is_timezone_token("ACTUALISÉ"))


class TestTzDatabasePreference(BaseTestCase):
    """Tests for #1322: prefer the tz database for conflicting abbreviations.

    ``dateparser/timezones.py`` maps every timezone abbreviation to a single UTC
    offset, and unrelated zones often share the same letters. The table was
    scraped from Wikipedia, so a few abbreviations ended up with a meaning no tz
    database zone has: "BST" resolved to +11, although the only zone named "BST"
    today is British Summer Time at +1 (#1321).

    The rule pinned down here is that when the tz database names exactly one
    offset for an abbreviation, dateparser has to use it, and when the tz
    database names several, dateparser's existing choice is left alone.

    The tests that exercise the comparison itself run against
    ``FROZEN_TZ_DATABASE`` so that they keep testing the same logic as the tz
    database changes; the two that check dateparser's actual data are the ones
    that read the installed tz database.
    """

    # A stand-in for the tz database: "BST"/"HDT" named by one offset each,
    # "CST" by three (US Central, Cuba, China).
    FROZEN_TZ_DATABASE = {
        "BST": {3600},
        "HDT": {-32400},
        "CST": {-21600, -18000, 28800},
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from dateparser_scripts import tz_abbreviation_conflicts

        cls.checker = tz_abbreviation_conflicts
        # Sampling every zone takes a moment, so it is done once for the class.
        cls.tz_database = tz_abbreviation_conflicts.tz_database_abbreviations()

    def offset_of(self, date_string):
        _, timezone_offset = pop_tz_offset_from_string(date_string)
        self.assertIsNotNone(timezone_offset, f"no timezone found in {date_string!r}")
        return timezone_offset.utcoffset(None)

    @parameterized.expand(
        [
            # British Summer Time, the case reported in #1321.
            param("13 August 2026 10:00 BST", +1, "BST"),
            # Hawaii-Aleutian Daylight Time (America/Adak). The table used
            # -9:30, which is what Pacific/Honolulu called "HDT" back when
            # Hawaii kept -10:30; no zone has been named that since.
            param("13 August 2026 10:00 HDT", -9, "HDT"),
        ]
    )
    def test_unambiguous_abbreviation_uses_tz_database_offset(
        self, date_string, expected_offset, abbreviation
    ):
        self.assertEqual(timedelta(hours=expected_offset), self.offset_of(date_string))
        # And the tz database really does name only that one offset.
        self.assertEqual({int(expected_offset * 3600)}, self.tz_database[abbreviation])

    @parameterized.expand(
        [
            param("13 August 2026 10:00 BST", +1, "BST"),
            param("13 August 2026 10:00 HDT", -9, "HDT"),
        ]
    )
    def test_unambiguous_abbreviation_parses_end_to_end(
        self, date_string, expected_offset, abbreviation
    ):
        # The #1321 report as a user would hit it, not just at the popping layer.
        parsed = parse(date_string, settings={"RETURN_AS_TIMEZONE_AWARE": True})
        self.assertEqual(timedelta(hours=expected_offset), parsed.utcoffset())
        self.assertEqual(abbreviation, parsed.tzname())

    @parameterized.expand(
        [
            # US Central, but "CST" also names Cuba (-5) and China (+8).
            param("13 August 2026 10:00 CST", -6),
            # US Central Daylight, but "CDT" also names Cuba (-4).
            param("13 August 2026 10:00 CDT", -5),
            # Israel, but "IST" also names India (+5:30) and Ireland (+1).
            param("13 August 2026 10:00 IST", +2),
            # US Pacific, but "PST" also names the Philippines (+8).
            param("13 August 2026 10:00 PST", -8),
        ]
    )
    def test_ambiguous_abbreviation_keeps_its_offset(
        self, date_string, expected_offset
    ):
        # These keep the value dateparser has always used. The assertion below
        # holds whether or not the abbreviation stays ambiguous: what matters is
        # that the retained value is one a real zone uses, not an arbitrary one.
        self.assertEqual(timedelta(hours=expected_offset), self.offset_of(date_string))
        abbreviation = date_string.rsplit(" ", 1)[1]
        self.assertIn(int(expected_offset * 3600), self.tz_database[abbreviation])

    def test_table_agrees_with_the_tz_database(self):
        # The generalized check behind #1322: instead of asserting a fixed list
        # of abbreviations, ask the tz database about every abbreviation the two
        # tables share, so a regression on any of them is caught.
        shared = set(self.checker.static_tz_abbreviations()) & set(self.tz_database)
        # Without this, the assertion below would also pass if the comparison
        # silently stopped covering anything.
        self.assertGreater(
            len(shared), 40, f"only {len(shared)} abbreviations compared"
        )
        conflicts = self.checker.find_conflicts(tz_database=self.tz_database)
        self.assertEqual([], conflicts, f"conflicts with the tz database: {conflicts}")

    def test_report_runs_clean(self):
        # Exercises the module's entry point with its real defaults, which the
        # test above bypasses by passing the tz database in.
        self.assertEqual(0, self.checker.main())

    def test_reference_years_stay_in_settled_years(self):
        # The tz database records future daylight-saving rules as predictions
        # that change between releases, so sampling them would tie the result to
        # the installed version rather than to real usage.
        self.assertLess(max(self.checker.REFERENCE_YEARS), datetime.now().year)

    def test_pre_fix_offsets_are_reported_as_conflicts(self):
        # Reproduces the bug this change fixes, and keeps the whole-table check
        # from passing vacuously: the offsets shipped before #1322 are flagged.
        conflicts = self.checker.find_conflicts(
            static={"BST": 39600, "HDT": -34200},
            tz_database=self.FROZEN_TZ_DATABASE,
        )
        self.assertEqual(
            [
                ("BST", "unambiguous", 39600, [3600]),
                ("HDT", "unambiguous", -34200, [-32400]),
            ],
            [tuple(conflict) for conflict in conflicts],
        )

    def test_offset_no_zone_uses_is_reported_even_when_ambiguous(self):
        # "CST" has several meanings, so none of them can be preferred, but +11
        # is not one of them and is still worth reporting.
        (conflict,) = self.checker.find_conflicts(
            static={"CST": 39600}, tz_database=self.FROZEN_TZ_DATABASE
        )
        self.assertEqual("CST", conflict.abbreviation)
        self.assertEqual("unsupported", conflict.kind)
        self.assertNotIn(39600, conflict.tz_database_offsets)

    @parameterized.expand([param(-21600), param(28800)])
    def test_any_offset_a_zone_really_uses_is_accepted(self, offset):
        # Both US Central (-6) and China (+8) are legitimate readings of "CST".
        self.assertEqual(
            [],
            self.checker.find_conflicts(
                static={"CST": offset}, tz_database=self.FROZEN_TZ_DATABASE
            ),
        )

    def test_abbreviations_outside_the_reference_window_are_ignored(self):
        # dateparser keeps abbreviations no zone is named after any more, such
        # as "AHST", so historical text still parses. The tz database says
        # nothing about them, so they are skipped rather than reported.
        self.assertNotIn("AHST", self.tz_database)
        self.assertEqual(
            [],
            self.checker.find_conflicts(
                static={"AHST": -36000}, tz_database=self.FROZEN_TZ_DATABASE
            ),
        )

    def test_abbreviations_are_compared_case_insensitively(self):
        # dateparser matches abbreviations regardless of case, so the table's
        # "ChST" entry and the tz database's "ChST" are one abbreviation and
        # have to meet under the same key.
        self.assertIn("CHST", self.checker.static_tz_abbreviations())
        self.assertIn("CHST", self.tz_database)

    def test_numeric_zone_names_are_not_treated_as_abbreviations(self):
        # The tz database names zones that have no established abbreviation
        # after their offset, as in "+11" or "-0930". Those are offsets rather
        # than identities, and dateparser matches numeric offsets through its
        # separate UTC/GMT patterns, so they stay out of this comparison.
        self.assertEqual([], [name for name in self.tz_database if name[0] in "+-"])
        self.assertIn("BST", self.tz_database)

    def test_repeated_abbreviation_resolves_to_its_first_entry(self):
        # "LMT" is listed four times with four different offsets. Only the first
        # can ever match, so that is the value the comparison has to use;
        # checking against all four would hide a wrong first entry.
        self.assertEqual(
            self.checker.static_tz_abbreviations()["LMT"],
            self.offset_of("13 August 2026 10:00 LMT").total_seconds(),
        )
