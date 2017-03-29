# -*- coding: utf-8 -*-
from pkgutil import get_data
from collections import OrderedDict

import six

from ..utils import SafeLoader
from .language import Language


class LanguageDataLoader(object):
    _data = {}

    def __init__(self, file=None):
        if isinstance(file, six.string_types):
            file = open(file)
        self.file = file

    def get_language_map(self,languages = None):
        return self._load_data(languages = languages)

    def get_languages(self):
        return self._load_data().values()

    def get_language(self, shortname):
        return self._load_data(languages = [shortname]).get(shortname)

    def _load_data(self, languages = None):
        if self.file is None:
            data = get_data('data', 'languages.yaml')
        else:
            data = self.file.read()
        
        language_order = ['en', 'ar', 'be', 'bg', 'bn', 'cs', 'da', 'de', 'es', 
          'fa', 'fi', 'fr', 'he', 'hi', 'hu', 'id', 'it', 'ja', 'nl', 'pl', 'pt', 
          'ro', 'ru', 'th', 'tl', 'tr', 'uk', 'vi', 'zh']
        if not languages:
            languages=language_order
        else:
            unsupported_languages = set(languages)-set(language_order)
            if unsupported_languages:
                raise ValueError("Unknown language(s): %s" % ', '.join(map(repr, unsupported_languages)))
            languages.sort(key = language_order.index)
        absent_languages = set(languages)-set(self._data.keys())
        data = SafeLoader(data,languages=absent_languages).get_data()
        data = {key:value for key,value in data.items() if value}
        base_data = data.pop('base', {'skip': []})
        for shortname in absent_languages:
            language_info = data[shortname]
            self._update_language_info_with_base_info(language_info, base_data)
            language = Language(shortname, language_info)
            if language.validate_info():
                self._data[shortname] = language
        required_languages=OrderedDict()
        for shortname in languages:
            required_languages[shortname] = self._data[shortname]
        return required_languages

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in six.iteritems(base_info):
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


default_language_loader = LanguageDataLoader()
