from collections.abc import Set
from datetime import datetime

import regex as re

from dateparser.conf import apply_settings, check_settings
from dateparser.custom_language_detection.language_mapping import map_languages
from dateparser.date import DateDataParser
from dateparser.languages.loader import LocaleDataLoader
from dateparser.search.ngram_search import _NgramDateSearch
from dateparser.search.text_detection import FullTextLanguageDetector
from dateparser.utils.time_spans import detect_time_span, generate_time_span

RELATIVE_REG = re.compile("(ago|in|from now|tomorrow|today|yesterday)")


def date_is_relative(translation):
    return re.search(RELATIVE_REG, translation) is not None


def _add_time_span_results(results, text, settings):
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
    def __init__(self, loader):
        self.loader = loader

    def get_current_language(self, shortname):
        return self.loader.get_locale(shortname)

    def search(self, shortname, text, settings):
        language = self.get_current_language(shortname)
        result = language.translate_search(text, settings=settings)
        return result

    @staticmethod
    def set_relative_base(substring, already_parsed):
        if len(already_parsed) == 0:
            return substring, None

        i = len(already_parsed) - 1
        while already_parsed[i][1]:
            i -= 1
            if i == -1:
                return substring, None
        relative_base = already_parsed[i][0]["date_obj"]
        return substring, relative_base

    @staticmethod
    def _has_explicit_year(substring):
        """Return True if the substring contains a 4-digit year number."""
        return bool(re.search(r"\b\d{4}\b", substring))

    # Text joining two dates that reads as one range rather than two
    # unrelated mentions (e.g. "from 23th December UNTIL 8th January").
    # English-only: non-English ranges fall back to no rollover instead of
    # guessing, since translating this word list per-locale is out of scope.
    _RANGE_CONNECTOR_REG = re.compile(
        r"^[\s,]*(?:until|to|through|till|-|–|—)[\s,]*$", re.IGNORECASE
    )

    @staticmethod
    def _is_range_connector(connector):
        return bool(_ExactLanguageSearch._RANGE_CONNECTOR_REG.match(connector))

    @staticmethod
    def _adjust_year_for_rollovers(results, text):
        """Fix year-spanning date ranges parsed without explicit years.

        When two consecutive parsed dates are joined by a range connector
        (e.g. "from 23th December until 8th January") and go backwards
        chronologically, but neither substring contains an explicit year, the
        later-mentioned date belongs to the next calendar year and its year
        is incremented by one.

        The connector check (rather than a bare month comparison) is what
        keeps this from misfiring on unrelated date mentions in running text
        that merely happen to go backwards in month, e.g. "June 23 ... May
        31" listed as separate standalone dates within the same year.
        """
        if len(results) < 2:
            return results
        adjusted = list(results)
        cursor = 0
        positions = []
        for substring, _ in adjusted:
            start = text.find(substring, cursor)
            if start == -1:
                positions.append((None, None))
                continue
            end = start + len(substring)
            positions.append((start, end))
            cursor = end
        for i in range(1, len(adjusted)):
            prev_text, prev_date = adjusted[i - 1]
            curr_text, curr_date = adjusted[i]
            if _ExactLanguageSearch._has_explicit_year(
                prev_text
            ) or _ExactLanguageSearch._has_explicit_year(curr_text):
                continue
            prev_end = positions[i - 1][1]
            curr_start = positions[i][0]
            if prev_end is None or curr_start is None:
                continue
            connector = text[prev_end:curr_start]
            if not _ExactLanguageSearch._is_range_connector(connector):
                continue
            if curr_date.month < prev_date.month:
                adjusted[i] = (curr_text, curr_date.replace(year=curr_date.year + 1))
        return adjusted

    def choose_best_split(self, possible_parsed_splits, possible_substrings_splits):
        rating = []
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
            best_index, best_rating = min(
                enumerate(rating), key=lambda p: (p[1][1], p[1][0], p[1][2])
            )
        return (
            possible_parsed_splits[best_index],
            possible_substrings_splits[best_index],
        )

    def split_by(self, item, original, splitter):
        if item.count(splitter) <= 2:
            return [[item.split(splitter), original.split(splitter)]]

        item_all_split = item.split(splitter)
        original_all_split = original.split(splitter)
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

    def split_if_not_parsed(self, item, original):
        splitters = [",", "،", "——", "—", "–", ".", " "]
        possible_splits = []
        for splitter in splitters:
            if splitter in item and item.count(splitter) == original.count(splitter):
                possible_splits.extend(self.split_by(item, original, splitter))
        return possible_splits

    def parse_item(self, parser, item, translated_item, parsed, need_relative_base):
        relative_base = None
        item = item.replace("ngày", "")
        item = item.replace("am", "")
        parsed_item = parser.get_date_data(item)
        is_relative = date_is_relative(translated_item)

        if need_relative_base:
            item, relative_base = self.set_relative_base(item, parsed)

        if relative_base:
            parser._settings = parser._settings.replace(RELATIVE_BASE=relative_base)
            parsed_item = parser.get_date_data(item)
        return parsed_item, is_relative

    def parse_found_objects(self, parser, to_parse, original, translated, settings):
        parsed = []
        substrings = []
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
                substrings.append(original[i].strip(" .,:()[]-'"))
                continue

            possible_splits = self.split_if_not_parsed(item, original[i])
            if not possible_splits:
                continue

            possible_parsed = []
            possible_substrings = []
            for split_translated, split_original in possible_splits:
                current_parsed = []
                current_substrings = []
                if split_translated:
                    for j, jtem in enumerate(split_translated):
                        if len(jtem) <= 2:
                            continue
                        parsed_jtem, is_relative_jtem = self.parse_item(
                            parser,
                            jtem,
                            split_translated[j],
                            current_parsed,
                            need_relative_base,
                        )
                        current_parsed.append((parsed_jtem, is_relative_jtem))
                        current_substrings.append(split_original[j].strip(" .,:()[]-"))
                possible_parsed.append(current_parsed)
                possible_substrings.append(current_substrings)
            parsed_best, substrings_best = self.choose_best_split(
                possible_parsed, possible_substrings
            )
            for k in range(len(parsed_best)):
                if parsed_best[k][0]["date_obj"]:
                    parsed.append(parsed_best[k])
                    substrings.append(substrings_best[k])
        return parsed, substrings

    def search_parse(self, shortname, text, settings):
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
        )

        results = list(zip(substrings, [i[0]["date_obj"] for i in parsed]))
        results = self._adjust_year_for_rollovers(results, text)

        _add_time_span_results(results, text, settings)

        return results


class DateSearchWithDetection:
    """
    Class which executes language detection of string in a natural language, translation of a given string,
    search of substrings which represent date and/or time and parsing of these substrings.

    """

    def __init__(self):
        self.loader = LocaleDataLoader()
        self.available_language_map = self.loader.get_locale_map()
        self.search = _ExactLanguageSearch(self.loader)
        self.ngram_search = _NgramDateSearch()

    def _get_candidate_languages(self, detected_language, languages):
        candidates = []
        if detected_language:
            candidates.append(detected_language)

        if isinstance(languages, (list, tuple, Set)) and len(languages) > 1:
            candidates.extend(languages)

        seen = set()
        return [
            language
            for language in candidates
            if not (language in seen or seen.add(language))
        ]

    @apply_settings
    def detect_language(
        self, text, languages, settings=None, detect_languages_function=None
    ):
        if detect_languages_function and not languages:
            detected_languages = detect_languages_function(
                text,
                confidence_threshold=settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD,
            )
            detected_languages = (
                map_languages(detected_languages) or settings.DEFAULT_LANGUAGES
            )
            return detected_languages[0] if detected_languages else None

        if isinstance(languages, (list, tuple, Set)):
            if all([language in self.available_language_map for language in languages]):
                languages = [
                    self.available_language_map[language] for language in languages
                ]
            else:
                unsupported_languages = set(languages) - set(
                    self.available_language_map.keys()
                )
                raise ValueError(
                    "Unknown language(s): %s"
                    % ", ".join(map(repr, unsupported_languages))
                )
        elif languages is not None:
            raise TypeError(
                "languages argument must be a list (%r given)" % type(languages)
            )

        if languages:
            language_detector = FullTextLanguageDetector(languages=languages)
        else:
            language_detector = FullTextLanguageDetector(
                list(self.available_language_map.values())
            )

        detected_language = language_detector._best_language(text) or (
            settings.DEFAULT_LANGUAGES[0] if settings.DEFAULT_LANGUAGES else None
        )
        return detected_language

    @apply_settings
    def search_dates(
        self,
        text,
        languages=None,
        settings=None,
        detect_languages_function=None,
        strategy="split",
    ):
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
                'strategy must be "split" or "ngram" (%r given)' % strategy
            )

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

    def preprocess_text(self, text, languages):
        """Preprocess text to handle language-specific quirks."""
        if languages and "ru" in languages:
            # Replace "с" (from) before numbers with a placeholder
            text = re.sub(r"\bс\s+(?=\d)", "[FROM] ", text)
        return text
