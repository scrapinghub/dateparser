# coding: utf-8
from dateparser.languages.loader import LanguageDataLoader
from dateparser.conf import Settings


class ExactLanguageSearch:
    def __init__(self):
        self.loader = LanguageDataLoader()
        self.language = None

    def get_current_language(self, shortname):
        if self.language is None or self.language.shortname != shortname:
            self.language = self.loader.get_language(shortname)

    def search(self, shortname, text):
        self.get_current_language(shortname)
        result = self.language.translate_search(text, settings=Settings())
        return result
