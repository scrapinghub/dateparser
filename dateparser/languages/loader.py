import threading
from collections import OrderedDict
from collections.abc import Iterable, Iterator
from copy import deepcopy
from importlib import import_module
from itertools import zip_longest
from typing import Any

import regex as re

from ..data.languages_info import language_locale_dict, language_order
from .locale import Locale

LOCALE_SPLIT_PATTERN = re.compile(r"-(?=[A-Z0-9]+$)")


def _isvalidlocale(locale: str) -> bool:
    language = LOCALE_SPLIT_PATTERN.split(locale)[0]
    if language not in language_order:
        return False
    else:
        locales_list = language_locale_dict[language]
        if locale == language or locale in locales_list:
            return True
        else:
            return False


def _filter_valid_locales(locales: Iterable[str]) -> list[str]:
    return [locale for locale in locales if _isvalidlocale(locale)]


def _construct_locales(languages: Iterable[str], region: str) -> Iterable[str]:
    if region:
        possible_locales = [language + "-" + region for language in languages]
        locales: Iterable[str] = _filter_valid_locales(possible_locales)
    else:
        locales = languages
    return locales


class LocaleDataLoader:
    """Class that handles loading of locale instances."""

    _loaded_languages: dict[str, dict[str, Any]] = {}
    _loaded_locales: dict[str, Locale] = {}
    _load_lock = threading.Lock()

    def get_locale_map(
        self,
        languages: Iterable[str] | None = None,
        locales: Iterable[str] | None = None,
        region: str | None = None,
        use_given_order: bool = False,
        allow_conflicting_locales: bool = False,
    ) -> OrderedDict[str, Locale]:
        """
        Get an ordered mapping with locale codes as keys
        and corresponding locale instances as values.

        :param languages:
            A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
            If locales are not given, languages and region are
            used to construct locales to load.
        :type languages: list

        :param locales:
            A list of codes of locales which are to be loaded,
            e.g. ['fr-PF', 'qu-EC', 'af-NA']
        :type locales: list

        :param region:
            A region code, e.g. 'IN', '001', 'NE'.
            If locales are not given, languages and region are
            used to construct locales to load.
        :type region: str

        :param use_given_order:
            If True, the returned mapping is ordered in the order locales are given.
        :type use_given_order: bool

        :param allow_conflicting_locales:
            if True, locales with same language and different region can be loaded.
        :type allow_conflicting_locales: bool

        :return: ordered locale code to locale instance mapping
        """
        return OrderedDict(
            self._load_data(
                languages=languages,
                locales=locales,
                region=region,
                use_given_order=use_given_order,
                allow_conflicting_locales=allow_conflicting_locales,
            )
        )

    def get_locales(
        self,
        languages: Iterable[str] | None = None,
        locales: Iterable[str] | None = None,
        region: str | None = None,
        use_given_order: bool = False,
        allow_conflicting_locales: bool = False,
    ) -> Iterator[Locale]:
        """
        Yield locale instances.

        :param languages:
            A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
            If locales are not given, languages and region are
            used to construct locales to load.
        :type languages: list

        :param locales:
            A list of codes of locales which are to be loaded,
            e.g. ['fr-PF', 'qu-EC', 'af-NA']
        :type locales: list

        :param region:
            A region code, e.g. 'IN', '001', 'NE'.
            If locales are not given, languages and region are
            used to construct locales to load.
        :type region: str

        :param use_given_order:
            If True, the returned mapping is ordered in the order locales are given.
        :type use_given_order: bool

        :param allow_conflicting_locales:
            if True, locales with same language and different region can be loaded.
        :type allow_conflicting_locales: bool

        :yield: locale instances
        """
        for _, locale in self._load_data(
            languages=languages,
            locales=locales,
            region=region,
            use_given_order=use_given_order,
            allow_conflicting_locales=allow_conflicting_locales,
        ):
            yield locale

    def get_locale(self, shortname: str) -> Locale:
        """
        Get a locale instance.

        :param shortname:
            A locale code, e.g. 'fr-PF', 'qu-EC', 'af-NA'.
        :type shortname: str

        :return: locale instance
        """
        return list(self.get_locales(locales=[shortname]))[0]

    def _load_data(
        self,
        languages: Iterable[str] | None = None,
        locales: Iterable[str] | None = None,
        region: str | None = None,
        use_given_order: bool = False,
        allow_conflicting_locales: bool = False,
    ) -> Iterator[tuple[str, Locale]]:
        locale_dict: dict[str, tuple[str, ...]] = {}
        if locales:
            invalid_locales = []
            for locale in locales:
                split_locale = LOCALE_SPLIT_PATTERN.split(locale)
                if len(split_locale) == 1:
                    split_locale.append("")
                locale_dict[locale] = tuple(split_locale)
                if not _isvalidlocale(locale):
                    invalid_locales.append(locale)
            if invalid_locales:
                raise ValueError(
                    "Unknown locale(s): %s" % ", ".join(map(repr, invalid_locales))
                )

            if not allow_conflicting_locales:
                if len(set(locales)) > len({t[0] for t in locale_dict.values()}):
                    raise ValueError(
                        "Locales should not have same language and different region"
                    )

        else:
            if languages is None:
                languages = language_order
            unsupported_languages = set(languages) - set(language_order)
            if unsupported_languages:
                raise ValueError(
                    "Unknown language(s): %s"
                    % ", ".join(map(repr, unsupported_languages))
                )
            if region is None:
                region = ""
            locales = _construct_locales(languages, region)
            locale_dict.update(
                zip_longest(
                    locales, tuple(zip_longest(languages, [], fillvalue=region))
                )
            )

        if not use_given_order:
            locale_dict = dict(
                sorted(locale_dict.items(), key=lambda x: language_order.index(x[1][0]))
            )

        for shortname, lang_reg in locale_dict.items():
            with self._load_lock:
                if shortname not in self._loaded_locales:
                    lang, reg = lang_reg
                    if lang in self._loaded_languages:
                        locale_obj = Locale(
                            shortname,
                            language_info=deepcopy(self._loaded_languages[lang]),
                        )
                    else:
                        language_info = getattr(
                            import_module(
                                "dateparser.data.date_translation_data." + lang
                            ),
                            "info",
                        )
                        locale_obj = Locale(
                            shortname, language_info=deepcopy(language_info)
                        )
                        self._loaded_languages[lang] = language_info
                    # Store only once fully built so concurrent readers never see
                    # a half-initialised locale.
                    self._loaded_locales[shortname] = locale_obj
                locale_obj = self._loaded_locales[shortname]
            yield shortname, locale_obj


default_loader = LocaleDataLoader()
