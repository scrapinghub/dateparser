# -*- coding: utf-8 -*-
import regex as re
from itertools import chain

from dateutil import parser

from dateparser.timezone_parser import pop_tz_offset_from_string
from dateparser.utils import wrap_replacement_for_regex, normalize_unicode

from .dictionary import Dictionary, NormalizedDictionary, ALWAYS_KEEP_TOKENS
from .validation import LanguageValidator


class Language(object):

    _dictionary = None
    _normalized_dictionary = None
    _simplifications = None
    _normalized_simplifications = None
    _splitters = None
    _wordchars = None

    def __init__(self, shortname, language_info):
        self.shortname = shortname
        self.info = language_info

    def validate_info(self, validator=None):
        if validator is None:
            validator = LanguageValidator

        return validator.validate_info(language_id=self.shortname, info=self.info)

    def is_applicable(self, date_string, strip_timezone=False, settings=None):
        if strip_timezone:
            date_string, _ = pop_tz_offset_from_string(date_string, as_offset=False)

        date_string = self._simplify(date_string, settings=settings)
        tokens = self._split(date_string, keep_formatting=False, settings=settings)
        if self._is_date_consists_of_digits_only(tokens):
            return True
        else:
            return self._are_all_words_in_the_dictionary(tokens, settings)

    def translate(self, date_string, keep_formatting=False, settings=None):
        date_string = self._simplify(date_string, settings=settings)
        words = self._split(date_string, keep_formatting, settings=settings)

        dictionary = self._get_dictionary(settings)
        for i, word in enumerate(words):
            word = word.lower()
            if word in dictionary:
                words[i] = dictionary[word] or ''
        if "in" in words:
            words = self._clear_future_words(words)

        return self._join(
            list(filter(bool, words)), separator="" if keep_formatting else " ", settings=settings)

    def _simplify(self, date_string, settings=None):
        date_string = date_string.lower()
        for simplification in self._get_simplifications(settings=settings):
            pattern, replacement = list(simplification.items())[0]
            if not self.info.get('no_word_spacing', False):
                replacement = wrap_replacement_for_regex(replacement, pattern)
                pattern = r'(\A|\d|_|\W)%s(\d|_|\W|\Z)' % pattern
            date_string = re.sub(
                pattern, replacement, date_string, flags=re.IGNORECASE | re.UNICODE).lower()
        return date_string

    def _clear_future_words(self, words):
        freshness_words = set(['day', 'week', 'month', 'year', 'hour', 'minute', 'second'])
        if set(words).isdisjoint(freshness_words):
            words.remove("in")
        return words

    def _is_date_consists_of_digits_only(self, tokens):
        for token in tokens:
            if not token.isdigit():
                return False
        else:
            return True

    def _are_all_words_in_the_dictionary(self, words, settings=None):
        dictionary = self._get_dictionary(settings=settings)
        for word in words:
            word = word.lower()
            if (word.isdigit() or word in dictionary):
                continue
            else:
                return False
        else:
            return True

    def _split(self, date_string, keep_formatting, settings=None):
        tokens = [date_string]
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

    def _get_simplifications(self, settings=None):
        if not settings.NORMALIZE:
            if self._simplifications is None:
                self._simplifications = self._generate_simplifications(
                    normalize=False)
            return self._simplifications
        else:
            if self._normalized_simplifications is None:
                self._normalized_simplifications = self._generate_simplifications(
                    normalize=True)
            return self._normalized_simplifications

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
