# -*- coding: utf-8 -*-
from pkgutil import get_data
from pkgutil import get_loader

import six
from yaml import load as load_yaml
import yaml

from .language import Language


import os.path
from os import listdir

class Loader(yaml.Loader):

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]

        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))

        with open(filename, 'r') as f:
            return load_yaml(f, Loader)

Loader.add_constructor('!include', Loader.include)


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
        known_languages = {}
        loader = get_loader('data.languages')
        for lang_file in  listdir(loader.filename):
            if not lang_file.startswith('base') and lang_file.endswith('.yaml'):
                shortname = lang_file.replace('.yaml', '')
                f_name = os.path.join(loader.filename, lang_file)
                with open(f_name, 'r') as f:
                    lang_data = load_yaml(f, Loader)
                    base_data = lang_data.pop('base', {'skip': []})
                    self._update_language_info_with_base_info(lang_data, base_data)
                    language = Language(shortname, lang_data)
                    if language.validate_info():
                        known_languages[shortname] = language

        self._data = known_languages

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in six.iteritems(base_info):
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


default_language_loader = LanguageDataLoader()
