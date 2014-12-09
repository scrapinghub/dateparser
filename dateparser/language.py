# -*- coding: utf-8 -*-
import re
from itertools import izip_longest, chain
from logging import getLogger
from operator import methodcaller
from pkgutil import get_data

from dateutil import parser
from yaml import load as load_yaml

DATEUTIL_PARSER_HARDCODED_TOKENS = [":", ".", " ", "-", "/"]  # Consts used in dateutil.parser._parse
DATEUTIL_PARSERINFO_KNOWN_TOKENS = ["am", "pm", "a", "p", "UTC", "GMT", "Z"]


class UnknownTokenError(Exception):
    pass


class LanguageDataLoader(object):
    _data = None

    def __init__(self, file=None):
        if isinstance(file, basestring):
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
        data = load_yaml(data)
        base_data = data.pop('base', {})
        known_languages = {}
        for shortname, language_info in data.iteritems():
            self._update_language_info_with_base_info(language_info, base_data)
            language = Language(shortname, language_info)
            if language.validate_info():
                known_languages[shortname] = language
        self._data = known_languages

    def _update_language_info_with_base_info(self, language_info, base_info):
        for key, values in base_info.iteritems():
            if isinstance(values, list):
                extended_values = (values + language_info[key]) if key in language_info else values
                language_info[key] = extended_values


class Language(object):
    _dictionary = None
    _splitters = None
    _wordchars = None

    def __init__(self, shortname, language_info):
        self.shortname = shortname
        self.info = language_info.copy()
        for simplification in self.info.get('simplifications', []):
            key, value = simplification.items()[0]
            if isinstance(value, int):
                simplification[key] = str(value)

    def validate_info(self, validator=None):
        if validator is None:
            validator = LanguageValidator

        return validator.validate_info(language_id=self.shortname, info=self.info)

    def is_applicable(self, date_string):
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

        return self._join(filter(bool, words), separator="" if keep_formatting else " ")

    def _simplify(self, date_string):
        date_string = date_string.lower()
        for simplification in self.info.get('simplifications', []):
            pattern, replacement = simplification.items()[0]
            if not self.info.get('no_word_spacing', False):
                pattern = r'\b%s\b' % pattern
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
        tokens = self._split_tokens_by_wordchar_splitters(tokens, keep_formatting)
        tokens = self._split_tokens_with_regex(tokens, "(\d+)")

        if self.info.get('no_word_spacing', False):
            tokens = self._split_tokens_by_known_words(tokens)
        else:
            tokens = self._split_tokens_by_unknown_words(tokens, keep_formatting)

        return tokens

    def _split_tokens_by_wordchar_splitters(self, tokens, keep_formatting):
        splitters = self._get_splitters()
        if splitters['wordchars']:
            capturing = set(splitters['wordchars']) & set(splitters['capturing'])
            if capturing:
                capturing_group = u'({})'.format("|".join(map(re.escape, capturing)))
                tokens = self._split_tokens_with_regex(tokens, u'(?<=[\W\d]){}'.format(capturing_group))
                tokens = self._split_tokens_with_regex(tokens, u'{}(?=[\W\d])'.format(capturing_group))

            non_capturing = set(splitters['wordchars']) - set(splitters['capturing'])
            if non_capturing:
                non_capturing_group = (u'({})' if keep_formatting else u'(?:{})').format(
                    "|".join(map(re.escape, non_capturing)))
                tokens = self._split_tokens_with_regex(tokens, u'(?<=[\W\d]){}'.format(non_capturing_group))
                tokens = self._split_tokens_with_regex(tokens, u'{}(?=[\W\d])'.format(non_capturing_group))
        return tokens

    def _split_tokens_with_regex(self, tokens, regex):
        tokens = tokens[:]
        for i, token in enumerate(tokens):
            tokens[i] = re.split(regex, token)
        return filter(bool, chain(*tokens))

    def _split_tokens_by_known_words(self, tokens):
        for i, token in enumerate(tokens):
            try:
                splitted_token = self._split_by_dictionary(token)
            except UnknownTokenError:
                tokens[i] = [token]
            else:
                tokens[i] = splitted_token
        return list(chain(*tokens))

    def _split_tokens_by_unknown_words(self, tokens, keep_formatting):
        tokens = tokens[:]
        wordchars = self._get_wordchars()
        capturing_splitters = self._get_splitters()['capturing']
        for i, token in enumerate(tokens):
            splitted = []
            token_ = ''
            for char in token:
                if char in wordchars:
                    token_ += char
                else:
                    splitted.append(token_)
                    token_ = ''
                    if keep_formatting or (char in capturing_splitters) or re.match("^[^\W_]$", char, re.U):
                        splitted.append(char)
            splitted.append(token_)
            tokens[i] = splitted

        tokens = filter(bool, chain(*tokens))
        tokens = self._combine_splitted_words(tokens)
        return tokens

    def _split_by_dictionary(self, string):
        """ Recursively splitting string by words in dictionary """
        dictionary = self._get_dictionary()
        token = ''
        while string:
            token += string[0]
            string = string[1:]
            if token in dictionary:
                try:
                    splitted = self._split_by_dictionary(string) if string else []
                except UnknownTokenError:
                    continue  # Try longer token
                else:
                    return [token] + splitted

        raise UnknownTokenError

    def _combine_splitted_words(self, words):
        combined = []
        tested = ''
        dictionary = self._get_dictionary()
        for word in words:
            tested += word
            candidate = False
            for translation in dictionary:
                if translation == tested:
                    combined.append(tested)
                    tested = ''
                    break
                elif re.match(r'%s\b.*' % tested, translation):
                    candidate = True
                    continue
            else:
                if not candidate:
                    combined.append(tested)
                    tested = ''
        if tested:
            combined.append(tested)
        return combined

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
        splitters['capturing'] |= set(DATEUTIL_PARSER_HARDCODED_TOKENS)

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
        dictionary = {}

        if 'skip' in self.info:
            skip = map(methodcaller('lower'), self.info['skip'])
            dictionary.update(izip_longest(skip, [], fillvalue=None))
        if 'pertain' in self.info:
            pertain = map(methodcaller('lower'), self.info['pertain'])
            dictionary.update(izip_longest(pertain, [], fillvalue=None))
        for word in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                     'january', 'february', 'march', 'april', 'may', 'june', 'july',
                     'august', 'september', 'october', 'november', 'december',
                     'year', 'month', 'week', 'day', 'hour', 'minute', 'second',
                     'ago']:
            translations = map(methodcaller('lower'), self.info[word])
            dictionary.update(izip_longest(translations, [], fillvalue=word))
        dictionary.update(izip_longest(DATEUTIL_PARSER_HARDCODED_TOKENS, DATEUTIL_PARSER_HARDCODED_TOKENS))
        dictionary.update(izip_longest(DATEUTIL_PARSERINFO_KNOWN_TOKENS, DATEUTIL_PARSERINFO_KNOWN_TOKENS))

        self._dictionary = dictionary

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
        name = '{language}ParserInfo'.format(self.info['name'])
        return type(name, bases=[base_cls], dict=attributes)


class LanguageValidator(object):
    logger = getLogger('dateparser')
    VALID_KEYS = ['name', 'skip', 'pertain', 'simplifications', 'no_word_spacing', 'ago',
                  'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                  'january', 'february', 'march', 'april', 'may', 'june', 'july',
                  'august', 'september', 'october', 'november', 'december',
                  'year', 'month', 'week', 'day', 'hour', 'minute', 'second']

    @classmethod
    def validate_info(cls, language_id, info):
        result = True

        result &= cls._validate_type(language_id, info)
        if not result:
            return False

        result &= cls._validate_name(language_id, info)
        result &= cls._validate_word_spacing(language_id, info)
        result &= cls._validate_skip_list(language_id, info)
        result &= cls._validate_pertain_list(language_id, info)
        result &= cls._validate_weekdays(language_id, info)
        result &= cls._validate_months(language_id, info)
        result &= cls._validate_units(language_id, info)
        result &= cls._validate_other_words(language_id, info)
        result &= cls._validate_simplifications(language_id, info)
        result &= cls._validate_extra_keys(language_id, info)
        return result

    @classmethod
    def _validate_type(cls, language_id, info):
        result = True

        if not isinstance(info, dict):
            cls.logger.error("Language '%(id)s' info expected to be dict, but have got %(type)s",
                             {'id': language_id, 'type': type(info).__name__})
            result = False

        return result

    @classmethod
    def _validate_name(cls, language_id, info):
        result = True

        if 'name' not in info \
                or not isinstance(info['name'], basestring) \
                or not info['name']:
            cls.logger.error("Language '%(id)s' does not have a name", {'id': language_id})
            result = False

        return result

    @classmethod
    def _validate_word_spacing(cls, language_id, info):
        if 'no_word_spacing' not in info:
            return True  # Optional key

        result = True

        value = info['no_word_spacing']
        if value not in [True, False]:
            cls.logger.error("Invalid 'no_word_spacing' value %(value)r for '%(id)s' language:"
                             " expected boolean",
                             {'value': value, 'id': language_id})
            result = False

        return result

    @classmethod
    def _validate_skip_list(cls, language_id, info):
        if 'skip' not in info:
            return True  # Optional key

        result = True

        skip_tokens_list = info['skip']
        if isinstance(skip_tokens_list, list):
            for token in skip_tokens_list:
                if not isinstance(token, basestring) or not token:
                    cls.logger.error("Invalid 'skip' token %(token)r for '%(id)s' language:"
                                     " expected not empty string",
                                     {'token': token, 'id': language_id})
                    result = False
        else:
            cls.logger.error("Invalid 'skip' list for '%(id)s' language:"
                             " expected list type but have got %(type)s",
                             {'id': language_id, 'type': type(skip_tokens_list).__name__})
            result = False

        return result

    @classmethod
    def _validate_pertain_list(cls, language_id, info):
        if 'pertain' not in info:
            return True  # Optional key

        result = True

        pertain_tokens_list = info['skip']
        if isinstance(pertain_tokens_list, list):
            for token in pertain_tokens_list:
                if not isinstance(token, basestring) or not token:
                    cls.logger.error("Invalid 'pertain' token %(token)r for '%(id)s' language:"
                                     " expected not empty string",
                                     {'token': token, 'id': language_id})
                    result = False
        else:
            cls.logger.error("Invalid 'pertain' list for '%(id)s' language:"
                             " expected list type but have got %(type)s",
                             {'id': language_id, 'type': type(pertain_tokens_list).__name__})
            result = False

        return result

    @classmethod
    def _validate_weekdays(cls, language_id, info):
        result = True

        for weekday in 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday':
            if weekday not in info or not info[weekday]:
                cls.logger.error("No translations for '%(weekday)s' provided for '%(id)s' language",
                                 {'weekday': weekday, 'id': language_id})
                result = False
                continue

            translations_list = info[weekday]
            if isinstance(translations_list, list):
                for token in translations_list:
                    if not isinstance(token, basestring) or not token:
                        cls.logger.error("Invalid '%(weekday)s' translation %(token)r for '%(id)s' language:"
                                         " expected not empty string",
                                         {'weekday': weekday, 'token': token, 'id': language_id})
                        result = False
            else:
                cls.logger.error("Invalid '%(weekday)s' translations list for '%(id)s' language:"
                                 " expected list type but have got %(type)s",
                                 {'weekday': weekday, 'id': language_id, 'type': type(translations_list).__name__})
                result = False

        return result


    @classmethod
    def _validate_months(cls, language_id, info):
        result = True

        for month in ('january', 'february', 'march', 'april', 'may', 'june', 'july',
                      'august', 'september', 'october', 'november', 'december'):
            if month not in info or not info[month]:
                cls.logger.error("No translations for '%(month)s' provided for '%(id)s' language",
                                 {'month': month, 'id': language_id})
                result = False
                continue

            translations_list = info[month]
            if isinstance(translations_list, list):
                for token in translations_list:
                    if not isinstance(token, basestring) or not token:
                        cls.logger.error("Invalid '%(month)s' translation %(token)r for '%(id)s' language:"
                                         " expected not empty string",
                                         {'month': month, 'token': token, 'id': language_id})
                        result = False
            else:
                cls.logger.error("Invalid '%(month)s' translations list for '%(id)s' language:"
                                 " expected list type but have got %(type)s",
                                 {'month': month, 'id': language_id, 'type': type(translations_list).__name__})
                result = False

        return result

    @classmethod
    def _validate_units(cls, language_id, info):
        result = True

        for unit in 'year', 'month', 'week', 'day', 'hour', 'minute', 'second':
            if unit not in info or not info[unit]:
                cls.logger.error("No translations for '%(unit)s' provided for '%(id)s' language",
                                 {'unit': unit, 'id': language_id})
                result = False
                continue

            translations_list = info[unit]
            if isinstance(translations_list, list):
                for token in translations_list:
                    if not isinstance(token, basestring) or not token:
                        cls.logger.error("Invalid '%(unit)s' translation %(token)r for '%(id)s' language:"
                                         " expected not empty string",
                                         {'unit': unit, 'token': token, 'id': language_id})
                        result = False
            else:
                cls.logger.error("Invalid '%(unit)s' translations list for '%(id)s' language:"
                                 " expected list type but have got %(type)s",
                                 {'unit': unit, 'id': language_id, 'type': type(translations_list).__name__})
                result = False

        return result

    @classmethod
    def _validate_other_words(cls, language_id, info):
        result = True

        for word in 'ago', :
            if word not in info or not info[word]:
                cls.logger.error("No translations for '%(word)s' provided for '%(id)s' language",
                                 {'word': word, 'id': language_id})
                result = False
                continue

            translations_list = info[word]
            if isinstance(translations_list, list):
                for token in translations_list:
                    if not isinstance(token, basestring) or not token:
                        cls.logger.error("Invalid '%(word)s' translation %(token)r for '%(id)s' language:"
                                         " expected not empty string",
                                         {'word': word, 'token': token, 'id': language_id})
                        result = False
            else:
                cls.logger.error("Invalid '%(word)s' translations list for '%(id)s' language:"
                                 " expected list type but have got %(type)s",
                                 {'word': word, 'id': language_id, 'type': type(translations_list).__name__})
                result = False

        return result

    @classmethod
    def _validate_simplifications(cls, language_id, info):
        if 'simplifications' not in info:
            return True  # Optional key

        result = True

        simplifications_list = info['simplifications']
        if isinstance(simplifications_list, list):
            for simplification in simplifications_list:
                if not isinstance(simplification, dict) or len(simplification) != 1:
                    cls.logger.error("Invalid simplification %(simplification)r for '%(id)s' language:"
                                     " eash simplification suppose to be one-to-one mapping",
                                     {'simplification': simplification, 'id': language_id})
                    result = False
                    continue

                key, value = simplification.items()[0]
                if not isinstance(key, basestring) or not isinstance(value, (basestring, int)):
                    cls.logger.error("Invalid simplification %(simplification)r for '%(id)s' language:"
                                     " each simplification suppose to be string-to-string-or-int mapping",
                                     {'simplification': simplification, 'id': language_id})
                    result = False
                    continue

                compiled_key = re.compile(key)
                value = unicode(value)
                replacements = re.findall(r'\\(\d+)', value)
                replacements.extend(re.findall(r'\\g<(.+?)>', value))

                groups = []
                for group in replacements:
                    if group.isdigit():
                        groups.append(int(group))
                    elif group in compiled_key.groupindex:
                        groups.append(compiled_key.groupindex[group])
                    else:
                        cls.logger.error("Invalid simplification %(simplification)r for '%(id)s' language:"
                                         " unknown group %(group)s",
                                         {'simplification': simplification, 'id': language_id, 'group': group})
                        result = False

                used_groups = set(map(int, groups))
                expected_groups = set(range(0, compiled_key.groups + 1))
                extra_groups = used_groups - expected_groups
                not_used_groups = expected_groups - used_groups
                not_used_groups -= {0}  # Entire substring is not required to be used

                if extra_groups:
                    cls.logger.error("Invalid simplification %(simplification)r for '%(id)s' language:"
                                     " unknown groups %(groups)s",
                                     {'simplification': simplification,
                                      'id': language_id,
                                      'groups': ", ".join(map(unicode, sorted(extra_groups)))})
                    result = False

                if not_used_groups:
                    cls.logger.error("Invalid simplification %(simplification)r for '%(id)s' language:"
                                     " groups %(groups)s were not used",
                                     {'simplification': simplification,
                                      'id': language_id,
                                      'groups': ", ".join(map(unicode, sorted(not_used_groups)))})
                    result = False
        else:
            cls.logger.error("Invalid 'simplifications' list for '%(id)s' language:"
                             " expected list type but have got %(type)s",
                             {'id': language_id, 'type': type(simplifications_list).__name__})
            result = False

        return result

    @classmethod
    def _validate_extra_keys(cls, language_id, info):
        result = True

        extra_keys = set(info.keys()) - set(cls.VALID_KEYS)
        if extra_keys:
            cls.logger.error("Extra keys found for '%(id)s' language: %(keys)s",
                             {'id': language_id, 'keys': ", ".join(map(repr, extra_keys))})
            result = False

        return result
