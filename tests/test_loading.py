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


class TestLanguageDataLoader(BaseTestCase):
    def setUp(self):
        super(TestLanguageDataLoader, self).setUp()
        self.data_loader = default_language_loader
        self.data_loader._data = {}

    @parameterized.expand([
        param(given_languages=['he','pt','en','es','uk']),
        param(given_languages=['zh','uk','hi','es']),
        param(given_languages=['ar','it','pt','uk']),
        param(given_languages=['sv','ja','ar','fr','zh']),
    ])
    def test_loading_with_given_order_with_strict_order(self, given_languages):
        self.load_data(given_languages, strict_order=True, use_given_order=True)
        self.then_languages_are_yielded_in_order(given_languages)

    @parameterized.expand([
        param(given_languages=['he','pt','id','zh'], stored_languages=['en','es','zh'],
        expected_languages=['zh','he','pt','id']),
        param(given_languages=['ar','it','uk','da'], stored_languages=['en','it','da','fr'],
        expected_languages=['it','da','ar','uk']),
        param(given_languages=['hi','fr','ja','ka'], stored_languages=['ja','es','hi','sv'],
        expected_languages=['hi','ja','fr','ka']),
    ])
    def test_loading_with_given_order_without_strict_order(self, given_languages, stored_languages, expected_languages):
        self.data_loader._data = self.data_loader.get_language_map(languages=stored_languages)
        self.load_data(given_languages, strict_order=False, use_given_order=True)
        self.then_languages_are_yielded_in_order(expected_languages)

    @parameterized.expand([
        param(given_languages=['he','id','sv','ja']),
        param(given_languages=['pt','ar','fr','es']),
        param(given_languages=['bg','fi','cs']),
    ])
    def test_get_language_map_with_given_order(self, given_languages):
        self.given_language_map(given_languages=given_languages, use_given_order=True)
        self.then_language_map_in_order(given_languages)

    @parameterized.expand([
        param(given_languages=['cs','vi','ru','nl'], expected_languages=['cs','nl','ru','vi']),
        param(given_languages=['uk','sv','hu','de'], expected_languages=['de','hu','sv','uk']),
        param(given_languages=['da','th','ka','fa'], expected_languages=['da','fa','ka','th']),
    ])
    def test_get_language_map_without_given_order(self, given_languages, expected_languages):
        self.given_language_map(given_languages=given_languages, use_given_order=False)
        self.then_language_map_in_order(expected_languages)

    def load_data(self, given_languages, strict_order, use_given_order):
        self.language_generator = self.data_loader.get_languages(languages=given_languages, strict_order=strict_order,
        use_given_order=use_given_order)

    def given_language_map(self, given_languages, use_given_order):
        self.language_map = self.data_loader.get_language_map(languages=given_languages, use_given_order=use_given_order)

    def then_languages_are_yielded_in_order(self, expected_languages):
        self.assertEqual(list(map(attrgetter('shortname'), list(self.language_generator))), expected_languages)

    def then_language_map_in_order(self, expected_languages):
        self.assertEqual(list(self.language_map.keys()), expected_languages)
