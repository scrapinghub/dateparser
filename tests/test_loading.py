from nose_parameterized import parameterized, param
from dateparser.languages.loader import default_language_loader
from tests import BaseTestCase

class TestLanguageDataLoader(BaseTestCase):
    def setUp(self):
        super(TestLanguageDataLoader, self).setUp()

    @classmethod
    def setUpClass(cls):
        cls.data_loader = default_language_loader
        cls.data_loader._data = {}

    @parameterized.expand([
        param(languages=['es','fr','en'], loaded_languages=['en','es','fr'],
              returned_languages=['en','es','fr']),
        param(languages=['ar','he'], loaded_languages=['en','ar','es','fr','he'],
              returned_languages=['ar','he']),
        param(languages=['tl','zh','uk'], loaded_languages=['en','ar','es','fr','he','tl','uk','zh'],
              returned_languages=['tl','uk','zh']),
        param(languages=['fr','zh','he','ru'], loaded_languages=['en','ar','es','fr','he','ru','tl','uk','zh'],
              returned_languages=['fr','he','ru','zh']),
        param(languages=['en','tl'], loaded_languages=['en','ar','es','fr','he','ru','tl','uk','zh'],
              returned_languages=['en','tl']),
        param(languages=['it'], loaded_languages=['en','ar','es','fr','he','it','ru','tl','uk','zh'],
              returned_languages=['it']),
    ])
    def test_loading(self, languages, loaded_languages, returned_languages):
        self.load_data(languages)
        self.then_loaded_languages_are(loaded_languages)
        self.then_returned_languages_are(returned_languages)

    def load_data(self, languages):
        self.returned_languages = self.data_loader._load_data(languages=languages)

    def then_loaded_languages_are(self, loaded_languages):
        self.assertEqual(set(loaded_languages),set(self.data_loader._data.keys()))

    def then_returned_languages_are(self, returned_languages):
        self.assertEqual(list(self.returned_languages.keys()), returned_languages)
