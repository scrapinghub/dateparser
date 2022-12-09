from collections.abc import Set

from dateparser.search.text_detection import FullTextLanguageDetector
from dateparser.languages.loader import LocaleDataLoader
from dateparser.custom_language_detection.language_mapping import map_languages


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

    def detect_language(self, text, languages, settings=None, detect_languages_function=None):
        if detect_languages_function and not languages:
            detected_languages = detect_languages_function(
                text, confidence_threshold=settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD
            )
            detected_languages = map_languages(detected_languages) or settings.DEFAULT_LANGUAGES
            return detected_languages[0] if detected_languages else None

        if isinstance(languages, (list, tuple, Set)):
            if all([language in self.available_language_map for language in languages]):
                languages = [self.available_language_map[language] for language in languages]
            else:
                unsupported_languages = set(languages) - set(self.available_language_map.keys())
                raise ValueError("Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
        elif languages is not None:
            raise TypeError("languages argument must be a list (%r given)" % type(languages))

        if languages:
            self.language_detector = FullTextLanguageDetector(languages=languages)
        else:
            self.language_detector = FullTextLanguageDetector(list(self.available_language_map.values()))

        detected_language = self.language_detector._best_language(text) or (
            settings.DEFAULT_LANGUAGES[0] if settings.DEFAULT_LANGUAGES else None
        )
        return detected_language
