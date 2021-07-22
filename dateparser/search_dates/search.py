import re
from typing import List, Dict
import string

from dateparser.conf import apply_settings
from dateparser.date import DateDataParser
from dateparser.search_dates.languages import SearchLanguages

_excape_chars = re.escape(string.punctuation)
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


def _final_text_clean(parsed_objects):
    # THIS IS TEMPORARY FIX
    final_returnable_objects = []

    for candidate in parsed_objects:
        original_object, date_obj = candidate

        first_two_chars = re.sub(r'[' + _excape_chars + ']', '', original_object[:2])
        last_two_chars = re.sub(r'[' + _excape_chars + ']', '', original_object[-2:])

        if original_object[0].isdigit():
            first_two_chars = original_object[:2]

        if original_object[-1].isdigit():
            last_two_chars = last_two_chars[:2]


        original_object = first_two_chars + original_object[2:-2] + last_two_chars

        final_returnable_objects.append(
            (original_object.strip(), date_obj)
        )

    return final_returnable_objects


def _create_joined_parse(text, max_join=7, sort_ascending=False):
    split_objects = text.split()
    joint_objects = []
    for i in range(len(split_objects)):
        for j in reversed(range(min(max_join, len(split_objects) - i))):
            x = " ".join(split_objects[i:i + j + 1])
            if _bad_date_re.match(x):
                continue
            if not len(x) >= 4:
                continue
            joint_objects.append(x)

    if sort_ascending:
        joint_objects = sorted(joint_objects, key=len)

    return joint_objects


def _get_accurate_return_text(text, parser, datetime_object):
    # THIS METHOD IS STILL BEING TESTED
    text_candidates = _create_joined_parse(text=text, sort_ascending=True)
    for text_candidate in text_candidates:
        if parser.get_date_data(text_candidate).date_obj == datetime_object:
            return text_candidate


def _joint_parse(text, parser, deep_search=True, accurate_return_text=False, data_carry=None):
    if not text:
        return data_carry or []

    if not len(text) >= 4:
        return data_carry or []

    reduced_text_candidate = None
    returnable_objects = data_carry or []
    joint_based_search_dates = _create_joined_parse(text)
    for date_object_candidate in joint_based_search_dates:
        parsed_date_object = parser.get_date_data(date_object_candidate)
        if parsed_date_object.date_obj:
            if accurate_return_text:
                date_object_candidate = _get_accurate_return_text(
                    date_object_candidate, parser, parsed_date_object.date_obj
                )

            returnable_objects.append(
                (date_object_candidate, parsed_date_object.date_obj)
            )
            start_index = text.find(date_object_candidate)
            end_index = start_index + len(date_object_candidate)
            if start_index < 0:
                break
            reduced_text_candidate = text[:start_index] + text[end_index:]
            break

    if deep_search:
        _joint_parse(reduced_text_candidate, parser, data_carry=returnable_objects)

    return returnable_objects


class DateSearch:
    def __init__(
        self,
        make_joints_parse=True,
        default_language="en",
    ):
        self.make_joints_parse = make_joints_parse
        self.default_language = default_language

        self.search_languages = SearchLanguages()

    @apply_settings
    def search_parse(
        self, text, language_shortname, settings, limit_date_search_results=None, final_clean=True
    ) -> List[tuple]:

        returnable_objects = []
        parser = DateDataParser(languages=[language_shortname], settings=settings)
        _, original = self.search_languages.translate_objects(
            language_shortname, text, settings
        )

        for original_object in original:
            if limit_date_search_results and returnable_objects:
                if len(returnable_objects) == limit_date_search_results:
                    return [returnable_objects]

            if not len(original_object) >= 4:
                continue

            if self.make_joints_parse:
                joint_based_search_dates = _joint_parse(
                    original_object, parser
                )
                if joint_based_search_dates:
                    returnable_objects.extend(joint_based_search_dates)
            else:
                parsed_date_object = parser.get_date_data(original_object)
                if parsed_date_object.date_obj:
                    returnable_objects.append(
                        (original_object, parsed_date_object.date_obj)
                    )

        if final_clean:
            returnable_objects = _final_text_clean(returnable_objects)
            pass

        return returnable_objects

    @apply_settings
    def search_dates(
        self, text, languages=None, limit_date_search_results=None, settings=None
    ) -> Dict:

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
