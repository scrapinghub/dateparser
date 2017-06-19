# -*- coding: utf-8 -*-
from pkgutil import get_data
from collections import OrderedDict
from ruamel.yaml.loader import SafeLoader

import six

from .language import Language


class LanguageDataLoader(object):
    _data = {}

    def __init__(self):
        self.base_data = SafeLoader(get_data('data', 'languages.yaml')).get_data()
        self.language_order = self.base_data.pop('languageorder')

    def get_language_map(self, languages=None, use_given_order=False):
        return OrderedDict(self._load_data(languages=languages, strict_order=True,
                            use_given_order=use_given_order))

    def get_languages(self, languages=None, strict_order=False, use_given_order=False):
        for shortname, language in self._load_data(languages = languages,
        strict_order=strict_order, use_given_order=use_given_order):
            yield language

    def get_language(self, shortname):
        return list(self.get_languages(languages = [shortname]))[0]

    def _load_data(self, languages=None, strict_order=False, use_given_order=False):
        if not languages:
            languages = self.language_order
        unsupported_languages = set(languages) - set(self.language_order)
        if unsupported_languages:
            raise ValueError("Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
        languages_to_load = list(set(languages) - set(self._data.keys()))
        loaded_languages = list(set(languages) - set(languages_to_load))
        languages_to_load.sort(key = self.language_order.index)
        loaded_languages.sort(key = self.language_order.index)

        if strict_order:
            if not use_given_order:
                languages.sort(key = self.language_order.index)
            for shortname in languages:
                if shortname in loaded_languages:
                    yield shortname, self._data[shortname]
                else:
                    language_info = SafeLoader(get_data('data', 'languagefiles/' + shortname + '.yaml')).get_data()
                    self._update_language_info_with_base_info(language_info, self.base_data)
                    language = Language(shortname, language_info)
                    if language.validate_info():
                        self._data[shortname] = language
                        yield shortname, language
        else:
            if use_given_order:
                languages_to_load.sort(key = languages.index)
                loaded_languages.sort(key = languages.index)
            for shortname in loaded_languages:
                yield shortname, self._data[shortname]
            for shortname in languages_to_load:
                language_info = SafeLoader(get_data('data', 'languagefiles/' + shortname + '.yaml')).get_data()
                self._update_language_info_with_base_info(language_info, self.base_data)
                language = Language(shortname, language_info)
                if language.validate_info():
                    self._data[shortname] = language
                    yield shortname, language

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in six.iteritems(base_info):
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


default_language_loader = LanguageDataLoader()
