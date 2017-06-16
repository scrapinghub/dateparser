from nose_parameterized import parameterized, param
from operator import attrgetter
import six

from dateparser.languages.loader import default_language_loader
from tests import BaseTestCase

class TestLoadingWithStrictOrder(BaseTestCase):
    def setUp(self):
        super(TestLoadingWithStrictOrder, self).setUp()

    @classmethod
    def setUpClass(cls):
        cls.data_loader = default_language_loader
        cls.data_loader._data = {}

    @parameterized.expand([
        param(given_languages=['es','fr','en'], loaded_languages=['en','es','fr'],
              expected_languages=['en','es','fr']),
        param(given_languages=['ar','he'], loaded_languages=['en','ar','es','fr','he'],
              expected_languages=['ar','he']),
        param(given_languages=['tl','zh','uk'], loaded_languages=['en','ar','es','fr','he','tl','uk','zh'],
              expected_languages=['tl','uk','zh']),
        param(given_languages=['fr','zh','he','ru'], loaded_languages=['en','ar','es','fr','he','ru','tl','uk','zh'],
              expected_languages=['fr','he','ru','zh']),
        param(given_languages=['en','tl'], loaded_languages=['en','ar','es','fr','he','ru','tl','uk','zh'],
              expected_languages=['en','tl']),
        param(given_languages=['it'], loaded_languages=['en','ar','es','fr','he','it','ru','tl','uk','zh'],
              expected_languages=['it']),
    ])
    def test_loading_if_strict_order_is_True(self, given_languages, loaded_languages, expected_languages):
        self.load_data(given_languages, strict_order=True)
        self.then_languages_are_yielded_in_order(expected_languages)
        self.then_loaded_languages_are(loaded_languages)

    def load_data(self, given_languages, strict_order):
        self.language_generator = self.data_loader.get_languages(languages=given_languages, strict_order=strict_order)

    def then_loaded_languages_are(self, loaded_languages):
        six.assertCountEqual(self, loaded_languages, self.data_loader._data.keys())

    def then_languages_are_yielded_in_order(self, expected_languages):
        self.assertEqual(list(map(attrgetter('shortname'), list(self.language_generator))), expected_languages)


class TestLoadingWithoutStrictOrder(BaseTestCase):
    def setUp(self):
        super(TestLoadingWithoutStrictOrder, self).setUp()

    @classmethod
    def setUpClass(cls):
        cls.data_loader = default_language_loader
        cls.data_loader._data = {}

    @parameterized.expand([
        param(given_languages=['es','fr','en'], loaded_languages=['en','es','fr'],
              expected_languages=['en','es','fr']),
        param(given_languages=['ar','he','fr'], loaded_languages=['en','ar','es','fr','he'],
              expected_languages=['fr','ar','he']),
        param(given_languages=['bg','es','he','zh','uk'], loaded_languages=['en','ar','es','fr','he','bg','uk','zh'],
              expected_languages=['es','he','bg','uk','zh']),
        param(given_languages=['fr','zh','he','ru'], loaded_languages=['en','ar','es','fr','he','bg','uk','zh','ru'],
              expected_languages=['fr','he','zh','ru']),
        param(given_languages=['en','uk','pt','ar'], loaded_languages=['en','ar','es','fr','he','bg','uk','zh','ru','pt'],
              expected_languages=['en','ar','uk','pt']),
        param(given_languages=['it','id','bg'], loaded_languages=['en','ar','es','fr','he','bg','uk','zh','ru','pt','it','id'],
              expected_languages=['bg','id','it']),
    ])
    def test_loading_if_strict_order_is_False(self, given_languages, loaded_languages, expected_languages):
        self.load_data(given_languages, strict_order=False)
        self.then_languages_are_yielded_in_order(expected_languages)
        self.then_loaded_languages_are(loaded_languages)

    def load_data(self, given_languages, strict_order):
        self.language_generator = self.data_loader.get_languages(languages=given_languages, strict_order=strict_order)

    def then_loaded_languages_are(self, loaded_languages):
        six.assertCountEqual(self, loaded_languages, self.data_loader._data.keys())

    def then_languages_are_yielded_in_order(self, expected_languages):
        self.assertEqual(list(map(attrgetter('shortname'), list(self.language_generator))), expected_languages)
