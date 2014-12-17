# -*- coding: utf-8 -*-
from dateparser.languages import LanguageDataLoader

default_language_loader = LanguageDataLoader()


class BaseLanguageDetector(object):
    def __init__(self, languages):
        self.languages = languages

    def iterate_applicable_languages(self, date_string, modify=False):
        languages = self.languages if modify else self.languages[:]
        for language in self._iterate_languages(date_string, languages):
            yield language

    @staticmethod
    def _iterate_languages(date_string, languages):
        while languages:
            language = languages[0]
            if language.is_applicable(date_string, strip_timezone=False):
                yield language
            elif language.is_applicable(date_string, strip_timezone=True):
                yield language

            languages.pop(0)


class AutoDetectLanguage(BaseLanguageDetector):
    def __init__(self, languages=None, allow_redetection=False):
        if languages is None:
            languages = default_language_loader.get_languages()
        super(AutoDetectLanguage, self).__init__(languages=languages)
        self.allow_redetection = allow_redetection

    def iterate_applicable_languages(self, date_string, modify=False):
        languages = self.languages if modify else self.languages[:]
        initial_languages = languages[:]
        for language in self._iterate_languages(date_string, languages):
            yield language

        if not self.allow_redetection:
            return

        # Try languages that was not tried before with this date_string
        languages = [language
                     for language in default_language_loader.get_languages()
                     if language not in initial_languages]
        if modify:
            self.languages = languages

        for language in self._iterate_languages(date_string, languages):
            yield language


class ExactLanguage(BaseLanguageDetector):
    def __init__(self, language):
        if language is None:
            raise ValueError("language cannot be None for ExactLanguage")
        super(ExactLanguage, self).__init__(languages=[language])

    def iterate_applicable_languages(self, date_string, modify=False):
        for language in super(ExactLanguage, self).iterate_applicable_languages(date_string, modify=False):
            yield language
