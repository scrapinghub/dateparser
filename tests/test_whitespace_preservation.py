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
            # Single space preservation - Finnish
            param("fi", "28 maalis klo 9:37", "28 march 9:37"),
            # Double space preservation - Finnish
            param("fi", "28  maalis  klo  9:37", "28  march  9:37"),
            # Triple space preservation - Finnish
            param("fi", "28   maalis   klo   9:37", "28   march   9:37"),
            # Mixed whitespace - Finnish
            param("fi", "28  maalis klo  9:37", "28  march  9:37"),
            # More complex Finnish date with whitespace
            param(
                "fi", "tiistaina  27.  lokakuuta  2015", "tuesday  27.  october  2015"
            ),
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

    def given_bundled_language(self, shortname):
        self.language = default_loader.get_locale(shortname)

    def given_string(self, datetime_string):
        self.datetime_string = datetime_string

    def when_datetime_string_translated(self):
        self.translation = self.language.translate(
            self.datetime_string, settings=self.settings
        )

    def then_string_translated_to(self, expected_string):
        self.assertEqual(
            expected_string,
            self.translation,
            f"\nExpected: |{expected_string}|\nGot:      |{self.translation}|\n"
            f"Input:    |{self.datetime_string}|",
        )
