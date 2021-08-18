from collections.abc import Set

from dateparser.search.text_detection import FullTextLanguageDetector
from dateparser.languages.loader import LocaleDataLoader


class SearchLanguages:
    def __init__(self):
        self.loader = LocaleDataLoader()
        self.available_language_map = self.loader.get_locale_map()
        self.language = None

    def get_current_language(self, language_shortname):
        if self.language is None or self.language.shortname != language_shortname:
            self.language = self.loader.get_locale(language_shortname)

    def translate_objects(self, language_shortname, text, settings):
        self.get_current_language(language_shortname)
        result = self.language.translate_search(text, settings=settings)
        return result

    def detect_language(self, text, languages):
        if isinstance(languages, (list, tuple, Set)):

            if all([language in self.available_language_map for language in languages]):
                languages = [
                    self.available_language_map[language] for language in languages
                ]
            else:
                unsupported_languages = set(languages) - set(
                    self.available_language_map.keys()
                )
                raise ValueError(
                    "Unknown language(s): %s"
                    % ", ".join(map(repr, unsupported_languages))
                )
        elif languages is not None:
            raise TypeError(
                "languages argument must be a list (%r given)" % type(languages)
            )

        if languages:
            self.language_detector = FullTextLanguageDetector(languages=languages)
        else:
            self.language_detector = FullTextLanguageDetector(
                list(self.available_language_map.values())
            )

        return self.language_detector._best_language(text)
