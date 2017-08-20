# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from importlib import import_module
from six.moves import zip_longest
import regex as re
from copy import deepcopy

from ..data import language_order, language_locale_dict
from .locale import Locale
from ..utils import convert_to_unicode

LOCALE_SPLIT_PATTERN = re.compile(r'-(?=[A-Z0-9]+$)')


def _isvalidlocale(locale):
    language = LOCALE_SPLIT_PATTERN.split(locale)[0]
    if language not in language_order:
        return False
    else:
        locales_list = language_locale_dict[language]
        if locale == language or locale in locales_list:
            return True
        else:
            return False


def _filter_valid_locales(locales):
    return [locale for locale in locales if _isvalidlocale(locale)]


def _construct_locales(languages, region):
    if region:
        possible_locales = [language + '-' + region for language in languages]
        locales = _filter_valid_locales(possible_locales)
    else:
        locales = languages
    return locales


class LocaleDataLoader(object):
    _loaded_languages = {}
    _loaded_locales = {}

    def get_locale_map(self, languages=None, locales=None, region=None,
                       use_given_order=False, allow_conflicting_locales=False):
        return OrderedDict(self._load_data(
            languages=languages, locales=locales, region=region, use_given_order=use_given_order,
            allow_conflicting_locales=allow_conflicting_locales))

    def get_locales(self, languages=None, locales=None, region=None,
                    use_given_order=False, allow_conflicting_locales=False):
        for _, locale in self._load_data(
                languages=languages, locales=locales, region=region,
                use_given_order=use_given_order,
                allow_conflicting_locales=allow_conflicting_locales):
            yield locale

    def get_locale(self, shortname):
        return list(self.get_locales(locales=[shortname]))[0]

    def _load_data(self, languages=None, locales=None, region=None,
                   use_given_order=False, allow_conflicting_locales=False):
        locale_dict = OrderedDict()
        if locales:
            invalid_locales = []
            for locale in locales:
                lang_reg = LOCALE_SPLIT_PATTERN.split(locale)
                if len(lang_reg) == 1:
                    lang_reg.append('')
                locale_dict[locale] = tuple(lang_reg)
                if not _isvalidlocale(locale):
                    invalid_locales.append(locale)
            if invalid_locales:
                raise ValueError("Unknown locale(s): %s"
                                 % ', '.join(map(repr, invalid_locales)))

            if not allow_conflicting_locales:
                if len(set(locales)) > len(set([t[0] for t in locale_dict.values()])):
                    raise ValueError("Locales should not have same language and different region")

        else:
            if languages is None:
                languages = language_order
            unsupported_languages = set(languages) - set(language_order)
            if unsupported_languages:
                raise ValueError("Unknown language(s): %s"
                                 % ', '.join(map(repr, unsupported_languages)))
            if region is None:
                region = ''
            locales = _construct_locales(languages, region)
            locale_dict.update(zip_longest(locales,
                               tuple(zip_longest(languages, [], fillvalue=region))))

        if not use_given_order:
            locale_dict = OrderedDict(sorted(locale_dict.items(),
                                      key=lambda x: language_order.index(x[1][0])))

        for shortname, lang_reg in locale_dict.items():
            if shortname not in self._loaded_locales:
                lang, reg = lang_reg
                if lang in self._loaded_languages:
                    locale = Locale(shortname, language_info=deepcopy(self._loaded_languages[lang]))
                    self._loaded_locales[shortname] = locale
                else:
                    language_info = getattr(
                        import_module('dateparser.data.date_translation_data.' + lang), 'info')
                    language_info = convert_to_unicode(language_info)
                    locale = Locale(shortname, language_info=deepcopy(language_info))
                    self._loaded_languages[lang] = language_info
                    self._loaded_locales[shortname] = locale
            yield shortname, self._loaded_locales[shortname]


default_loader = LocaleDataLoader()
