# -*- coding: utf-8 -*-
from logging import getLogger
from pkgutil import get_data

from yaml import load as load_yaml


class LanguageDataLoader(object):
    def __init__(self, file=None):
        if isinstance(file, basestring):
            file = open(file)
        self.file = file

    def load_data(self):
        if self.file is None:
            data = get_data('data', 'languages.yaml')
        else:
            data = self.file.read()
        data = load_yaml(data)
        return data


class Language(object):
    def __init__(self, shortname, language_info):
        self.shortname = shortname
        self.info = language_info

    def validate_info(self, validator=None):
        if validator is None:
            validator = LanguageValidator

        return validator.validate_info(language_id=self.shortname, info=self.info)


class LanguageValidator(object):
    logger = getLogger('dateparser')
    VALID_KEYS = ['name', 'skip', 'pertain', 'simplifications',
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
        result &= cls._validate_skip_list(language_id, info)
        result &= cls._validate_pertain_list(language_id, info)
        result &= cls._validate_weekdays(language_id, info)
        result &= cls._validate_months(language_id, info)
        result &= cls._validate_units(language_id, info)
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
