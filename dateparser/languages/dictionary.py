# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
from operator import methodcaller

import regex as re
from six.moves import zip_longest

DATEUTIL_PARSER_HARDCODED_TOKENS = [":", ".", " ", "-", "/"]  # Consts used in dateutil.parser._parse
DATEUTIL_PARSERINFO_KNOWN_TOKENS = ["am", "pm", "a", "p", "UTC", "GMT", "Z"]
ALWAYS_KEEP_TOKENS = ["+"] + DATEUTIL_PARSER_HARDCODED_TOKENS
from dateparser.utils import strip_diacritical_marks

# Convert these unicode characters into ASCII
xlate = {
    # The note at the bottom of the page says "the inverted question
    # mark represents a questionable character found as a result of
    # NLM's conversion from its legacy extended EBCDIC character set
    # to UNICODE UTF-8."  I do not use it but leave it here for
    # completeness.
    ord(u"\N{LATIN CAPITAL LETTER O WITH STROKE}"): u"O",
    ord(u"\N{LATIN SMALL LETTER A WITH GRAVE}"): u"a",
    ord(u"\N{LATIN SMALL LETTER A WITH ACUTE}"): u"a",
    ord(u"\N{LATIN SMALL LETTER A WITH CIRCUMFLEX}"): u"a",
    ord(u"\N{LATIN SMALL LETTER A WITH TILDE}"): u"a",
    ord(u"\N{LATIN SMALL LETTER A WITH DIAERESIS}"): u"a",
    ord(u"\N{LATIN SMALL LETTER A WITH RING ABOVE}"): u"a",
    ord(u"\N{LATIN SMALL LETTER C WITH CEDILLA}"): u"c",
    ord(u"\N{LATIN SMALL LETTER E WITH GRAVE}"): u"e",
    ord(u"\N{LATIN SMALL LETTER E WITH ACUTE}"): u"e",
#    ord(u"\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}"): u"e",
#    ord(u"\N{LATIN SMALL LETTER E WITH DIAERESIS}"): u"e",
#    ord(u"\N{LATIN SMALL LETTER I WITH GRAVE}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER I WITH ACUTE}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER I WITH DIAERESIS}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER N WITH TILDE}"): u"n",
#    ord(u"\N{LATIN SMALL LETTER O WITH GRAVE}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH ACUTE}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH CIRCUMFLEX}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH TILDE}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH DIAERESIS}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH STROKE}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER U WITH GRAVE}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH ACUTE}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH CIRCUMFLEX}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH DIAERESIS}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER Y WITH ACUTE}"): u"y",
#    ord(u"\N{LATIN SMALL LETTER Y WITH DIAERESIS}"): u"y",
#    ord(u"\N{LATIN SMALL LETTER A WITH MACRON}"): u"a",
#    ord(u"\N{LATIN SMALL LETTER A WITH BREVE}"): u"a",
#    ord(u"\N{LATIN SMALL LETTER C WITH ACUTE}"): u"c",
#    ord(u"\N{LATIN SMALL LETTER C WITH CIRCUMFLEX}"): u"c",
#    ord(u"\N{LATIN SMALL LETTER E WITH MACRON}"): u"e",
#    ord(u"\N{LATIN SMALL LETTER E WITH BREVE}"): u"e",
#    ord(u"\N{LATIN SMALL LETTER G WITH CIRCUMFLEX}"): u"g",
#    ord(u"\N{LATIN SMALL LETTER G WITH BREVE}"): u"g",
#    ord(u"\N{LATIN SMALL LETTER G WITH CEDILLA}"): u"g",
#    ord(u"\N{LATIN SMALL LETTER H WITH CIRCUMFLEX}"): u"h",
#    ord(u"\N{LATIN SMALL LETTER I WITH TILDE}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER I WITH MACRON}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER I WITH BREVE}"): u"i",
#    ord(u"\N{LATIN SMALL LETTER J WITH CIRCUMFLEX}"): u"j",
#    ord(u"\N{LATIN SMALL LETTER K WITH CEDILLA}"): u"k",
#    ord(u"\N{LATIN SMALL LETTER L WITH ACUTE}"): u"l",
#    ord(u"\N{LATIN SMALL LETTER L WITH CEDILLA}"): u"l",
#    ord(u"\N{LATIN CAPITAL LETTER L WITH STROKE}"): u"L",
#    ord(u"\N{LATIN SMALL LETTER L WITH STROKE}"): u"l",
#    ord(u"\N{LATIN SMALL LETTER N WITH ACUTE}"): u"n",
#    ord(u"\N{LATIN SMALL LETTER N WITH CEDILLA}"): u"n",
#    ord(u"\N{LATIN SMALL LETTER O WITH MACRON}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER O WITH BREVE}"): u"o",
#    ord(u"\N{LATIN SMALL LETTER R WITH ACUTE}"): u"r",
#    ord(u"\N{LATIN SMALL LETTER R WITH CEDILLA}"): u"r",
#    ord(u"\N{LATIN SMALL LETTER S WITH ACUTE}"): u"s",
#    ord(u"\N{LATIN SMALL LETTER S WITH CIRCUMFLEX}"): u"s",
#    ord(u"\N{LATIN SMALL LETTER S WITH CEDILLA}"): u"s",
#    ord(u"\N{LATIN SMALL LETTER T WITH CEDILLA}"): u"t",
#    ord(u"\N{LATIN SMALL LETTER U WITH TILDE}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH MACRON}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH BREVE}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER U WITH RING ABOVE}"): u"u",
#    ord(u"\N{LATIN SMALL LETTER W WITH CIRCUMFLEX}"): u"w",
#    ord(u"\N{LATIN SMALL LETTER Y WITH CIRCUMFLEX}"): u"y",
#    ord(u"\N{LATIN SMALL LETTER Z WITH ACUTE}"): u"z",
#    ord(u"\N{LATIN SMALL LETTER W WITH GRAVE}"): u"w",
#    ord(u"\N{LATIN SMALL LETTER W WITH ACUTE}"): u"w",
#    ord(u"\N{LATIN SMALL LETTER W WITH DIAERESIS}"): u"w",
#    ord(u"\N{LATIN SMALL LETTER Y WITH GRAVE}"): u"y",
    }

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
        self._normalize_dictionary()

    def _normalize_dictionary(self):

        normalization_table = {}
        if 'normalization' in self.info:
            for n in self.info['normalization']:
                for j in n:
                    normalization_table.update({ord(j): unicode(n[j])})

        new_dict = {}
        for i in self._dictionary:
            new_dict[unicode(i).translate(normalization_table)] = self._dictionary[i]
        self._dictionary = new_dict
