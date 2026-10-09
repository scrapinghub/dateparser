from collections.abc import Callable, Iterable, Sequence
from collections.abc import Set as AbstractSet
from datetime import datetime
from itertools import chain
from typing import Any, TypedDict

import regex as re

from dateparser.conf import Settings, apply_settings, check_settings
from dateparser.custom_language_detection.language_mapping import map_languages
from dateparser.date import DateData, DateDataParser
from dateparser.freshness_date_parser import _UNITS
from dateparser.languages.loader import LocaleDataLoader
from dateparser.languages.locale import PUNCTUATION, Locale
from dateparser.search.ngram_search import _NgramDateSearch
from dateparser.search.text_detection import FullTextLanguageDetector
from dateparser.utils.time_spans import detect_time_span, generate_time_span

RELATIVE_REG = re.compile("(ago|in|from now|tomorrow|today|yesterday)")

# How a relative expression looks once translated. A single word such as "today"
# turns into several words ("0 day ago"), which is why the translation of a
# chunk can hold more words than the text it was translated from.
TRANSLATED_RELATIVE_REG = re.compile(
    rf"\bin \d+ (?:{_UNITS})s?\b|\b\d+ (?:{_UNITS})s? ago\b"
)


_WEEKDAY_MODIFIERS = {"last", "this", "next"}

_MAX_TRAILING_WORDS = 3
"""Words after a relative expression, e.g. "5 pm" after "in 1 day", that
:meth:`_ExactLanguageSearch.split_by_relative_expression` keeps with it."""


def _is_weekday_modifier(word: str) -> bool:
    return word.strip().strip(PUNCTUATION) in _WEEKDAY_MODIFIERS


def _has_weekday_modifier(text: str) -> bool:
    return any(_is_weekday_modifier(word) for word in text.split())


def _clean_substring(substring: str, skip: AbstractSet[str]) -> str:
    """Strip the punctuation around *substring*, including that of *skip*,
    e.g. "/"."""
    while True:
        substring = substring.strip(" .,:()[]-'\"")
        first, _, rest = substring.partition(" ")
        if rest and first in skip and not any(char.isalnum() for char in first):
            substring = rest
            continue
        rest, _, last = substring.rpartition(" ")
        if rest and last in skip and not any(char.isalnum() for char in last):
            substring = rest
            continue
        return substring


def _trim_connectors(
    text: str, substrings: Sequence[str], skip: AbstractSet[str]
) -> list[str]:
    """Strip the words of *skip* that end each of *substrings* followed right
    away in *text* by the next one, e.g. "and" in "yesterday and"."""
    positions = []
    start = 0
    for substring in substrings:
        position = text.find(substring, start)
        positions.append(position)
        if position != -1:
            start = position + len(substring)
    trimmed = list(substrings)
    for index, (substring, position, next_position) in enumerate(
        zip(substrings, positions, positions[1:], strict=False)
    ):
        if position == -1 or next_position == -1:
            continue
        if text[position + len(substring) : next_position].strip(" ([{\"'"):
            # Words such as German "Uhr" are skipped as well, and are part of
            # the date unless another date follows them.
            continue
        words = substring.split(" ")
        while len(words) > 1 and words[-1].lower() in skip:
            words.pop()
        trimmed[index] = " ".join(words)
    return trimmed


def _join_weekday_modifiers(
    item_units: Sequence[str], original_units: Sequence[str], separator: str
) -> tuple[list[str], list[str]]:
    """Join each weekday modifier of *item_units* to the unit after it, and
    the matching *original_units* likewise, so that a group of units cannot
    separate a modifier from its weekday."""
    item_joined: list[str] = []
    original_joined: list[str] = []
    after_modifier = False
    for item_unit, original_unit in zip(item_units, original_units, strict=True):
        if after_modifier:
            item_joined[-1] += separator + item_unit
            original_joined[-1] += separator + original_unit
        else:
            item_joined.append(item_unit)
            original_joined.append(original_unit)
        after_modifier = _is_weekday_modifier(item_unit)
    return item_joined, original_joined


class _SearchResult(TypedDict):
    Language: str | None
    Dates: list[tuple[str, datetime]] | None


def date_is_relative(translation: str) -> bool:
    return re.search(RELATIVE_REG, translation) is not None


def _add_time_span_results(
    results: list[tuple[str, datetime]], text: str, settings: Settings
) -> list[tuple[str, datetime]]:
    """Append time span start/end dates if RETURN_TIME_SPAN is enabled."""
    if getattr(settings, "RETURN_TIME_SPAN", False):
        span_info = detect_time_span(text)
        if span_info:
            base_date = getattr(settings, "RELATIVE_BASE", None) or datetime.now()
            start_date, end_date = generate_time_span(span_info, base_date, settings)
            matched_text = span_info["matched_text"]
            results.append((matched_text + " (start)", start_date))
            results.append((matched_text + " (end)", end_date))
    return results


class _ExactLanguageSearch:
    def __init__(self, loader: LocaleDataLoader) -> None:
        self.loader = loader

    def get_current_language(self, shortname: str) -> Locale:
        return self.loader.get_locale(shortname)

    def search(
        self, shortname: str, text: str, settings: Settings
    ) -> tuple[list[str], list[str]]:
        language = self.get_current_language(shortname)
        return language.translate_search(text, settings=settings)

    @staticmethod
    def set_relative_base(
        substring: str, already_parsed: Sequence[tuple[DateData, bool]]
    ) -> tuple[str, datetime | None]:
        if len(already_parsed) == 0:
            return substring, None

        i = len(already_parsed) - 1
        while already_parsed[i][1] or already_parsed[i][0]["date_obj"] is None:
            i -= 1
            if i == -1:
                return substring, None
        relative_base = already_parsed[i][0]["date_obj"]
        return substring, relative_base

    def choose_best_split(
        self,
        possible_parsed_splits: Sequence[list[tuple[DateData, bool]]],
        possible_substrings_splits: Sequence[list[str]],
    ) -> tuple[list[tuple[DateData, bool]], list[str]]:
        rating: list[list[float]] = []
        for i in range(len(possible_parsed_splits)):
            num_substrings = len(possible_substrings_splits[i])
            num_substrings_without_digits = 0
            not_parsed = 0
            for j, item in enumerate(possible_parsed_splits[i]):
                if item[0]["date_obj"] is None:
                    not_parsed += 1
                if not any(char.isdigit() for char in possible_substrings_splits[i][j]):
                    num_substrings_without_digits += 1
            rating.append(
                [
                    num_substrings,
                    0
                    if not_parsed == 0
                    else (float(not_parsed) / float(num_substrings)),
                    0
                    if num_substrings_without_digits == 0
                    else (float(num_substrings_without_digits) / float(num_substrings)),
                ]
            )
            best_index, _best_rating = min(
                enumerate(rating), key=lambda p: (p[1][1], p[1][0], p[1][2])
            )
        return (
            possible_parsed_splits[best_index],
            possible_substrings_splits[best_index],
        )

    def split_by(
        self, item: str, original: str, splitter: str
    ) -> list[list[list[str]]]:
        item_all_split, original_all_split = _join_weekday_modifiers(
            item.split(splitter), original.split(splitter), splitter
        )
        if len(item_all_split) <= 3:
            return [[item_all_split, original_all_split]]

        all_possible_splits = [[item_all_split, original_all_split]]
        for i in range(2, 4):
            item_partially_split = []
            original_partially_split = []
            for j in range(0, len(item_all_split), i):
                item_join = splitter.join(item_all_split[j : j + i])
                original_join = splitter.join(original_all_split[j : j + i])
                item_partially_split.append(item_join)
                original_partially_split.append(original_join)
            all_possible_splits.append([item_partially_split, original_partially_split])
        return all_possible_splits

    def split_by_relative_expression(
        self,
        parser: DateDataParser,
        item: str,
        original: str,
        language: Locale,
        settings: Settings,
    ) -> list[list[list[str]]]:
        """Split a chunk into a relative expression and the date next to it.

        A word translated into a multi-word relative expression gives the
        translation more separators than the text it was translated from, which
        is what keeps the splitters above from lining the two up. Cutting the
        chunk in two where the expression starts or ends lines them up again,
        once the words the expression part was translated from are known and
        the other part turns out to be the date it was written next to.
        """
        if not TRANSLATED_RELATIVE_REG.search(item):
            return []
        words = original.split()
        # Skipped words, e.g. "and", have no counterpart in the translation.
        kept = [
            index
            for index, word in enumerate(words)
            if language.translate(word, settings=settings).strip()
        ]
        possible_splits: list[list[list[str]]] = []
        for match in TRANSLATED_RELATIVE_REG.finditer(item):
            # The expression starts or ends the chunk, which leaves a single
            # boundary to cut it at. The date part keeps one word per original
            # one, the other part holds the expression, which may be translated
            # from several words, e.g. "next week", and may have a few more
            # words after it, e.g. "tomorrow at 5pm", so a date after it starts
            # at the first of those words that lines up.
            cuts = []
            if len(item[match.end() :].split()) <= _MAX_TRAILING_WORDS:
                cuts.append((match.start(), True))
            if not item[: match.start()].strip():
                later_spaces = [
                    index
                    for index, char in enumerate(item)
                    if char == " " and index > match.end()
                ]
                cuts.append((match.end(), False))
                cuts.extend(
                    (index, False) for index in later_spaces[:_MAX_TRAILING_WORDS]
                )
            date_after_found = False
            for cut, date_first in cuts:
                parts = [item[:cut].strip(), item[cut:].strip()]
                if not all(parts) or (date_after_found and not date_first):
                    continue
                date, expression_part = parts if date_first else parts[::-1]
                size = len(date.split())
                if size >= len(kept):
                    continue
                boundary = size if date_first else len(kept) - size
                # Skipped words between the two parts, e.g. "and", usually
                # belong to neither, but some only translate as part of the
                # expression, e.g. Arabic "خلال" ("within") as "in".
                gap_start = kept[boundary - 1] + 1
                gap_end = kept[boundary]
                for expression_start, expression_end in (
                    (gap_end, len(words)) if date_first else (0, gap_start),
                    (gap_start, len(words)) if date_first else (0, gap_end),
                ):
                    expression = " ".join(words[expression_start:expression_end])
                    translation = " ".join(
                        chain.from_iterable(
                            language.translate_search(expression, settings=settings)[0]
                        )
                    )
                    if translation.replace(" ", "") == expression_part.replace(" ", ""):
                        break
                else:
                    # The words next to the boundary are not the ones the
                    # expression part was translated from: some other word of
                    # the chunk also changed the word count, and only made the
                    # one above add up. Spaces are ignored because a whole
                    # chunk keeps "5pm" together, which alone gives "5 pm".
                    continue
                if any(
                    parser.get_date_data(part)["date_obj"] is None for part in parts
                ):
                    # There is no date next to the expression, so cutting the
                    # chunk would report the expression and drop the rest of
                    # it, or the words after the expression are not part of it.
                    continue
                date_original = (
                    " ".join(words[: kept[boundary - 1] + 1])
                    if date_first
                    else " ".join(words[kept[boundary] :])
                )
                if not date_first:
                    date_after_found = True
                possible_splits.append(
                    [
                        parts,
                        [date_original, expression]
                        if date_first
                        else [expression, date_original],
                    ]
                )
        return possible_splits

    def split_around_skipped_words(
        self, item: str, original: str, language: Locale, settings: Settings
    ) -> list[list[list[str]]]:
        """Split a chunk by spaces, ignoring the words its translation skips.

        Words like "and" or "of" are left out of the translation but not of
        the original text, so splitting both by spaces does not line them up.
        Each part of the original text spans from its first word that is not
        skipped to its last one.
        """
        words = original.split()
        kept = []
        for index, word in enumerate(words):
            translation = language.translate(word, settings=settings).split()
            if len(translation) > 1:
                return []
            if translation:
                kept.append(index)
        item_words = item.split()
        if len(kept) == len(words) or len(kept) != len(item_words):
            return []
        units: list[list[int]] = []
        for k in range(len(kept)):
            # A weekday modifier and its weekday make a single unit, which also
            # takes the word after "of", e.g. "last friday of march".
            if k and (
                _is_weekday_modifier(item_words[k - 1])
                or (
                    k > 1
                    and _is_weekday_modifier(item_words[k - 2])
                    and "of"
                    in (word.lower() for word in words[kept[k - 1] + 1 : kept[k]])
                )
            ):
                units[-1].append(k)
            else:
                units.append([k])
        sizes = [1] if len(units) <= 3 else [1, 2, 3]
        possible_splits = []
        for size in sizes:
            groups = [
                [*chain.from_iterable(units[start : start + size])]
                for start in range(0, len(units), size)
            ]
            possible_splits.append(
                [
                    [
                        " ".join(item_words[group[0] : group[-1] + 1])
                        for group in groups
                    ],
                    [
                        " ".join(words[kept[group[0]] : kept[group[-1]] + 1])
                        for group in groups
                    ],
                ]
            )
        return possible_splits

    def split_off_leading_number(
        self, parser: DateDataParser, item: str, original: str
    ) -> list[list[list[str]]]:
        """Split a chunk that starts with a number into that number and the
        rest, to find a date written after a number that is not part of it,
        e.g. the decimals of “-58.5” before “06 Mar 2009”."""
        number, _, rest = item.partition(" ")
        original_number, _, original_rest = original.partition(" ")
        if (
            not number.isdigit()
            or number != original_number
            or parser.get_date_data(rest)["date_obj"] is None
        ):
            return []
        return [[[number, rest], [original_number, original_rest]]]

    def split_if_not_parsed(
        self,
        parser: DateDataParser,
        item: str,
        original: str,
        language: Locale,
        settings: Settings,
    ) -> list[list[list[str]]]:
        splitters = [",", "،", "——", "—", "–", ".", " "]
        possible_splits = self.split_off_leading_number(parser, item, original)
        misaligned = False
        for splitter in splitters:
            if splitter not in item or item.count(splitter) != original.count(splitter):
                continue
            if (
                splitter == " "
                and item != original
                and any(
                    not language.translate(word, settings=settings).strip()
                    for word in original.split()
                )
            ):
                # A skipped word, e.g. "and", has no counterpart in the
                # translation, so the words of both only line up by chance,
                # unless the language is searched untranslated.
                misaligned = True
                continue
            possible_splits.extend(self.split_by(item, original, splitter))
        if not possible_splits or misaligned:
            # Only when no splitter lines up, or skipped words keep spaces from
            # doing so, so that a chunk which already splits keeps being split
            # exactly the way it is split today.
            possible_splits += self.split_by_relative_expression(
                parser, item, original, language, settings
            ) or self.split_around_skipped_words(item, original, language, settings)
        return possible_splits

    def parse_item(
        self,
        parser: DateDataParser,
        item: str,
        translated_item: str,
        parsed: Sequence[tuple[DateData, bool]],
        need_relative_base: bool,
    ) -> tuple[DateData, bool]:
        relative_base = None
        item = item.replace("ngày", "")
        item = item.replace("am", "")
        parsed_item = parser.get_date_data(item)
        is_relative = date_is_relative(translated_item)

        # A weekday modifier, e.g. "last" in "last friday", is relative to the
        # current date, not to a date found earlier in the text.
        if need_relative_base and not _has_weekday_modifier(item):
            item, relative_base = self.set_relative_base(item, parsed)

        if relative_base:
            settings = parser._settings
            parser._settings = settings.replace(RELATIVE_BASE=relative_base)
            try:
                parsed_item = parser.get_date_data(item)
            finally:
                parser._settings = settings
        return parsed_item, is_relative

    def parse_found_objects(
        self,
        parser: DateDataParser,
        to_parse: Sequence[str],
        original: Sequence[str],
        translated: Sequence[str],
        settings: Settings,
        language: Locale,
        already_parsed: Sequence[tuple[DateData, bool]] = (),
    ) -> tuple[list[tuple[DateData, bool]], list[str]]:
        parsed: list[tuple[DateData, bool]] = list(already_parsed)
        substrings = []
        skip = {word.lower() for word in language.info.get("skip", [])}
        need_relative_base = True
        if settings.RELATIVE_BASE:
            need_relative_base = False
        for i, item in enumerate(to_parse):
            if len(item) <= 2:
                continue

            parsed_item, is_relative = self.parse_item(
                parser, item, translated[i], parsed, need_relative_base
            )
            if parsed_item["date_obj"]:
                parsed.append((parsed_item, is_relative))
                substrings.append(_clean_substring(original[i], skip))
                continue

            possible_splits = self.split_if_not_parsed(
                parser, item, original[i], language, settings
            )
            if not possible_splits:
                continue

            possible_parsed: list[list[tuple[DateData, bool]]] = []
            possible_substrings: list[list[str]] = []
            possible_parts: list[list[tuple[str, str]]] = []
            for split_translated, split_original in possible_splits:
                current_parsed: list[tuple[DateData, bool]] = []
                current_substrings: list[str] = []
                current_parts: list[tuple[str, str]] = []
                for j, jtem in enumerate(split_translated):
                    if len(jtem) <= 2:
                        continue
                    parsed_jtem, is_relative_jtem = self.parse_item(
                        parser,
                        jtem,
                        jtem,
                        [*parsed, *current_parsed],
                        need_relative_base,
                    )
                    current_parsed.append((parsed_jtem, is_relative_jtem))
                    current_substrings.append(_clean_substring(split_original[j], skip))
                    current_parts.append((jtem, split_original[j]))
                possible_parsed.append(current_parsed)
                possible_substrings.append(current_substrings)
                possible_parts.append(current_parts)
            parsed_best, substrings_best = self.choose_best_split(
                possible_parsed, possible_substrings
            )
            best_index = next(
                index
                for index, current_parsed in enumerate(possible_parsed)
                if current_parsed is parsed_best
            )
            for parsed_part, substring, (part, original_part) in zip(
                parsed_best, substrings_best, possible_parts[best_index], strict=True
            ):
                if parsed_part[0]["date_obj"]:
                    parsed.append(parsed_part)
                    substrings.append(substring)
                    continue
                if part == item or not _has_weekday_modifier(part):
                    continue
                # A part can join several dates, e.g. "last monday and next
                # sunday" after splitting by commas, so split it again.
                sub_parsed, sub_substrings = self.parse_found_objects(
                    parser,
                    [part],
                    [original_part],
                    [part],
                    settings,
                    language,
                    already_parsed=parsed,
                )
                parsed.extend(sub_parsed)
                substrings.extend(sub_substrings)
        return parsed[len(already_parsed) :], substrings

    def search_parse(
        self, shortname: str, text: str, settings: Settings
    ) -> list[tuple[str, datetime]]:
        language = self.get_current_language(shortname)
        translated, original = self.search(shortname, text, settings)
        bad_translate_with_search = [
            "vi",
            "hu",
        ]  # splitting done by spaces and some dictionary items contain spaces
        if shortname not in bad_translate_with_search:
            languages = ["en"]
            to_parse = translated
        else:
            languages = [shortname]
            to_parse = original

        parser = DateDataParser(languages=languages, settings=settings)
        parsed, substrings = self.parse_found_objects(
            parser=parser,
            to_parse=to_parse,
            original=original,
            translated=translated,
            settings=settings,
            language=language,
        )

        skip = {word.lower() for word in language.info.get("skip", [])}
        substrings = _trim_connectors(text, substrings, skip)
        results = list(zip(substrings, [i[0]["date_obj"] for i in parsed], strict=True))

        _add_time_span_results(results, text, settings)

        return results


class DateSearchWithDetection:
    """
    Class which executes language detection of string in a natural language, translation of a given string,
    search of substrings which represent date and/or time and parsing of these substrings.

    """

    def __init__(self) -> None:
        self.loader = LocaleDataLoader()
        self.available_language_map = self.loader.get_locale_map()
        self.search = _ExactLanguageSearch(self.loader)
        self.ngram_search = _NgramDateSearch()

    def _get_candidate_languages(
        self, detected_language: str | None, languages: Iterable[str] | None
    ) -> list[str]:
        candidates = []
        if detected_language:
            candidates.append(detected_language)

        if isinstance(languages, (list, tuple, AbstractSet)) and len(languages) > 1:
            candidates.extend(languages)

        return list(dict.fromkeys(candidates))

    @apply_settings
    def detect_language(
        self,
        text: str,
        languages: Iterable[str] | None,
        settings: Settings | dict[str, Any] | None = None,
        detect_languages_function: Callable[..., list[str]] | None = None,
    ) -> str | None:
        assert isinstance(settings, Settings)
        if detect_languages_function and not languages:
            detected_languages = detect_languages_function(
                text,
                confidence_threshold=settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD,
            )
            detected_languages = (
                map_languages(detected_languages) or settings.DEFAULT_LANGUAGES
            )
            return detected_languages[0] if detected_languages else None

        locales = None
        if isinstance(languages, (list, tuple, AbstractSet)):
            if all(language in self.available_language_map for language in languages):
                locales = [
                    self.available_language_map[language] for language in languages
                ]
            else:
                unsupported_languages = set(languages) - set(
                    self.available_language_map.keys()
                )
                raise ValueError(
                    f"Unknown language(s): {', '.join(map(repr, unsupported_languages))}"
                )
        elif languages is not None:
            raise TypeError(
                f"languages argument must be a list ({type(languages)!r} given)"
            )

        if locales:
            language_detector = FullTextLanguageDetector(languages=locales)
        else:
            language_detector = FullTextLanguageDetector(
                list(self.available_language_map.values())
            )

        return language_detector._best_language(text) or (
            settings.DEFAULT_LANGUAGES[0] if settings.DEFAULT_LANGUAGES else None
        )

    @apply_settings
    def search_dates(
        self,
        text: str,
        languages: Iterable[str] | None = None,
        settings: Settings | dict[str, Any] | None = None,
        detect_languages_function: Callable[..., list[str]] | None = None,
        strategy: str = "split",
    ) -> _SearchResult:
        """
        Find all substrings of the given string which represent date and/or time and parse them.

        :param text:
            A string in a natural language which may contain date and/or time expressions.
        :type text: str

        :param languages:
            A list of two letters language codes.e.g. ['en', 'es']. If languages are given, it will not attempt
            to detect the language.
        :type languages: list

        :param settings:
               Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
        :type settings: dict

        :param detect_languages_function:
               A function for language detection that takes as input a `text` and a `confidence_threshold`,
               returns a list of detected language codes.
        :type detect_languages_function: function

        :param strategy:
               The search strategy to use: "split" (default) translates the text and splits it
               into chunks that are likely to contain dates, while "ngram" tries to parse the
               longest possible sequences of tokens as dates. The "ngram" strategy tends to
               produce more predictable results, at the cost of more parse attempts.
        :type strategy: str

        :return: a dict mapping keys to two letter language code and a list of tuples of pairs:
                substring representing date expressions and corresponding :mod:`datetime.datetime` object.
            For example:
            {'Language': 'en', 'Dates': [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]}
            If language of the string isn't recognised returns:
            {'Language': None, 'Dates': None}
        :raises: ValueError - Unknown Language
        """
        if strategy not in ("split", "ngram"):
            raise ValueError(
                f'strategy must be "split" or "ngram" ({strategy!r} given)'
            )

        assert isinstance(settings, Settings)
        check_settings(settings)

        language_shortname = self.detect_language(
            text=text,
            languages=languages,
            settings=settings,
            detect_languages_function=detect_languages_function,
        )

        candidate_languages = self._get_candidate_languages(
            language_shortname, languages
        )
        if not candidate_languages:
            return {"Language": None, "Dates": None}

        if strategy == "ngram":
            dates = self.ngram_search.search_parse(
                candidate_languages, text, settings=settings
            )
            _add_time_span_results(dates, text, settings)
            return {"Language": language_shortname, "Dates": dates}

        for candidate_language in candidate_languages:
            dates = self.search.search_parse(
                candidate_language, text, settings=settings
            )
            if dates:
                return {"Language": candidate_language, "Dates": dates}

        return {
            "Language": language_shortname,
            "Dates": [],
        }

    def preprocess_text(self, text: str, languages: Iterable[str] | None) -> str:
        """Preprocess text to handle language-specific quirks."""
        if languages and "ru" in languages:
            # Replace "с" (from) before numbers with a placeholder
            text = re.sub(r"\bс\s+(?=\d)", "[FROM] ", text)
        return text
