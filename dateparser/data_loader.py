# -*- coding: utf-8 -*-
from pkgutil import get_data

from yaml import load as load_yaml


class LanguageDataLoader(object):
    def __init__(self, file=None):
        if isinstance(file, basestring):
            file = open(file)
        self.file = file

    def load_data(self):
        if self.file is None:
            data = get_data('dateparser', 'languages.yaml')
        else:
            data = self.file.read()
        data = load_yaml(data)
        return data
