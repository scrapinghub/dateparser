import re
from typing import List, Dict

from dateparser.conf import apply_settings, Settings
from dateparser.date import DateDataParser
from dateparser.search_dates.languages import SearchLanguages

_drop_words = {'on', 'of'}  # cause annoying false positives
_bad_date_re = re.compile(
    # whole dates we black-list (can still be parts of valid dates)
    "^("
    + "|".join(
        [
            r"\d{1,3}",  # less than 4 digits
            r"#\d+",  # this is a sequence number
            # some common false positives below
            r"[-/.]+",  # bare separators parsed as current date
            r"\w\.?",  # one letter (with optional dot)
            "an",
        ]
    )
    + ")$"
)

_secondary_splitters = [',', '،', '——', '—', '–', '.', ' ']  # are used if no date object is found


def _get_relative_base(already_parsed):
    if already_parsed:
        return already_parsed[-1][1]
    return None


def _create_splits(text):
    splited_objects = text.split()
    splited_objects = [p for p in splited_objects if p and p not in _drop_words]
    return splited_objects


def _create_joined_parse(text, max_join=7, sort_ascending=False):
    split_objects = _create_splits(text=text)
    joint_objects = []
    for i in range(len(split_objects)):
        for j in reversed(range(min(max_join, len(split_objects) - i))):
            x = " ".join(split_objects[i:i + j + 1])
            if _bad_date_re.match(x):
                continue
            if not len(x) > 2:
                continue
            joint_objects.append(x)

    if sort_ascending:
        joint_objects = sorted(joint_objects, key=len)

    return joint_objects


def _get_accurate_return_text(text, parser, datetime_object):
    text_candidates = _create_joined_parse(text=text, sort_ascending=True)
    for text_candidate in text_candidates:
        if parser.get_date_data(text_candidate).date_obj == datetime_object:
            return text_candidate


def _joint_parse(text, parser, translated=None, deep_search=True, accurate_return_text=False, data_carry=None):
    if not text:
        return data_carry

    elif not len(text) > 2:
        return data_carry

    elif translated and len(translated) <= 2:
        return data_carry

    reduced_text_candidate = None
    secondary_split_made = False
    returnable_objects = data_carry or []
    joint_based_search_dates = _create_joined_parse(text=text)
    for date_object_candidate in joint_based_search_dates:
        parsed_date_object = parser.get_date_data(date_object_candidate)
        if parsed_date_object.date_obj:
            if accurate_return_text:
                date_object_candidate = _get_accurate_return_text(
                    text=date_object_candidate, parser=parser, datetime_object=parsed_date_object.date_obj
                )

            returnable_objects.append(
                (date_object_candidate.strip(" .,:()[]-'"), parsed_date_object.date_obj)
            )
            start_index = text.find(date_object_candidate)
            end_index = start_index + len(date_object_candidate)
            if start_index < 0:
                break
            reduced_text_candidate = text[:start_index] + text[end_index:]
            break
        else:
            for splitter in _secondary_splitters:
                secondary_split = re.split('(?<! )[' + splitter + ']+(?! )', date_object_candidate)
                if secondary_split and len(secondary_split) > 1:
                    reduced_text_candidate = " ".join(secondary_split)
                    secondary_split_made = True

    if (deep_search or secondary_split_made) and not text == reduced_text_candidate:
        if reduced_text_candidate and len(reduced_text_candidate) > 2:
            returnable_objects = _joint_parse(
                text=reduced_text_candidate,
                parser=parser,
                data_carry=returnable_objects
            )

    return returnable_objects


class DateSearch:
    def __init__(self, make_joints_parse=True, default_language="en"):
        self.make_joints_parse = make_joints_parse
        self.default_language = default_language

        self.search_languages = SearchLanguages()

    @apply_settings
    def search_parse(
        self, text, language_shortname, settings, limit_date_search_results=None
    ) -> List[tuple]:

        returnable_objects = []
        parser = DateDataParser(languages=[language_shortname], settings=settings)
        translated, original = self.search_languages.translate_objects(
            language_shortname, text, settings
        )

        for index, original_object in enumerate(original):
            if limit_date_search_results and returnable_objects:
                if len(returnable_objects) == limit_date_search_results:
                    break

            if not len(original_object) > 2:
                continue

            if not settings.RELATIVE_BASE:
                relative_base = _get_relative_base(already_parsed=returnable_objects)
                if relative_base:
                    parser._settings.RELATIVE_BASE = relative_base

            if self.make_joints_parse:
                joint_based_search_dates = _joint_parse(
                    text=original_object, parser=parser, translated=translated[index]
                )
                if joint_based_search_dates:
                    returnable_objects.extend(joint_based_search_dates)
            else:
                parsed_date_object = parser.get_date_data(original_object)
                if parsed_date_object.date_obj:
                    returnable_objects.append(
                        (original_object.strip(" .,:()[]-'"), parsed_date_object.date_obj)
                    )

        parser._settings = Settings()
        return returnable_objects

    @apply_settings
    def search_dates(
        self, text, languages=None, limit_date_search_results=None, settings=None
    ) -> Dict:
        """
        Find all substrings of the given string which represent date and/or time and parse them.

        :param text:
            A string in a natural language which may contain date and/or time expressions.
        :type text: str

        :param languages:
            A list of two letters language codes.e.g. ['en', 'es']. If languages are given, it will not attempt
            to detect the language.
        :type languages: list

        :param limit_date_search_results:
            A int which sets maximum results to be returned.
        :type limit_date_search_results: int

        :param settings:
               Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
        :type settings: dict

        :return: a dict mapping keys to two letter language code and a list of tuples of pairs:
                substring representing date expressions and corresponding :mod:`datetime.datetime` object.
            For example:
            {'Language': 'en', 'Dates': [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]}
            If language of the string isn't recognised returns:
            {'Language': None, 'Dates': None}
        :raises: ValueError - Unknown Language
        """

        language_shortname = (
            self.search_languages.detect_language(text=text, languages=languages)
            or self.default_language
        )

        if not language_shortname:
            return {"Language": None, "Dates": None}
        return {
            "Language": language_shortname,
            "Dates": self.search_parse(
                text=text,
                language_shortname=language_shortname,
                limit_date_search_results=limit_date_search_results,
                settings=settings,
            ),
        }
