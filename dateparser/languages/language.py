# -*- coding: utf-8 -*-
import re
from itertools import chain

from dateutil import parser

from dateparser.timezone_parser import pop_tz_offset_from_string
from dateparser.utils import wrap_replacement_for_regex

from .dictionary import Dictionary, ALWAYS_KEEP_TOKENS
from .validation import LanguageValidator


class Language(object):
    _dictionary = None
    _splitters = None
    _wordchars = None

    def __init__(self, shortname, language_info):
        self.shortname = shortname
        self.info = language_info.copy()
        for simplification in self.info.get('simplifications', []):
            key, value = list(simplification.items())[0]
            if isinstance(value, int):
                simplification[key] = str(value)

    def validate_info(self, validator=None):
        if validator is None:
            validator = LanguageValidator

        return validator.validate_info(language_id=self.shortname, info=self.info)

    def is_applicable(self, date_string, strip_timezone=False):
        if strip_timezone:
            date_string, timezone = pop_tz_offset_from_string(date_string, as_offset=False)

        date_string = self._simplify(date_string)
        tokens = self._split(date_string, keep_formatting=False)
        if self._is_date_consists_of_digits_only(tokens):
            return True
        else:
            return self._are_all_words_in_the_dictionary(tokens)

    def translate(self, date_string, keep_formatting=False):
        date_string = self._simplify(date_string)
        words = self._split(date_string, keep_formatting)

        dictionary = self._get_dictionary()
        for i, word in enumerate(words):
            word = word.lower()
            if word in dictionary:
                words[i] = dictionary[word] or ''

        return self._join(list(filter(bool, words)), separator="" if keep_formatting else " ")

    def _simplify(self, date_string):
        date_string = date_string.lower()
        for simplification in self.info.get('simplifications', []):
            pattern, replacement = list(simplification.items())[0]
            if not self.info.get('no_word_spacing', False):
                replacement = wrap_replacement_for_regex(replacement, pattern)
                pattern = r'(\A|\d|_|\W)%s(\d|_|\W|\Z)' % pattern
            date_string = re.sub(pattern, replacement, date_string, flags=re.IGNORECASE | re.UNICODE).lower()
        return date_string

    def _is_date_consists_of_digits_only(self, tokens):
        for token in tokens:
            if not token.isdigit():
                return False
        else:
            return True

    def _are_all_words_in_the_dictionary(self, words):
        dictionary = self._get_dictionary()
        for word in words:
            word = word.lower()
            if word.isdigit() or word in dictionary:
                continue
            else:
                return False
        else:
            return True

    def _split(self, date_string, keep_formatting):
        tokens = [date_string]
        tokens = list(self._split_tokens_with_regex(tokens, "(\d+)"))
        tokens = list(self._split_tokens_by_known_words(tokens, keep_formatting))
        return tokens

    def _split_tokens_with_regex(self, tokens, regex):
        tokens = tokens[:]
        for i, token in enumerate(tokens):
            tokens[i] = re.split(regex, token)
        return filter(bool, chain(*tokens))

    def _split_tokens_by_known_words(self, tokens, keep_formatting):
        dictionary = self._get_dictionary()
        for i, token in enumerate(tokens):
            tokens[i] = dictionary.split(token, keep_formatting)
        return list(chain(*tokens))

    def _join(self, tokens, separator=" "):
        if not tokens:
            return ""

        capturing_splitters = self._get_splitters()['capturing']
        joined = tokens[0]
        for i in range(1, len(tokens)):
            left, right = tokens[i - 1], tokens[i]
            if left not in capturing_splitters and right not in capturing_splitters:
                joined += separator
            joined += right

        return joined

    def _get_dictionary(self):
        if self._dictionary is None:
            self._generate_dictionary()
        return self._dictionary

    def _get_wordchars(self):
        if self._wordchars is None:
            self._set_wordchars()
        return self._wordchars

    def _get_splitters(self):
        if self._splitters is None:
            self._set_splitters()
        return self._splitters

    def _set_splitters(self):
        splitters = {
            'wordchars': set(),  # The ones that split string only if they are not surrounded by letters from both sides
            'capturing': set(),  # The ones that are not filtered out from tokens after split
        }
        splitters['capturing'] |= set(ALWAYS_KEEP_TOKENS)

        wordchars = self._get_wordchars()
        skip = set(self.info.get('skip', [])) | splitters['capturing']
        for token in skip:
            if not re.match('^\W+$', token, re.UNICODE):
                continue
            if token in wordchars:
                splitters['wordchars'].add(token)

        self._splitters = splitters

    def _set_wordchars(self):
        wordchars = set()
        for word in self._get_dictionary():
            if re.match('^[\W\d_]+$', word, re.UNICODE):
                continue
            for char in word:
                wordchars.add(char.lower())

        self._wordchars = wordchars - {" "} | {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}

    def _generate_dictionary(self):
        self._dictionary = Dictionary(self.info)

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
