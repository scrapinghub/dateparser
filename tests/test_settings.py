import copy
import pickle
import subprocess
import sys
from datetime import datetime, timedelta, tzinfo
from pathlib import Path
from typing import Any

import pytest
from parameterized import param, parameterized

import dateparser
from dateparser import DateDataParser, PartsOfDay, parse
from dateparser.conf import Settings, SettingValidationError, apply_settings, settings
from dateparser.languages.dictionary import Dictionary
from dateparser.languages.loader import default_loader
from dateparser.search import search_dates
from dateparser_data.settings import default_parsers
from tests import BaseTestCase


def test_function(settings: object = None) -> object:
    return settings


class TimeZoneSettingsTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.given_ds: str = NotImplemented
        self.result: datetime | None = NotImplemented
        self.timezone = NotImplemented
        self.confs: Settings = NotImplemented

    @parameterized.expand(
        [
            param(
                "12 Feb 2015 10:30 PM +0100",
                datetime(2015, 2, 12, 22, 30),
                r"UTC\+01:00",
            ),
            param("12 Feb 2015 4:30 PM EST", datetime(2015, 2, 12, 16, 30), "EST"),
            param("12 Feb 2015 8:30 PM PKT", datetime(2015, 2, 12, 20, 30), "PKT"),
            param("12 Feb 2015 8:30 PM ACT", datetime(2015, 2, 12, 20, 30), "ACT"),
        ]
    )
    def test_should_return_and_assert_tz(self, ds: str, dt: datetime, tz: str) -> None:
        self.given(ds)
        self.given_configurations({})
        self.when_date_is_parsed()
        self.then_date_is_tz_aware()
        self.then_date_is(dt)
        self.then_timezone_is(tz)

    @parameterized.expand(
        [
            param("12 Feb 2015 4:30 PM EST", datetime(2015, 2, 12, 16, 30), "EST"),
            param("12 Feb 2015 8:30 PM PKT", datetime(2015, 2, 12, 20, 30), "PKT"),
            param("12 Feb 2015 8:30 PM ACT", datetime(2015, 2, 12, 20, 30), "ACT"),
            param("12 Feb 2015 8:30 PM", datetime(2015, 2, 12, 20, 30), ""),
        ]
    )
    def test_only_return_explicit_timezone(
        self, ds: str, dt: datetime, tz: str
    ) -> None:
        self.given(ds)
        self.given_configurations({})
        self.when_date_is_parsed()
        self.then_date_is(dt)
        if tz:
            self.then_date_is_tz_aware()
            self.then_timezone_is(tz)
        else:
            self.then_date_is_not_tz_aware()

    @parameterized.expand(
        [
            param(
                "12 Feb 2015 4:30 PM EST",
                datetime(2015, 2, 12, 16, 30),
            ),
            param(
                "12 Feb 2015 8:30 PM PKT",
                datetime(2015, 2, 12, 20, 30),
            ),
            param(
                "12 Feb 2015 8:30 PM ACT",
                datetime(2015, 2, 12, 20, 30),
            ),
            param(
                "12 Feb 2015 8:30 PM +0100",
                datetime(2015, 2, 12, 20, 30),
            ),
        ]
    )
    def test_should_return_naive_if_RETURN_AS_TIMEZONE_AWARE_IS_FALSE(
        self, ds: str, dt: datetime
    ) -> None:
        self.given(ds)
        self.given_configurations({"RETURN_AS_TIMEZONE_AWARE": False})
        self.when_date_is_parsed()
        self.then_date_is(dt)
        self.then_date_is_not_tz_aware()

    def then_timezone_is(self, tzname: str) -> None:
        assert self.result is not None
        assert self.result.tzinfo is not None
        self.assertEqual(self.result.tzinfo.tzname(None), tzname)

    def given(self, ds: str) -> None:
        self.given_ds = ds

    def given_configurations(self, confs: dict[str, Any]) -> None:
        if "TIMEZONE" not in confs:
            confs.update({"TIMEZONE": "local"})

        self.confs = settings.replace(**confs)

    def when_date_is_parsed(self) -> None:
        self.result = parse(self.given_ds, settings=(self.confs or {}))

    def then_date_is_tz_aware(self) -> None:
        assert self.result is not None
        self.assertIsInstance(self.result.tzinfo, tzinfo)

    def then_date_is_not_tz_aware(self) -> None:
        assert self.result is not None
        self.assertIsNone(self.result.tzinfo)

    def then_date_is(self, date: datetime) -> None:
        assert self.result is not None
        dtc = self.result.replace(tzinfo=None)
        self.assertEqual(dtc, date)


class SettingsTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.default_settings = settings

    def test_apply_settings_should_return_default_settings_when_no_settings_are_supplied_to_the_decorated_function(
        self,
    ) -> None:
        test_func = apply_settings(test_function)
        self.assertEqual(test_func(), self.default_settings)

    def test_apply_settings_should_return_non_default_settings_when_settings_are_supplied_to_the_decorated_function(
        self,
    ) -> None:
        test_func = apply_settings(test_function)
        self.assertNotEqual(
            test_func(settings={"PREFER_DATES_FROM": "past"}), self.default_settings
        )

    def test_apply_settings_should_return_default_settings_when_called_with_no_settings_after_once_called_with_settings_supplied_to_the_decorated_function(
        self,
    ) -> None:
        test_func = apply_settings(test_function)
        settings_once = test_func(settings={"PREFER_DATES_FROM": "past"})
        settings_twice = test_func()
        self.assertNotEqual(settings_once, self.default_settings)
        self.assertEqual(settings_twice, self.default_settings)

    def test_replace_keeps_the_settings_that_the_caller_set(self) -> None:
        test_func = apply_settings(test_function)
        caller_settings = test_func(settings={"DATE_ORDER": "DMY"})
        assert isinstance(caller_settings, Settings)
        replaced = caller_settings.replace(RELATIVE_BASE=datetime(2020, 12, 25))
        # A DATE_ORDER that the caller set wins over the MDY order of the locale.
        parser = DateDataParser(languages=["en"], settings=replaced)
        self.assertEqual(
            datetime(2021, 1, 2), parser.get_date_data("02/01/2021")["date_obj"]
        )

    def test_replace_does_not_count_the_settings_it_copies_as_set_by_the_caller(
        self,
    ) -> None:
        test_func = apply_settings(test_function)
        caller_settings = test_func(settings={"PREFER_DATES_FROM": "past"})
        assert isinstance(caller_settings, Settings)
        replaced = caller_settings.replace(RELATIVE_BASE=datetime(2020, 12, 25))
        # The default DATE_ORDER, MDY, gives way to the DMY order of the locale.
        parser = DateDataParser(languages=["de"], settings=replaced)
        self.assertEqual(
            datetime(2021, 1, 2), parser.get_date_data("02.01.2021")["date_obj"]
        )


class InvalidSettingsTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_error_is_raised_when_none_is_passed_in_settings(self) -> None:
        test_func = apply_settings(test_function)
        with self.assertRaisesRegex(TypeError, r"Invalid.*None\}"):
            test_func(settings={"PREFER_DATES_FROM": None})

        with self.assertRaisesRegex(TypeError, r"Invalid.*None\}"):
            test_func(settings={"TIMEZONE": None})

        with self.assertRaisesRegex(TypeError, r"Invalid.*None\}"):
            test_func(settings={"TO_TIMEZONE": None})

    def test_error_is_raised_for_invalid_type_settings(self) -> None:
        test_func = apply_settings(test_function)
        try:
            test_func(settings=["current_period", False, "current"])
        except Exception as error:
            self.error = error
            self.then_error_was_raised(
                TypeError,
                ["settings can only be either dict or instance of Settings class"],
            )

    def test_check_settings_wrong_setting_name(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError, r".* is not a valid setting"
        ):
            DateDataParser(settings={"AAAAA": "foo"})

    @parameterized.expand(
        [
            param("DATE_ORDER", 2, "YYY", "MDY"),
            param(
                "TIMEZONE", False, "", "Europe/Madrid"
            ),  # should we check valid timezones?
            param(
                "TO_TIMEZONE", True, "", "Europe/Madrid"
            ),  # should we check valid timezones?
            param("RETURN_AS_TIMEZONE_AWARE", "false", "", True),
            param("PREFER_DAY_OF_MONTH", False, "current_period", "current"),
            param("PREFER_DATES_FROM", True, "current", "current_period"),
            param("RELATIVE_BASE", "yesterday", "", datetime.now()),
            param("SKIP_TOKENS", "foo", "", ["foo"]),
            param("REQUIRE_PARTS", "day", "", ["month", "day"]),
            param("PARSERS", "absolute-time", "", ["absolute-time", "no-spaces-time"]),
            param("STRICT_PARSING", "true", "", True),
            param("RETURN_TIME_AS_PERIOD", "false", "", True),
            param("PREFER_LOCALE_DATE_ORDER", "true", "", False),
            param("STRICT_DATE_ORDER", True, "full", "none"),
            param("NORMALIZE", "true", "", True),
            param("FUZZY", "true", "", False),
            param("PREFER_LOCALE_DATE_ORDER", "false", "", True),
            param("DEFAULT_LANGUAGES", "en", "", ["en"]),
            param("USE_GIVEN_LANGUAGE_ORDER", "yes", "", True),
            param("LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD", "1", "", 0.5),
        ]
    )
    def test_check_settings(
        self, setting: str, wrong_type: object, wrong_value: str, valid_value: object
    ) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            rf'"{setting}" must be .*, not "{type(wrong_type).__name__}".',
        ):
            DateDataParser(settings={setting: wrong_type})

        if wrong_value:
            with self.assertRaisesRegex(
                SettingValidationError,
                r'"{}" is not a valid value for "{}", it should be: .*'.format(
                    str(wrong_value).replace("[", "\\[").replace("]", "\\]"), setting
                ),
            ):
                DateDataParser(settings={setting: wrong_value})

        # check that a valid value doesn't raise an error
        assert DateDataParser(settings={setting: valid_value})

    def test_check_settings_extra_check_require_parts(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            r'"REQUIRE_PARTS" setting contains invalid values: time',
        ):
            DateDataParser(settings={"REQUIRE_PARTS": ["time", "day"]})
        with self.assertRaisesRegex(
            SettingValidationError,
            r'There are repeated values in the "REQUIRE_PARTS" setting',
        ):
            DateDataParser(settings={"REQUIRE_PARTS": ["month", "day", "month"]})

    def test_check_settings_extra_check_parsers(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            r'Found unknown parsers in the "PARSERS" setting: no-spaces',
        ):
            DateDataParser(settings={"PARSERS": ["absolute-time", "no-spaces"]})

        with self.assertRaisesRegex(
            SettingValidationError,
            r'There are repeated values in the "PARSERS" setting',
        ):
            DateDataParser(
                settings={"PARSERS": ["absolute-time", "timestamp", "absolute-time"]}
            )

    def test_check_settings_extra_check_timezone_abbreviations(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            r'Found unknown timezone abbreviations in the "TIMEZONE_ABBREVIATIONS" '
            r"setting: 'XYZ'",
        ):
            DateDataParser(settings={"TIMEZONE_ABBREVIATIONS": {"XYZ": timedelta()}})

        with self.assertRaisesRegex(
            SettingValidationError,
            r"The offset of 'IST' in the \"TIMEZONE_ABBREVIATIONS\" setting must be "
            r"a timedelta, not '\+05:30'.",
        ):
            DateDataParser(settings={"TIMEZONE_ABBREVIATIONS": {"IST": "+05:30"}})

    def test_check_settings_extra_check_confidence_threshold(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            r"1.1 is not a valid value for "
            r"LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD. It can take values "
            r"between 0 and 1",
        ):
            DateDataParser(settings={"LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": 1.1})

    def test_check_settings_extra_check_default_languages(self) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            "Found invalid languages in the 'DEFAULT_LANGUAGES' setting: 'abcd'",
        ):
            DateDataParser(settings={"DEFAULT_LANGUAGES": ["abcd"]})


class StrictDateOrderSettingsTest(BaseTestCase):
    """STRICT_DATE_ORDER enforces the DATE_ORDER that the caller sets, so it
    needs one."""

    @parameterized.expand([param("year"), param("all")])
    def test_strict_date_order_requires_date_order(self, strict: str) -> None:
        with self.assertRaisesRegex(
            SettingValidationError,
            rf'"STRICT_DATE_ORDER": "{strict}" requires the "DATE_ORDER" setting',
        ):
            DateDataParser(settings={"STRICT_DATE_ORDER": strict})

        # parse() builds the parser too, whatever the date string.
        with self.assertRaises(SettingValidationError):
            parse("12/10/95", settings={"STRICT_DATE_ORDER": strict})

        # The default DATE_ORDER is a preference, but one that the caller sets
        # is enforced, even if it is the default one.
        assert DateDataParser(
            settings={"STRICT_DATE_ORDER": strict, "DATE_ORDER": "MDY"}
        )

    def test_strict_date_order_none_does_not_require_date_order(self) -> None:
        assert DateDataParser(settings={"STRICT_DATE_ORDER": "none"})
        self.assertEqual(
            datetime(1995, 12, 10),
            parse("12/10/95", settings={"STRICT_DATE_ORDER": "none"}),
        )

    @parameterized.expand([param("year"), param("all")])
    def test_strict_date_order_stays_in_force_when_a_parser_is_reused(
        self, strict: str
    ) -> None:
        parser = DateDataParser(
            settings={"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": strict}
        )
        for _ in range(2):
            self.assertIsNone(parser.get_date_data("32 DEC 10")["date_obj"])
            self.assertEqual(
                datetime(2010, 12, 31), parser.get_date_data("31 DEC 10")["date_obj"]
            )

    @parameterized.expand([param("year"), param("all")])
    def test_search_dates_does_not_check_the_rebuilt_settings(
        self, strict: str
    ) -> None:
        """Test that search_dates does not raise SettingValidationError for the
        settings that it rebuilds for the dates after the first one, which
        remember which settings the caller set."""
        text = "Opened 25/12/2020, closed 31/12/2020."
        self.assertEqual(
            [
                ("25/12/2020", datetime(2020, 12, 25)),
                ("31/12/2020", datetime(2020, 12, 31)),
            ],
            search_dates(
                text,
                languages=["en"],
                settings={"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": strict},
            ),
        )
        with self.assertRaises(SettingValidationError):
            search_dates(text, languages=["en"], settings={"STRICT_DATE_ORDER": strict})


class StrictDateOrderReplacedSettingsTest(BaseTestCase):
    """STRICT_DATE_ORDER of the settings that Settings.replace() makes."""

    texts = (
        "32 DEC 10",
        "10 DEC 32",
        "31 DEC 10",
        "12/13/10",
        "13/12/10",
        "12/31/2020",
        "31/12/2020",
    )

    @parameterized.expand([param("year"), param("all")])
    def test_replaced_settings_enforce_strict_date_order(self, strict: str) -> None:
        """Test that the settings of replace() do what the same settings of a
        dict do."""
        as_dict = {"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": strict}
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER=strict)
        for text in self.texts:
            with self.subTest(text=text):
                self.assertEqual(
                    parse(text, languages=["en"], settings=as_dict),
                    parse(text, languages=["en"], settings=replaced),
                )
        self.assertIsNone(parse("32 DEC 10", languages=["en"], settings=replaced))
        self.assertEqual(
            datetime(2010, 12, 31),
            parse("31 DEC 10", languages=["en"], settings=replaced),
        )
        parser = DateDataParser(languages=["en"], settings=replaced)
        self.assertIsNone(parser.get_date_data("32 DEC 10")["date_obj"])

    def test_replaced_settings_enforce_the_whole_order(self) -> None:
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        self.assertIsNone(parse("12/13/10", languages=["en"], settings=replaced))
        self.assertEqual(
            datetime(2010, 12, 13),
            parse("13/12/10", languages=["en"], settings=replaced),
        )

    @parameterized.expand([param("year"), param("all")])
    def test_search_dates_with_replaced_settings(self, strict: str) -> None:
        text = "Opened 12/31/2020, closed 31/12/2020, again 12/13/10."
        as_dict = {"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": strict}
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER=strict)
        self.assertEqual(
            search_dates(text, languages=["en"], settings=as_dict),
            search_dates(text, languages=["en"], settings=replaced),
        )
        if strict == "all":
            self.assertEqual(
                [("31/12/2020", datetime(2020, 12, 31))],
                search_dates(text, languages=["en"], settings=replaced),
            )

    def test_replaced_strict_settings_stay_in_force(self) -> None:
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        for later in (
            replaced.replace(TIMEZONE="UTC"),
            replaced.replace(RELATIVE_BASE=datetime(2020, 1, 1)),
            replaced.replace(RELATIVE_BASE=datetime(2020, 1, 1)).replace(
                RETURN_AS_TIMEZONE_AWARE=False
            ),
        ):
            self.assertIsNone(parse("12/13/10", languages=["en"], settings=later))
            self.assertEqual(
                datetime(2010, 12, 13),
                parse("13/12/10", languages=["en"], settings=later),
            )

    def test_replacing_strict_date_order_with_none_turns_it_off(self) -> None:
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        relaxed = replaced.replace(STRICT_DATE_ORDER="none")
        self.assertEqual(
            parse("12/13/10", languages=["en"], settings={"DATE_ORDER": "DMY"}),
            parse("12/13/10", languages=["en"], settings=relaxed),
        )
        self.assertIsNotNone(parse("12/13/10", languages=["en"], settings=relaxed))

    def test_strict_date_order_none_does_not_make_date_order_explicit(self) -> None:
        """Test that replacing with "none" is not a change, as for the dict."""
        self.assertEqual(
            datetime(2020, 5, 6),
            parse(
                "05/06/2020",
                languages=["en"],
                settings=settings.replace(STRICT_DATE_ORDER="none"),
            ),
        )
        self.assertEqual(
            datetime(2020, 5, 6),
            parse("05/06/2020", languages=["en"], settings=settings.replace()),
        )

    def test_replaced_date_order_without_strict_date_order_is_unchanged(self) -> None:
        """Test that settings of replace() that do not ask for STRICT_DATE_ORDER
        keep giving way to the order of the locale, as they do."""
        self.assertEqual(
            datetime(2020, 5, 6),
            parse(
                "05/06/2020",
                languages=["en"],
                settings=settings.replace(DATE_ORDER="DMY"),
            ),
        )
        self.assertEqual(
            datetime(2020, 6, 5),
            parse(
                "05/06/2020",
                languages=["en"],
                settings={"DATE_ORDER": "DMY"},
            ),
        )

    @parameterized.expand([param("year"), param("all")])
    def test_strict_date_order_without_a_date_order_is_rejected(
        self, strict: str
    ) -> None:
        """Test that settings of replace() that ask for STRICT_DATE_ORDER
        without a DATE_ORDER that the caller set are rejected, as the same
        settings of a dict are. A DATE_ORDER given to replace() alone gives way
        to the order of the locale, so it is not one to enforce either."""
        with self.assertRaises(SettingValidationError):
            parse("05/06/2020", settings={"STRICT_DATE_ORDER": strict})
        for replaced in (
            settings.replace(STRICT_DATE_ORDER=strict),
            settings.replace(DATE_ORDER="DMY").replace(STRICT_DATE_ORDER=strict),
        ):
            with self.subTest(replaced=replaced._mod_settings):
                with self.assertRaises(SettingValidationError):
                    parse("05/06/2020", languages=["de"], settings=replaced)
                with self.assertRaises(SettingValidationError):
                    search_dates("on 05/06/2020", languages=["de"], settings=replaced)

    def test_strict_date_order_keeps_a_date_order_already_set(self) -> None:
        """Test that a STRICT_DATE_ORDER given to replace() later enforces the
        DATE_ORDER that the caller set before, in a dict or in replace()."""
        as_dict = {"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": "all"}
        from_dict = settings.replace(
            mod_settings={"DATE_ORDER": "DMY"}, DATE_ORDER="DMY"
        )
        from_replace = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="year")
        for later in (
            from_dict.replace(STRICT_DATE_ORDER="all"),
            from_replace.replace(STRICT_DATE_ORDER="all"),
        ):
            for text in self.texts:
                with self.subTest(text=text, later=later._mod_settings):
                    self.assertEqual(
                        parse(text, languages=["en"], settings=as_dict),
                        parse(text, languages=["en"], settings=later),
                    )

    def test_replacing_strict_date_order_updates_what_the_caller_set(self) -> None:
        """Test that the STRICT_DATE_ORDER recorded as set by the caller is the
        one that the settings have, also after it is replaced with "none"."""
        strict = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        from_dict = settings.replace(
            mod_settings={"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": "all"},
            DATE_ORDER="DMY",
            STRICT_DATE_ORDER="all",
        )
        for relaxed in (
            strict.replace(STRICT_DATE_ORDER="none"),
            from_dict.replace(STRICT_DATE_ORDER="none"),
        ):
            self.assertEqual("none", relaxed.STRICT_DATE_ORDER)
            self.assertEqual("none", relaxed._mod_settings["STRICT_DATE_ORDER"])
            self.assertEqual("DMY", relaxed._mod_settings["DATE_ORDER"])
        self.assertEqual(
            "year",
            strict.replace(STRICT_DATE_ORDER="year")._mod_settings["STRICT_DATE_ORDER"],
        )

    def test_replace_does_not_accept_an_invalid_strict_date_order(self) -> None:
        with self.assertRaises(SettingValidationError):
            DateDataParser(settings=settings.replace(STRICT_DATE_ORDER="always"))

    def test_replace_does_not_accept_an_invalid_date_order_under_strict(self) -> None:
        """Test that a DATE_ORDER given to a later replace() is checked when a
        STRICT_DATE_ORDER set before enforces it, as a dict's would be."""
        strict = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        with self.assertRaises(SettingValidationError):
            DateDataParser(settings=strict.replace(DATE_ORDER="XYZ"))

    def test_replace_does_not_accept_an_invalid_date_order_set_by_a_dict(self) -> None:
        """Test that a DATE_ORDER that the caller set in a dict is checked when a
        later replace() gives another one."""
        from_dict = settings.replace(
            mod_settings={"DATE_ORDER": "DMY"}, DATE_ORDER="DMY"
        )
        with self.assertRaises(SettingValidationError):
            DateDataParser(settings=from_dict.replace(DATE_ORDER="XYZ"))

    def test_a_later_replace_of_date_order_is_recorded(self) -> None:
        strict = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        from_dict = settings.replace(
            mod_settings={"DATE_ORDER": "DMY"}, DATE_ORDER="DMY"
        )
        for replaced in (strict, from_dict):
            later = replaced.replace(DATE_ORDER="MDY")
            self.assertEqual("MDY", later._mod_settings["DATE_ORDER"])

    @parameterized.expand([param("year"), param("all")])
    def test_replaced_strict_settings_read_valid_dates_as_a_dict_does(
        self, strict: str
    ) -> None:
        """Test that asking for STRICT_DATE_ORDER also makes the DATE_ORDER win
        over the order of the locale for the dates that it allows, as it does
        for a dict (and as replace() without it does not)."""
        as_dict = {"DATE_ORDER": "DMY", "STRICT_DATE_ORDER": strict}
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER=strict)
        for text in ("05/06/2020", "05/06", "01-02-03"):
            with self.subTest(text=text):
                self.assertEqual(
                    parse(text, languages=["en"], settings=as_dict),
                    parse(text, languages=["en"], settings=replaced),
                )
        self.assertEqual(
            datetime(2020, 6, 5),
            parse("05/06/2020", languages=["en"], settings=replaced),
        )

    def test_a_later_replace_of_date_order_takes_effect(self) -> None:
        replaced = settings.replace(DATE_ORDER="DMY", STRICT_DATE_ORDER="all")
        self.assertEqual(
            datetime(2020, 5, 6),
            parse(
                "05/06/2020",
                languages=["en"],
                settings=replaced.replace(DATE_ORDER="MDY"),
            ),
        )


class ModifiedSettingsCopyTest(BaseTestCase):
    """The settings that the caller set are not the caller's dict."""

    def test_parser_keeps_the_settings_that_it_was_given(self) -> None:
        # The locale of de puts the day first, and DATE_ORDER does not, unless
        # the caller sets it.
        caller = {"TIMEZONE": "UTC"}
        parser = DateDataParser(languages=["de"], settings=caller)
        self.assertEqual(
            datetime(2020, 6, 5), parser.get_date_data("05/06/2020")["date_obj"]
        )
        caller["DATE_ORDER"] = "MDY"
        self.assertEqual(
            datetime(2020, 6, 5), parser.get_date_data("05/06/2020")["date_obj"]
        )
        self.assertEqual({"TIMEZONE": "UTC"}, dict(parser._settings._mod_settings))
        self.assertEqual(
            datetime(2020, 5, 6),
            DateDataParser(languages=["de"], settings=caller).get_date_data(
                "05/06/2020"
            )["date_obj"],
        )

    def test_settings_of_a_dict_can_be_pickled_and_copied(self) -> None:
        """Test that the copy is of a kind that pickle and deepcopy accept."""

        @apply_settings
        def get_settings(settings: Any = None) -> Settings:
            return settings  # type: ignore[no-any-return]

        given = get_settings(settings={"DATE_ORDER": "DMY"})
        for copied in (
            pickle.loads(pickle.dumps(given)),
            copy.copy(given),
            copy.deepcopy(given),
        ):
            self.assertEqual({"DATE_ORDER": "DMY"}, dict(copied._mod_settings))

    def test_settings_do_not_change_the_dict_of_the_caller(self) -> None:
        caller = {"DATE_ORDER": "DMY", "TIMEZONE": "UTC"}
        DateDataParser(languages=["en"], settings=caller)
        parse("05/06/2020", settings=caller)
        search_dates("on 05/06/2020", languages=["en"], settings=caller)
        self.assertEqual({"DATE_ORDER": "DMY", "TIMEZONE": "UTC"}, caller)


@pytest.mark.parametrize(
    ("date_string", "expected_result"),
    [
        # Note that these results are "valid" but probably they shouldn't be considered
        ("2020", datetime(1900, 1, 1, 20, 2)),
        ("333", datetime(1900, 1, 1, 3, 3, 3)),
        ("1000", datetime(1900, 1, 1, 10, 0)),
        ("100000", datetime(1900, 1, 1, 10, 0)),
    ],
)
def test_no_spaces_strict_parsing(date_string: str, expected_result: datetime) -> None:
    parser = DateDataParser(
        settings={"PARSERS": ["no-spaces-time"], "STRICT_PARSING": False}
    )
    assert parser.get_date_data(date_string)["date_obj"] == expected_result

    parser = DateDataParser(
        settings={"PARSERS": ["no-spaces-time"], "STRICT_PARSING": True}
    )
    assert parser.get_date_data(date_string)["date_obj"] is None


def detect_languages(text: str, confidence_threshold: float) -> list[str]:
    if confidence_threshold > 0.5:
        return ["en"]
    return ["fr"]


def test_confidence_threshold_setting_is_applied() -> None:
    ddp = DateDataParser(
        detect_languages_function=detect_languages,
        settings={"LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": 0.6},
    )
    assert ddp.get_date_data("21/06/2020").locale == "en"

    ddp2 = DateDataParser(
        detect_languages_function=detect_languages,
        settings={"LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": 0.4},
    )
    assert ddp2.get_date_data("21/06/2020").locale == "fr"


_DICTIONARY_CACHES = (
    Dictionary._split_regex_cache,
    Dictionary._sorted_words_cache,
    Dictionary._split_relative_regex_cache,
    Dictionary._sorted_relative_strings_cache,
    Dictionary._match_relative_regex_cache,
)


def test_per_call_settings_do_not_grow_caches() -> None:
    parse("2 days ago", settings={"RELATIVE_BASE": datetime(2000, 1, 3)})
    cache_sizes = [len(cache) for cache in _DICTIONARY_CACHES]
    for day in range(4, 10):
        base = datetime(2000, 1, day)
        result = parse(
            "2 days ago",
            settings={"RELATIVE_BASE": base, "TIMEZONE": f"UTC+0{day}:00"},
        )
        assert result == datetime(2000, 1, day - 2)
    assert [len(cache) for cache in _DICTIONARY_CACHES] == cache_sizes


def test_skip_tokens_get_their_own_cache_entry() -> None:
    locale = default_loader.get_locale("en")
    for skip_tokens, expected in (
        (["foo"], ["2000", " ", "foo"]),
        (["t"], ["2000", " foo"]),
    ):
        dictionary = locale._get_dictionary(settings.replace(SKIP_TOKENS=skip_tokens))
        assert dictionary.split("2000 foo") == expected


def test_get_key_deprecated() -> None:
    with pytest.warns(FutureWarning, match="get_key"):
        assert Settings.get_key() == "default"
    with pytest.warns(FutureWarning, match="get_key"):
        assert Settings.get_key({"DATE_ORDER": "DMY"}) == Settings.get_key(
            {"DATE_ORDER": "DMY"}
        )


class DataModuleImportTest(BaseTestCase):
    """The dateparser_data modules can be imported on their own, for example to
    reuse default_parsers, as documented."""

    def test_settings_module_can_be_the_first_import(self) -> None:
        root = Path(dateparser.__file__).resolve().parent.parent
        # A fresh interpreter: in this process dateparser is already imported.
        code = "from dateparser_data.settings import default_parsers; print(default_parsers)"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == str(default_parsers)

    def test_parts_of_day_default_is_still_set(self) -> None:
        assert isinstance(Settings().PARTS_OF_DAY, PartsOfDay)
