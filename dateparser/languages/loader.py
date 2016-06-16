# -*- coding: utf-8 -*-
from pkgutil import get_data
from collections import OrderedDict

import six
import ruamel.yaml as yaml

from .language import Language


# support `!include` directive
def yaml_include(loader, node):
    return yaml.load(get_data('data', node.value))

yaml.add_constructor("!include", yaml_include)


class LanguageDataLoader(object):
    _data = None

    def __init__(self, file=None):
        if isinstance(file, six.string_types):
            file = open(file)
        self.file = file

    def get_language_map(self):
        if self._data is None:
            self._load_data()
        return self._data

    def get_languages(self):
        if self._data is None:
            self._load_data()
        return self._data.values()

    def get_language(self, shortname):
        if self._data is None:
            self._load_data()
        return self._data.get(shortname)

    def _load_data(self):
        if self.file is None:
            data = get_data('data', 'languages.yaml')
        else:
            data = self.file.read()
        data = yaml.load(data)
        base_data = data.pop('base', {'skip': []})
        language_order = data.pop('languageorder')
        known_languages = OrderedDict()
        for shortname in language_order:
            language_info = data[shortname]
            self._update_language_info_with_base_info(language_info, base_data)
            language = Language(shortname, language_info)
            if language.validate_info():
                known_languages[shortname] = language
        self._data = known_languages

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in six.iteritems(base_info):
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


default_language_loader = LanguageDataLoader()
