"""
Tests for issue #1302: Whitespace preservation during translation
"""

from parameterized import param, parameterized

from dateparser.conf import settings
from dateparser.languages import default_loader
from tests import BaseTestCase


class TestWhitespacePreservation(BaseTestCase):
    """
    Tests to ensure that whitespace is preserved exactly when translating
    date strings, even when tokens are removed from the skip list (e.g., "klo" in Finnish).

    Issue #1302: Extra whitespace handling during date translation
    """

    def setUp(self):
        super().setUp()
        self.language = NotImplemented
        self.datetime_string = NotImplemented
        self.translation = NotImplemented
        self.settings = settings

    @parameterized.expand(
        [
            # Finnish: "klo" is a skip word
            param("fi", "28 maalis klo 9:37", "28 march 9:37"),
            param("fi", "28  maalis  klo  9:37", "28  march  9:37"),
            param("fi", "28   maalis   klo   9:37", "28   march   9:37"),
            param("fi", "28  maalis klo  9:37", "28  march  9:37"),
            param(
                "fi", "tiistaina  27.  lokakuuta  2015", "tuesday  27.  october  2015"
            ),
            # Czech: "v" translates to "in", then cleared by _clear_future_words
            param("cs", "22. prosinec 2014 v 2:38", "22. december 2014 2:38"),
            param("cs", "22.  prosinec  2014  v  2:38", "22.  december  2014  2:38"),
            # Polish: "o" is a skip word
            param("pl", "4 stycznia o 13:50", "4 january 13:50"),
            param("pl", "29 listopada 2014 o 08:40", "29 november 2014 08:40"),
            # Russian: "в" is a skip word
            param("ru", "5 августа 2014 г. в 12:00", "5 august 2014 year. 12:00"),
            # Ukrainian: "о"/"об" are skip words
            param("uk", "30 листопада 2013 о 04:27", "30 november 2013 04:27"),
            # Croatian: "u" translates to "in", then cleared
            param("hr", "13. svibanj 2022. u 14:34", "13. may 2022. 14:34"),
        ]
    )
    def test_whitespace_preservation_during_translation(
        self, shortname, datetime_string, expected_translation
    ):
        """Test that exact whitespace is preserved when translating date strings."""
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated()
        self.then_string_translated_to(expected_translation)

    @parameterized.expand(
        [
            # Finnish: keep_formatting=True
            param("fi", "28 maalis klo 9:37", "28 march 9:37"),
            param("fi", "28  maalis  klo  9:37", "28  march  9:37"),
            param("fi", "28   maalis   klo   9:37", "28   march   9:37"),
            # Czech: keep_formatting=True
            param("cs", "22. prosinec 2014 v 2:38", "22. december 2014 2:38"),
            # Polish: keep_formatting=True
            param("pl", "4 stycznia o 13:50", "4 january 13:50"),
        ]
    )
    def test_whitespace_preservation_keep_formatting(
        self, shortname, datetime_string, expected_translation
    ):
        """Test whitespace preservation with keep_formatting=True."""
        self.given_bundled_language(shortname)
        self.given_string(datetime_string)
        self.when_datetime_string_translated_keep_formatting()
        self.then_string_translated_to(expected_translation)

    def given_bundled_language(self, shortname):
        self.language = default_loader.get_locale(shortname)

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(
            self.datetime_string, settings=self.settings
        )

    def when_datetime_string_translated_keep_formatting(self):
        self.translation = self.language.translate(
            self.datetime_string, keep_formatting=True, settings=self.settings
        )

    def then_string_translated_to(self, expected_string):
        self.assertEqual(
            expected_string,
            self.translation,
            f"\nExpected: |{expected_string}|\nGot:      |{self.translation}|\n"
            f"Input:    |{self.datetime_string}|",
        )
