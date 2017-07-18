# coding: utf-8
from dateparser.languages.loader import LanguageDataLoader
from dateparser.conf import Settings
from dateparser import parse
import datetime


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

    def parse_found_objects(self, language, to_parse, original, settings):
        parsed = []
        substrings = []
        for i, item in enumerate(to_parse):
            parsed_item = parse(item.replace('ngày', ''), languages=[language], settings=settings)
            if parsed_item:
                parsed.append(parsed_item)
                substrings.append(original[i])
        return parsed, substrings

    def search_parse(self, shortname, text, settings=None):
        translated, original = self.search(shortname, text)
        if shortname not in ['vi', 'hu']:
            parsed, substrings = self.parse_found_objects(language='en', to_parse=translated,
                                                          original=original, settings=settings)
        else:
            parsed, substrings = self.parse_found_objects(language=shortname, to_parse=original,
                                                          original=original, settings=settings)
        return list(zip(substrings, parsed))
