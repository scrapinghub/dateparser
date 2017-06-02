# -*- coding: utf-8 -*-
from pkgutil import get_data
from collections import OrderedDict

import six

from ..utils import SafeLoader
from .language import Language


class LanguageDataLoader(object):
    _data = {}

    def __init__(self, file=None):
        if isinstance(file, six.string_types) and file.lower().endswith('.yaml'):
            file = open(file)
        elif file is not None:
            raise ValueError("Invalid file : %s" % file)
        self.file = file

    def get_language_map(self,languages = None):
        return self._load_data(languages = languages)

    def get_languages(self):
        return self._load_data().values()

    def get_language(self, shortname):
        return self._load_data(languages = [shortname]).get(shortname)

    def _load_data(self, languages = None):
        required_languages=OrderedDict()
        if self.file is None:
            language_order = ['en', 'ar', 'be', 'bg', 'bn', 'cs', 'da', 'de',
                              'es', 'fa', 'fi', 'fr', 'he', 'hi', 'hu', 'id',
                              'it', 'ja', 'ka', 'nl', 'pl', 'pt', 'ro', 'ru',
                              'sv', 'th', 'tl', 'tr', 'uk', 'vi', 'zh']
            if not languages:
                languages=language_order
            else:
                unsupported_languages = set(languages)-set(language_order)
                if unsupported_languages:
                    raise ValueError("Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
                languages.sort(key = language_order.index)
            absent_languages = set(languages)-set(self._data.keys())
            if absent_languages:
                data = get_data('data', 'languages.yaml')
                data = SafeLoader(data,languages=absent_languages).get_data()
                data = {key:value for key,value in data.items() if value}
                base_data = data.pop('base', {'skip': []})
                for shortname in absent_languages:
                    language_info = data[shortname]
                    self._update_language_info_with_base_info(language_info, base_data)
                    language = Language(shortname, language_info)
                    if language.validate_info():
                        self._data[shortname] = language
            for shortname in languages:
                required_languages[shortname] = self._data[shortname]

        else:
            data = self.file.read()
            data = SafeLoader(data).get_data()
            base_data = data.pop('base', {'skip': []})
            language_order = data.pop('languageorder')
            if not languages:
                languages=language_order
            else:
                unsupported_languages = set(languages)-set(language_order)
                if unsupported_languages:
                    raise ValueError("Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
                languages.sort(key = language_order.index)
            for shortname in languages:
                language_info = data[shortname]
                self._update_language_info_with_base_info(language_info, base_data)
                language = Language(shortname, language_info)
                if language.validate_info():
                    required_languages[shortname] = language

        return required_languages

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in six.iteritems(base_info):
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


default_language_loader = LanguageDataLoader()
