# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from six.moves import zip_longest
from operator import methodcaller

DATEUTIL_PARSER_HARDCODED_TOKENS = [":", ".", " ", "-", "/"]  # Consts used in dateutil.parser._parse
DATEUTIL_PARSERINFO_KNOWN_TOKENS = ["am", "pm", "a", "p", "UTC", "GMT", "Z"]
ALWAYS_KEEP_TOKENS = ["+"] + DATEUTIL_PARSER_HARDCODED_TOKENS


class UnknownTokenError(Exception):
    pass


class Dictionary(object):
    _sorted_words = None
    _split_regex = None

    def __init__(self, language_info):
        dictionary = {}

        if 'skip' in language_info:
            skip = map(methodcaller('lower'), language_info['skip'])
            dictionary.update(zip_longest(skip, [], fillvalue=None))
        if 'pertain' in language_info:
            pertain = map(methodcaller('lower'), language_info['pertain'])
            dictionary.update(zip_longest(pertain, [], fillvalue=None))
        for word in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                     'january', 'february', 'march', 'april', 'may', 'june', 'july',
                     'august', 'september', 'october', 'november', 'december',
                     'year', 'month', 'week', 'day', 'hour', 'minute', 'second',
                     'ago']:
            translations = map(methodcaller('lower'), language_info[word])
            dictionary.update(zip_longest(translations, [], fillvalue=word))
        dictionary.update(zip_longest(ALWAYS_KEEP_TOKENS, ALWAYS_KEEP_TOKENS))
        dictionary.update(zip_longest(map(methodcaller('lower'),
                                           DATEUTIL_PARSERINFO_KNOWN_TOKENS),
                                       DATEUTIL_PARSERINFO_KNOWN_TOKENS))

        self._dictionary = dictionary
        self._no_word_spacing = language_info.get('no_word_spacing', False)

    def __contains__(self, key):
        return self._dictionary.__contains__(key)

    def __getitem__(self, key):
        return self._dictionary.__getitem__(key)

    def __iter__(self):
        return iter(self._dictionary)

    def split(self, string, keep_formatting):
        """ Recursively splitting string by words in dictionary """
        if not string:
            return string

        regex = self._get_split_regex()
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
        return keep_formatting or (token in ALWAYS_KEEP_TOKENS) or re.match("^.*[^\W_].*$", token, re.U)

    def _get_sorted_words(self):
        if self._sorted_words is None:
            self._sorted_words = sorted(self._dictionary.keys(), key=len, reverse=True)
        return self._sorted_words

    def _get_split_regex(self):
        if self._split_regex is None:
            self._construct_split_regex()
        return self._split_regex

    def _construct_split_regex(self):
        known_words_group = u"|".join(map(re.escape, self._get_sorted_words()))
        if self._no_word_spacing:
            regex = r"^(.*?)({})(.*)$".format(known_words_group)
        else:
            regex = r"^(.*?(?:\A|\d|_|\W))({})((?:\d|_|\W|\Z).*)$".format(known_words_group)
        self._split_regex = re.compile(regex, re.UNICODE | re.IGNORECASE)
