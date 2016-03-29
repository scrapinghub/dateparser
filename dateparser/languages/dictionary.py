# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
from operator import methodcaller

import regex as re
from six.moves import zip_longest

import unicodedata

DATEUTIL_PARSER_HARDCODED_TOKENS = [":", ".", " ", "-", "/"]  # Consts used in dateutil.parser._parse
DATEUTIL_PARSERINFO_KNOWN_TOKENS = ["am", "pm", "a", "p", "UTC", "GMT", "Z"]
ALWAYS_KEEP_TOKENS = ["+"] + DATEUTIL_PARSER_HARDCODED_TOKENS

class UnknownTokenError(Exception):
    pass


class Dictionary(object):
    _split_regex_cache = {}
    _sorted_words_cache = {}
    _denormalized_words_cache = {}

    def __init__(self, language_info, settings=None):
        dictionary = {}
        self._settings = settings
        self.info = language_info

        if 'skip' in language_info:
            skip = map(methodcaller('lower'), language_info['skip'])
            dictionary.update(zip_longest(skip, [], fillvalue=None))
        if 'pertain' in language_info:
            pertain = map(methodcaller('lower'), language_info['pertain'])
            dictionary.update(zip_longest(pertain, [], fillvalue=None))
        for word in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                     'january', 'february', 'march', 'april', 'may', 'june', 'july',
                     'august', 'september', 'october', 'november', 'december',
                     'year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'ago']:
            translations = map(methodcaller('lower'), language_info[word])
            dictionary.update(zip_longest(translations, [], fillvalue=word))
        dictionary.update(zip_longest(ALWAYS_KEEP_TOKENS, ALWAYS_KEEP_TOKENS))
        dictionary.update(zip_longest(map(methodcaller('lower'),
                                          DATEUTIL_PARSERINFO_KNOWN_TOKENS),
                                      DATEUTIL_PARSERINFO_KNOWN_TOKENS))

        self._dictionary = dictionary
        self._no_word_spacing = language_info.get('no_word_spacing', False)

    def __contains__(self, key):
        if key in self._settings.SKIP_TOKENS:
            return True
        return self._dictionary.__contains__(key)

    def __getitem__(self, key):
        if key in self._settings.SKIP_TOKENS:
            return None
        return self._dictionary.__getitem__(key)

    def __iter__(self):
        return chain(self._settings.SKIP_TOKENS, iter(self._dictionary))

    def split(self, string, keep_formatting):
        """ Recursively splitting string by words in dictionary """
        if not string:
            return string

        regex = self._get_split_regex_cache()
        match = regex.match(string)
        if not match:
            return [string] if self._should_capture(string, keep_formatting) else []

        unparsed, known, unknown = match.groups()
        splitted = [known] if self._should_capture(known, keep_formatting) else []
        if unparsed and self._should_capture(unparsed, keep_formatting):
            splitted = [unparsed] + splitted
        if unknown:
            splitted.extend(self.split(unknown, keep_formatting))

        return splitted

    def _should_capture(self, token, keep_formatting):
        return (
            keep_formatting or
            (token in ALWAYS_KEEP_TOKENS) or
            re.match(r"^.*[^\W_].*$", token, re.U)
        )

    def _get_sorted_words_from_cache(self):
        if (
                self._settings.registry_key not in self._sorted_words_cache or
                self.info['name'] not in self._sorted_words_cache[self._settings.registry_key]
            ):
            self._sorted_words_cache[self._settings.registry_key] = {
                self.info['name']: sorted([key for key in self], key=len, reverse=True)
            }
        return self._sorted_words_cache[self._settings.registry_key][self.info['name']]


    def _get_split_regex_cache(self):
        if (
                self._settings.registry_key not in self._split_regex_cache or
                self.info['name'] not in self._split_regex_cache[self._settings.registry_key]
            ):
            self._construct_split_regex()
        return self._split_regex_cache[self._settings.registry_key][self.info['name']]

    def _construct_split_regex(self):
        known_words_group = u"|".join(map(re.escape, self._get_sorted_words_from_cache()))
        if self._no_word_spacing:
            regex = r"^(.*?)({})(.*)$".format(known_words_group)
        else:
            regex = r"^(.*?(?:\A|\d|_|\W))({})((?:\d|_|\W|\Z).*)$".format(known_words_group)
        self._split_regex_cache[self._settings.registry_key] = {
            self.info['name']: re.compile(regex, re.UNICODE | re.IGNORECASE)
        }


class NormalizedDictionary(Dictionary):

    def __init__(self, language_info, settings=None):
        super(NormalizedDictionary, self).__init__(language_info, settings)
        self._normalize()

    def _normalize(self):
        '''
        Normalization can be done by defining either normalization mapping in languages.yml or 
        default unicode nkfd normalization.
        Example entry in languages.yml:
        normalization_mapping:
            - é: "e"
            - û: "u"
        '''

        normalization_mapping = {}
        if 'normalization_mapping' in self.info:
            for char_mapping in self.info['normalization_mapping']:
                for char in char_mapping:
                    normalization_mapping.update({ord(char): unicode(char_mapping[char])})
        new_dict = {}
        for key, value in self._dictionary.items():
            if set(key).intersection(set(normalization_mapping.keys())):
                new_dict[unicode(key).translate(normalization_mapping)] = value
            else:
                new_dict[self._normalize_default(key)] = value
        self._dictionary = new_dict

    def _normalize_default(self, string):
        return ''.join((
                c for c in unicodedata.normalize('NFKD', unicode(string))
                if unicodedata.category(c) != 'Mn'))
