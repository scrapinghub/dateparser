# -*- coding: utf-8 -*-


class LanguageDetector(object):
    def __init__(self, try_previous_languages=False):
        self.try_previous_languages = try_previous_languages

    def iterate_applicable_languages(self, date_string, language_generator,
                                     previous_languages, settings):
        if self.try_previous_languages:
            for language in self._filter_languages(date_string, previous_languages,
                                                   settings=settings):
                yield language

        for language in self._filter_languages(date_string, language_generator,
                                               settings=settings):
            yield language

    def _filter_languages(self, date_string, languages, settings=None):
        for language in languages:
            if language.is_applicable(date_string, strip_timezone=False, settings=settings):
                yield language
            elif language.is_applicable(date_string, strip_timezone=True, settings=settings):
                yield language
