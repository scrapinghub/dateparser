# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import regex as re
from itertools import chain
from collections import OrderedDict

from dateutil import parser

from dateparser.timezone_parser import pop_tz_offset_from_string
from dateparser.utils import normalize_unicode, combine_dicts

from .dictionary import Dictionary, NormalizedDictionary, ALWAYS_KEEP_TOKENS

DIGIT_GROUP_PATTERN = re.compile(r'\\d\+')


class Locale(object):

    _dictionary = None
    _normalized_dictionary = None
    _simplifications = None
    _normalized_simplifications = None
    _splitters = None
    _wordchars = None
    _relative_translations = None
    _normalized_relative_translations = None

    def __init__(self, shortname, language_info):
        self.shortname = shortname
        locale_specific_info = language_info.get("locale_specific", {}).get(shortname, {})
        self.info = combine_dicts(language_info, locale_specific_info)
        self.info.pop("locale_specific", None)

    def is_applicable(self, date_string, strip_timezone=False, settings=None):
        if strip_timezone:
            date_string, _ = pop_tz_offset_from_string(date_string, as_offset=False)

        date_string = self._translate_numerals(date_string)
        date_string = self._simplify(date_string, settings=settings)
        date_tokens = self._get_date_tokens(date_string, settings=settings)

        dictionary = self._get_dictionary(settings)
        return dictionary.are_tokens_valid(date_tokens)

    def translate(self, date_string, keep_formatting=False, settings=None):
        date_string = self._translate_numerals(date_string)
        date_string = self._simplify(date_string, settings=settings)
        date_string_tokens = self._get_date_tokens(date_string, keep_formatting,
                                                   settings=settings)

        dictionary = self._get_dictionary(settings)
        relative_translations = self._get_relative_translations(settings=settings)

        for i, word in enumerate(date_string_tokens):
            word = word.lower()
            for pattern, replacement in relative_translations.items():
                if pattern.match(word):
                    date_string_tokens[i] = pattern.sub(replacement, word)
            else:
                if word in dictionary:
                    date_string_tokens[i] = dictionary[word] or ''
        if "in" in date_string_tokens:
            date_string_tokens = self._clear_future_words(date_string_tokens)

        return self._join(list(filter(bool, date_string_tokens)),
                          separator="" if keep_formatting else " ", settings=settings)

    def _translate_numerals(self, date_string):
        date_string = [date_string]
        date_string_tokens = list(self._split_tokens_with_regex(date_string, r"(\d+)"))
        for i, token in enumerate(date_string_tokens):
            if token.isdigit():
                date_string_tokens[i] = str(int(token)).zfill(len(token))
                if isinstance(date_string_tokens[i], bytes):
                    date_string_tokens[i] = date_string_tokens[i].decode('utf-8')
        return u''.join(date_string_tokens)

    def _get_date_tokens(self, date_string, keep_formatting=False, settings=None):
        relative_translations = self._get_relative_translations(settings=settings)
        tokens = [date_string]
        tokens = list(self._split_tokens_by_known_relative_strings(tokens, keep_formatting,
                                                                   settings=settings))

        for i, token in enumerate(tokens):
            token = token.lower()
            for pattern, _ in relative_translations.items():
                if pattern.match(token):
                    tokens[i] = [token]
                    break
            else:
                tokens[i] = self._split([token], keep_formatting, settings=settings)

        return filter(bool, chain(*tokens))

    def _get_relative_translations(self, settings=None):
        if settings.NORMALIZE:
            if self._normalized_relative_translations is None:
                self._normalized_relative_translations = (
                        self._generate_relative_translations(normalize=True))
            return self._normalized_relative_translations
        else:
            if self._relative_translations is None:
                self._relative_translations = self._generate_relative_translations(normalize=False)
            return self._relative_translations

    def _generate_relative_translations(self, normalize=False):
        relative_translations = self.info.get('relative-type-regex', {})
        relative_dictionary = OrderedDict()
        for key, value in relative_translations.items():
            if normalize:
                value = list(map(normalize_unicode, value))
            pattern = '|'.join(sorted(value, key=len, reverse=True))
            pattern = DIGIT_GROUP_PATTERN.sub(r'?P<n>\d+', pattern)
            pattern = re.compile(r'^{}$'.format(pattern), re.UNICODE | re.IGNORECASE)
            relative_dictionary[pattern] = key
        return relative_dictionary

    def _simplify(self, date_string, settings=None):
        date_string = date_string.lower()
        simplifications = self._get_simplifications(settings=settings)
        for simplification in simplifications:
            pattern, replacement = list(simplification.items())[0]
            date_string = pattern.sub(replacement, date_string).lower()
        return date_string

    def _get_simplifications(self, settings=None):
        no_word_spacing = self.info.get('no_word_spacing', 'False')
        if settings.NORMALIZE:
            if self._normalized_simplifications is None:
                self._normalized_simplifications = []
                simplifications = self._generate_simplifications(normalize=True)
                for simplification in simplifications:
                    pattern, replacement = list(simplification.items())[0]
                    if no_word_spacing == 'False':
                        pattern = r'(?<=\b)%s(?=\b)' % pattern
                    pattern = re.compile(pattern, flags=re.I | re.U)
                    self._normalized_simplifications.append({pattern: replacement})
            return self._normalized_simplifications

        else:
            if self._simplifications is None:
                self._simplifications = []
                simplifications = self._generate_simplifications(normalize=False)
                for simplification in simplifications:
                    pattern, replacement = list(simplification.items())[0]
                    if no_word_spacing == 'False':
                        pattern = r'(?<=\b)%s(?=\b)' % pattern
                    pattern = re.compile(pattern, flags=re.I | re.U)
                    self._simplifications.append({pattern: replacement})
            return self._simplifications

    def _generate_simplifications(self, normalize=False):
        simplifications = []
        for simplification in self.info.get('simplifications', []):
            c_simplification = {}
            key, value = list(simplification.items())[0]
            if normalize:
                key = normalize_unicode(key)

            if isinstance(value, int):
                c_simplification[key] = str(value)
            else:
                c_simplification[key] = normalize_unicode(value) if normalize else value

            simplifications.append(c_simplification)
        return simplifications

    def _clear_future_words(self, words):
        freshness_words = set(['day', 'week', 'month', 'year', 'hour', 'minute', 'second'])
        if set(words).isdisjoint(freshness_words):
            words.remove("in")
        return words

    def _split(self, tokens, keep_formatting, settings=None):
        tokens = list(self._split_tokens_with_regex(tokens, r"(\d+)"))
        tokens = list(
            self._split_tokens_by_known_words(tokens, keep_formatting, settings=settings))
        return tokens

    def _split_tokens_with_regex(self, tokens, regex):
        tokens = tokens[:]
        for i, token in enumerate(tokens):
            tokens[i] = re.split(regex, token)
        return filter(bool, chain(*tokens))

    def _split_tokens_by_known_words(self, tokens, keep_formatting, settings=None):
        dictionary = self._get_dictionary(settings)
        for i, token in enumerate(tokens):
            tokens[i] = dictionary.split(token, keep_formatting)
        return list(chain(*tokens))

    def _split_tokens_by_known_relative_strings(self, tokens, keep_formatting, settings=None):
        dictionary = self._get_dictionary(settings)
        for i, token in enumerate(tokens):
            tokens[i] = dictionary.split_relative(token, keep_formatting)
        return list(chain(*tokens))

    def _join(self, tokens, separator=" ", settings=None):
        if not tokens:
            return ""

        capturing_splitters = self._get_splitters(settings)['capturing']
        joined = tokens[0]
        for i in range(1, len(tokens)):
            left, right = tokens[i - 1], tokens[i]
            if left not in capturing_splitters and right not in capturing_splitters:
                joined += separator
            joined += right

        return joined

    def _get_dictionary(self, settings=None):
        if not settings.NORMALIZE:
            if self._dictionary is None:
                self._generate_dictionary()
            self._dictionary._settings = settings
            return self._dictionary
        else:
            if self._normalized_dictionary is None:
                self._generate_normalized_dictionary()
            self._normalized_dictionary._settings = settings
            return self._normalized_dictionary

    def _get_wordchars(self, settings=None):
        if self._wordchars is None:
            self._set_wordchars(settings)
        return self._wordchars

    def _get_splitters(self, settings=None):
        if self._splitters is None:
            self._set_splitters(settings)
        return self._splitters

    def _set_splitters(self, settings=None):
        splitters = {
            'wordchars': set(),  # The ones that split string only if they are not surrounded by letters from both sides
            'capturing': set(),  # The ones that are not filtered out from tokens after split
        }
        splitters['capturing'] |= set(ALWAYS_KEEP_TOKENS)

        wordchars = self._get_wordchars(settings)
        skip = set(self.info.get('skip', [])) | splitters['capturing']
        for token in skip:
            if not re.match(r'^\W+$', token, re.UNICODE):
                continue
            if token in wordchars:
                splitters['wordchars'].add(token)

        self._splitters = splitters

    def _set_wordchars(self, settings=None):
        wordchars = set()
        for word in self._get_dictionary(settings):
            if re.match(r'^[\W\d_]+$', word, re.UNICODE):
                continue
            for char in word:
                wordchars.add(char.lower())

        self._wordchars = wordchars - {" "} | {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}

    def _generate_dictionary(self, settings=None):
        self._dictionary = Dictionary(self.info, settings=settings)

    def _generate_normalized_dictionary(self, settings=None):
        self._normalized_dictionary = NormalizedDictionary(self.info, settings=settings)

    def to_parserinfo(self, base_cls=parser.parserinfo):
        attributes = {
            'JUMP': self.info.get('skip', []),
            'PERTAIN': self.info.get('pertain', []),
            'WEEKDAYS': [self.info['monday'],
                         self.info['tuesday'],
                         self.info['wednesday'],
                         self.info['thursday'],
                         self.info['friday'],
                         self.info['saturday'],
                         self.info['sunday']],
            'MONTHS': [self.info['january'],
                       self.info['february'],
                       self.info['march'],
                       self.info['april'],
                       self.info['may'],
                       self.info['june'],
                       self.info['july'],
                       self.info['august'],
                       self.info['september'],
                       self.info['october'],
                       self.info['november'],
                       self.info['december']],
            'HMS': [self.info['hour'],
                    self.info['minute'],
                    self.info['second']],
        }
        name = '{language}ParserInfo'.format(language=self.info['name'])
        return type(name, bases=[base_cls], dict=attributes)
