from datetime import date, datetime, timedelta

from parameterized import param, parameterized
from pytz import utc

import dateparser
from dateparser.search import search_dates
from tests import BaseTestCase


class TestParseFunction(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.result = NotImplemented

    @parameterized.expand(
        [
            param(date_string="24 de Janeiro de 2014", expected_date=date(2014, 1, 24)),
            param(date_string="2 de Enero de 2013", expected_date=date(2013, 1, 2)),
            param(date_string="January 25, 2014", expected_date=date(2014, 1, 25)),
        ]
    )
    def test_parse_dates_in_different_languages(self, date_string, expected_date):
        self.when_date_is_parsed_with_defaults(date_string)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand(
        [
            param(
                date_string="May 5, 2000 13:00",
                expected_date=datetime(2000, 5, 5, 13, 0),
            ),
            param(
                date_string="August 8, 2018 5 PM",
                expected_date=datetime(2018, 8, 8, 17, 0),
            ),
            param(
                date_string="February 26, 1981 5 am UTC",
                expected_date=datetime(1981, 2, 26, 5, 0, tzinfo=utc),
            ),
        ]
    )
    def test_parse_dates_with_specific_time(self, date_string, expected_date):
        self.when_date_is_parsed_with_defaults(date_string)
        self.then_parsed_date_and_time_is(expected_date)

    @parameterized.expand(
        [
            param(
                date_string="May 5, 2000 13:00",
                expected_date=datetime(2000, 5, 5, 13, 0),
                relative=datetime(2000, 1, 1, 0, 0, tzinfo=utc),
            ),
            param(
                date_string="August 8, 2018 5 PM",
                expected_date=datetime(2018, 8, 8, 17, 0),
                relative=datetime(1900, 5, 5, 0, 0, tzinfo=utc),
            ),
            param(
                date_string="February 26, 1981 5 am UTC",
                expected_date=datetime(1981, 2, 26, 5, 0, tzinfo=utc),
                relative=datetime(1981, 2, 26, 5, 0, tzinfo=utc),
            ),
        ]
    )
    def test_parse_dates_with_specific_time_and_settings(
        self, date_string, expected_date, relative
    ):
        self.when_date_is_parsed_with_settings(
            date_string, settings={"RELATIVE_BASE": relative}
        )
        self.then_parsed_date_and_time_is(expected_date)

    @parameterized.expand(
        [
            param(
                date_string="24 de Janeiro de 2014",
                languages=["pt"],
                expected_date=date(2014, 1, 24),
            ),
        ]
    )
    def test_dates_which_match_languages_are_parsed(
        self, date_string, languages, expected_date
    ):
        self.when_date_is_parsed(date_string, languages=languages)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand(
        [
            param(date_string="January 24, 2014", languages=["pt"]),
        ]
    )
    def test_dates_which_do_not_match_languages_are_not_parsed(
        self, date_string, languages
    ):
        self.when_date_is_parsed(date_string, languages=languages)
        self.then_date_was_not_parsed()

    @parameterized.expand(
        [
            param(
                date_string="24 de Janeiro de 2014",
                locales=["pt-TL"],
                expected_date=date(2014, 1, 24),
            ),
        ]
    )
    def test_dates_which_match_locales_are_parsed(
        self, date_string, locales, expected_date
    ):
        self.when_date_is_parsed(date_string, locales=locales)
        self.then_parsed_date_is(expected_date)

    @parameterized.expand(
        [
            param(date_string="6 yar 2019", locales=["ff-CM"]),
            param(date_string="6 yar 2019", locales=["ff-GN"]),
            param(date_string="6 yar 2019", locales=["ff-MR"]),
        ]
    )
    def test_locales_dropped_in_cldr_44_remain_supported(self, date_string, locales):
        # ff-CM/ff-GN/ff-MR were standalone locales up to CLDR 31 but were dropped in
        # CLDR 44 (regional data moved under ff-Latn). They remain valid locale codes
        # and resolve to the base `ff` data, so existing callers keep working.
        self.when_date_is_parsed(date_string, locales=locales)
        self.then_parsed_date_is(date(2019, 10, 6))

    @parameterized.expand(
        [
            param(
                date_string="0:4",
                locales=["fr-PF"],
                languages=["en"],
                region="",
                date_formats=["%a", "%a", "%a", "%a"],
                expected_date=datetime(1969, 1, 31, 13, 4),
            )
        ]
    )
    def test_dates_parse_utc_offset_does_not_throw(
        self, date_string, locales, languages, region, date_formats, expected_date
    ):
        """
        Bug discovered by OSSFuzz that caused an exception in pytz to halt parsing
        Regression test to ensure that this is not reintroduced
        """
        self.when_date_is_parsed_with_args_and_settings(
            date_string,
            languages=languages,
            locales=locales,
            region=region,
            date_formats=date_formats,
            settings={
                "CACHE_SIZE_LIMIT": 1000,
                "DATE_ORDER": "YDM",
                "DEFAULT_LANGUAGES": [
                    "mzn",
                    "as",
                    "af",
                    "fur",
                    "sr-Cyrl",
                    "kw",
                    "ne",
                    "en",
                    "vi",
                    "teo",
                    "sr",
                    "cgg",
                ],
                "LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": 0.18823535008398845,
                "NORMALIZE": True,
                "PARSERS": ["custom-formats", "absolute-time"],
                "PREFER_DATES_FROM": "past",
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_LOCALE_DATE_ORDER": True,
                "PREFER_MONTH_OF_YEAR": "current",
                "RELATIVE_BASE": datetime(
                    year=1970, month=1, day=1, hour=0, minute=0, second=0
                ),
                "REQUIRE_PARTS": [],
                "RETURN_AS_TIMEZONE_AWARE": False,
                "RETURN_TIME_AS_PERIOD": False,
                "SKIP_TOKENS": [],
                "STRICT_PARSING": False,
                "TIMEZONE": "America/Hermosillo",
                "TO_TIMEZONE": "Asia/Almaty",
            },
        )
        self.then_parsed_date_and_time_is(expected_date)

    @parameterized.expand(
        [
            param(date_string="January 24, 2014", locales=["pt-AO"]),
        ]
    )
    def test_dates_which_do_not_match_locales_are_not_parsed(
        self, date_string, locales
    ):
        self.when_date_is_parsed(date_string, locales=locales)
        self.then_date_was_not_parsed()

    @parameterized.expand(
        [
            param(date_string="Oct-23", expected_date=datetime(2023, 10, 1, 0, 0)),
            param(date_string="May-23", expected_date=datetime(2023, 5, 1, 0, 0)),
        ]
    )
    def test_require_parts_month_year_parses_month_year(
        self, date_string, expected_date
    ):
        # Regression: when year is required, Mon-YY should be interpreted as month-year.
        base = datetime(2050, 1, 1, 0, 0)
        self.when_date_is_parsed_with_settings(
            date_string,
            settings={
                "RELATIVE_BASE": base,
                "PREFER_DAY_OF_MONTH": "first",
                "PREFER_DATES_FROM": "past",
                "REQUIRE_PARTS": ["month", "year"],
            },
        )
        self.then_parsed_date_and_time_is(expected_date)

    def test_require_parts_does_not_override_explicit_date_order(self):
        # Explicit DATE_ORDER must be respected.
        base = datetime(2050, 1, 1, 0, 0)
        self.when_date_is_parsed_with_settings(
            "Oct-23",
            settings={
                "RELATIVE_BASE": base,
                "REQUIRE_PARTS": ["month", "year"],
                "DATE_ORDER": "MDY",
            },
        )
        self.then_date_was_not_parsed()

    def test_require_parts_month_day_parses_month_day(self):
        # If day is required, Mon-XX should remain month-day.
        base = datetime(2000, 1, 1, 0, 0)
        self.when_date_is_parsed_with_settings(
            "Oct-23",
            settings={
                "RELATIVE_BASE": base,
                "REQUIRE_PARTS": ["month", "day"],
            },
        )
        self.then_parsed_date_and_time_is(datetime(2000, 10, 23, 0, 0))

    def when_date_is_parsed_with_defaults(self, date_string):
        self.result = dateparser.parse(date_string)

    def when_date_is_parsed(self, date_string, languages=None, locales=None):
        self.result = dateparser.parse(
            date_string, languages=languages, locales=locales
        )

    def when_date_is_parsed_with_settings(self, date_string, settings=None):
        self.result = dateparser.parse(date_string, settings=settings)

    def when_date_is_parsed_with_args_and_settings(
        self,
        date_string,
        languages=None,
        locales=None,
        region=None,
        date_formats=None,
        settings=None,
    ):
        self.result = dateparser.parse(
            date_string,
            languages=languages,
            locales=locales,
            region=region,
            date_formats=date_formats,
            settings=settings,
        )

    def then_parsed_date_is(self, expected_date):
        self.assertEqual(
            self.result, datetime.combine(expected_date, datetime.min.time())
        )

    def then_parsed_date_and_time_is(self, expected_date):
        self.assertEqual(self.result, expected_date)

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result)


class TestIgnoreSurroundingTextSetting(BaseTestCase):
    """Tests for the opt-in ``IGNORE_SURROUNDING_TEXT`` setting (issue #518)."""

    def setUp(self):
        super().setUp()
        self.result = NotImplemented

    @parameterized.expand(
        [
            # Issue #518: dates wrapped in harmless extra text.
            param(
                date_string="Actualisé le 17 avril 2019",
                languages=["fr"],
                expected_datetime=datetime(2019, 4, 17),
            ),
            param(
                date_string="Publié le 16 avril 2019",
                languages=["fr"],
                expected_datetime=datetime(2019, 4, 16),
            ),
            # The behavior is not French-specific.
            param(
                date_string="Published on 16 April 2019",
                languages=["en"],
                expected_datetime=datetime(2019, 4, 16),
            ),
            # Purely numeric dates do not need a month name to survive.
            param(
                date_string="published 2019-04-16 ok",
                languages=["en"],
                expected_datetime=datetime(2019, 4, 16),
            ),
            param(
                date_string="xx 16/04/2019 yy",
                languages=["en"],
                expected_datetime=datetime(2019, 4, 16),
            ),
            # No language hint is needed: locales are tried as usual.
            param(
                date_string="Actualisé le 17 avril 2019",
                languages=None,
                expected_datetime=datetime(2019, 4, 17),
            ),
            # Strings that parse as a whole are parsed exactly as before.
            param(
                date_string="le 17 avril 2019",
                languages=["fr"],
                expected_datetime=datetime(2019, 4, 17),
            ),
            param(
                date_string="17 avril 2019",
                languages=["fr"],
                expected_datetime=datetime(2019, 4, 17),
            ),
        ]
    )
    def test_dates_with_surrounding_text_are_parsed(
        self, date_string, languages, expected_datetime
    ):
        self.when_date_is_parsed(
            date_string,
            languages=languages,
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_parsed_datetime_is(expected_datetime)

    @parameterized.expand(
        [
            param(date_string="Actualisé le 17 avril 2019", languages=["fr"]),
            param(date_string="Publié le 16 avril 2019", languages=["fr"]),
            param(date_string="Published on 16 April 2019", languages=["en"]),
        ]
    )
    def test_dates_with_surrounding_text_are_not_parsed_by_default(
        self, date_string, languages
    ):
        self.when_date_is_parsed(date_string, languages=languages)
        self.then_date_was_not_parsed()

    @parameterized.expand(
        [
            # An unrecognized word inside the date still prevents parsing.
            param(date_string="17 foobar avril 2019", languages=["fr"]),
            # A string without any date content is still not parsed.
            param(date_string="hello world", languages=["en"]),
        ]
    )
    def test_non_dates_are_not_parsed_even_when_enabled(self, date_string, languages):
        self.when_date_is_parsed(
            date_string,
            languages=languages,
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_date_was_not_parsed()

    def test_surrounding_text_ignored_with_locales_argument(self):
        self.when_date_is_parsed(
            "Actualisé le 17 avril 2019",
            locales=["fr-CA"],
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 17))

    def test_surrounding_text_ignored_with_region_argument(self):
        self.when_date_is_parsed(
            "Actualisé le 17 avril 2019",
            languages=["fr"],
            region="CA",
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 17))

    def test_surrounding_text_ignored_with_default_languages_setting(self):
        self.when_date_is_parsed(
            "Actualisé le 17 avril 2019",
            settings={"IGNORE_SURROUNDING_TEXT": True, "DEFAULT_LANGUAGES": ["fr"]},
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 17))

    def test_surrounding_text_ignored_with_detected_language(self):
        self.when_date_is_parsed(
            "Actualisé le 17 avril 2019",
            detect_languages_function=lambda text, confidence_threshold: ["fr"],
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 17))

    def test_surrounding_text_ignored_with_date_formats(self):
        self.when_date_is_parsed(
            "Published on 16/04/2019",
            date_formats=["%d/%m/%Y"],
            languages=["en"],
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 16))

    def test_relative_date_with_surrounding_text(self):
        self.when_date_is_parsed(
            "asdf 3 hours ago asdf",
            languages=["en"],
            settings={
                "IGNORE_SURROUNDING_TEXT": True,
                "RELATIVE_BASE": datetime(2019, 4, 17, 12, 0),
            },
        )
        self.then_parsed_datetime_is(datetime(2019, 4, 17, 9, 0))

    def test_strict_parsing_rejects_incomplete_remainder(self):
        # The remainder is parsed as if it were the whole input, so settings
        # such as STRICT_PARSING apply to it as usual.
        self.when_date_is_parsed(
            "Page 3",
            languages=["en"],
            settings={"IGNORE_SURROUNDING_TEXT": True, "STRICT_PARSING": True},
        )
        self.then_date_was_not_parsed()

    def test_surrounding_text_can_turn_non_dates_into_dates(self):
        # Documented caveat: with the setting enabled, a string that merely
        # contains date-like words produces a date.
        self.when_date_is_parsed(
            "Chapter 12 March of the Penguins",
            languages=["en"],
            settings={
                "IGNORE_SURROUNDING_TEXT": True,
                "RELATIVE_BASE": datetime(2026, 7, 27),
            },
        )
        self.then_parsed_datetime_is(datetime(2026, 3, 12))

    def test_search_dates_is_not_affected_by_default(self):
        # search_dates keeps relying on the strict behavior of get_date_data.
        self.result = search_dates("Actualisé le 17 avril 2019", languages=["fr"])
        self.assertEqual([("le 17 avril 2019", datetime(2019, 4, 17))], self.result)

    def test_trailing_timezone_is_preserved(self):
        # A recognized timezone at the trailing edge must not be discarded with
        # the surrounding text: wrapping a date in extra text yields the same
        # instant as parsing the bare date, timezone included.
        settings = {"IGNORE_SURROUNDING_TEXT": True, "RETURN_AS_TIMEZONE_AWARE": True}
        wrapped = dateparser.parse(
            "Updated 23 March 2000 1:21 PM EST", languages=["en"], settings=settings
        )
        unwrapped = dateparser.parse(
            "23 March 2000 1:21 PM EST",
            languages=["en"],
            settings={"RETURN_AS_TIMEZONE_AWARE": True},
        )
        self.assertEqual(timedelta(hours=-5), wrapped.utcoffset())
        self.assertEqual(unwrapped, wrapped)

    @parameterized.expand(
        [
            # Abbreviations that are not dictionary words, so they are kept via
            # is_timezone_token rather than the plain known-word branch. Their
            # names and offsets are chosen not to coincide with a plausible
            # local timezone (in particular not UTC or CET), so a reversion of
            # the trailing-tz exception is caught on any machine rather than
            # only under a non-local timezone.
            param(
                wrapped="Updated 23 March 2000 1:21 PM PST",
                bare="23 March 2000 1:21 PM PST",
                tzname="PST",
                utcoffset=timedelta(hours=-8),
            ),
            param(
                wrapped="Updated 23 March 2000 1:21 PM JST",
                bare="23 March 2000 1:21 PM JST",
                tzname="JST",
                utcoffset=timedelta(hours=9),
            ),
        ]
    )
    def test_more_trailing_timezones_are_preserved(
        self, wrapped, bare, tzname, utcoffset
    ):
        # Like test_trailing_timezone_is_preserved, for further abbreviations:
        # wrapping the date in extra text yields the same tz-aware instant as
        # parsing the bare date. The timezone *name* is asserted (not only the
        # offset) so the test cannot pass by the dropped timezone happening to
        # match the machine's local offset.
        settings = {"IGNORE_SURROUNDING_TEXT": True, "RETURN_AS_TIMEZONE_AWARE": True}
        wrapped_result = dateparser.parse(wrapped, languages=["en"], settings=settings)
        bare_result = dateparser.parse(
            bare, languages=["en"], settings={"RETURN_AS_TIMEZONE_AWARE": True}
        )
        self.assertEqual(tzname, wrapped_result.tzname())
        self.assertEqual(utcoffset, wrapped_result.utcoffset())
        self.assertEqual(bare_result, wrapped_result)

    def test_parenthesized_trailing_timezone_is_applied(self):
        # A parenthesized trailing timezone is applied end to end. GMT is a
        # dictionary token, so the parentheses are split off and it is kept via
        # the ordinary known-word branch, not via is_timezone_token (which the
        # PST/JST cases above exercise). A parenthesized abbreviation that is
        # *not* a dictionary word stays glued to its parentheses and is dropped
        # like any other unrecognized edge token, so GMT is used here.
        settings = {"IGNORE_SURROUNDING_TEXT": True, "RETURN_AS_TIMEZONE_AWARE": True}
        wrapped = dateparser.parse(
            "Last updated: 12 March 2019 at 10:30 (GMT)",
            languages=["en"],
            settings=settings,
        )
        bare = dateparser.parse(
            "12 March 2019 at 10:30 (GMT)",
            languages=["en"],
            settings={"RETURN_AS_TIMEZONE_AWARE": True},
        )
        self.assertEqual("GMT", wrapped.tzname())
        self.assertEqual(timedelta(0), wrapped.utcoffset())
        self.assertEqual(bare, wrapped)

    def test_only_trailing_timezone_is_preserved(self):
        # tz-recognition when stripping edge tokens is deliberately applied to
        # the trailing edge only: a timezone that follows the date is kept and
        # applied, while the same abbreviation before the date is treated as
        # ordinary surrounding text and dropped.
        settings = {"IGNORE_SURROUNDING_TEXT": True, "RETURN_AS_TIMEZONE_AWARE": True}
        trailing = dateparser.parse(
            "23 March 2000 1:21 PM EST", languages=["en"], settings=settings
        )
        leading = dateparser.parse(
            "EST 23 March 2000 1:21 PM", languages=["en"], settings=settings
        )
        without_tz = dateparser.parse(
            "23 March 2000 1:21 PM",
            languages=["en"],
            settings={"RETURN_AS_TIMEZONE_AWARE": True},
        )
        # Trailing EST is applied...
        self.assertEqual(timedelta(hours=-5), trailing.utcoffset())
        # ...leading EST is not: the result matches the same string with no
        # timezone at all, and does not carry the EST offset.
        self.assertEqual(without_tz, leading)
        self.assertNotEqual(trailing, leading)

    def test_trailing_timezone_followed_by_more_text_is_dropped(self):
        # Known limitation: a trailing timezone is kept only when it is the
        # final token. If unrecognized text follows it, the tokenizer merges
        # the two, so the timezone is stripped together with that text and its
        # offset is not applied (use search_dates for such input). The date is
        # still parsed -- only the timezone is lost.
        settings = {"IGNORE_SURROUNDING_TEXT": True, "RETURN_AS_TIMEZONE_AWARE": True}
        result = dateparser.parse(
            "Updated 23 March 2000 1:21 PM EST reportedly",
            languages=["en"],
            settings=settings,
        )
        self.assertEqual(datetime(2000, 3, 23, 13, 21), result.replace(tzinfo=None))
        self.assertNotEqual(timedelta(hours=-5), result.utcoffset())

    def test_leading_numeric_noise_is_not_ignored(self):
        # Documented limitation: stripping stops at the first recognized token,
        # and a number counts as recognized, so leading text that contains a
        # number of its own blocks parsing. search_dates covers this shape.
        self.when_date_is_parsed(
            "invoice 12345 paid on 3 March 2019",
            languages=["en"],
            settings={"IGNORE_SURROUNDING_TEXT": True},
        )
        self.then_date_was_not_parsed()

    def when_date_is_parsed(self, date_string, **kwargs):
        self.result = dateparser.parse(date_string, **kwargs)

    def then_parsed_datetime_is(self, expected_datetime):
        self.assertEqual(expected_datetime, self.result)

    def then_date_was_not_parsed(self):
        self.assertIsNone(self.result)
