import re
from time import sleep
from types import new_class
from typing import List, Dict

from dateparser.conf import apply_settings
from dateparser.date import DateDataParser
from dateparser.search_dates.languages import SearchLanguages



_date_separator = re.compile(r"[ |\(\)@]")  # never part of the date
_drop_words = {"on", "at", "of", "a"}  # cause annoying false positives
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

# BELOW ARE TEMPORARY FIX

def _final_text_clean(text):
    if "." == text[-1]:
        text = text[:-1] 
    return text
        

        


def _split_objects(text) -> List[str]:
    splited_text = [
        p for p in _date_separator.split(text) if p and p not in _drop_words
    ]
    return splited_text


def _create_joined_parse(text, max_join, reverse_list=True):
    split_objects = _split_objects(text)
    joint_objects = []
    for i in range(len(split_objects)):
        for j in reversed(range(min(max_join, len(split_objects) - i))):
            x = " ".join(split_objects[i:i + j + 1])
            if _bad_date_re.match(x):
                continue
            if not len(x) >= 4:
                continue
            joint_objects.append(x)

    joint_objects = sorted(joint_objects, key=len)
    if reverse_list:
        joint_objects.reverse()

    return joint_objects


def _joint_parse(text, max_join, parser, reverse_list=True, deep_search=True, data_carry=None):

    if not len(text) >= 4:
        return data_carry or []

    reduced_text_candidate = None
    returnable_objects = data_carry or []
    joint_based_search_dates = _create_joined_parse(text, max_join, reverse_list)
    for date_object_candidate in joint_based_search_dates:
        parsed_date_object = parser.get_date_data(date_object_candidate)
        if parsed_date_object.date_obj:
            date_text= _final_text_clean(date_object_candidate)
            returnable_objects.append(
                (date_text, parsed_date_object.date_obj)
            )
            start_index = text.find(date_object_candidate)
            end_index = start_index + len(date_object_candidate)
            if not start_index > 0:
                break
            reduced_text_candidate = text[:start_index-1] + text[end_index:]
            break

    if deep_search and reduced_text_candidate:
        _joint_parse(reduced_text_candidate, max_join, parser, reverse_list=True, data_carry=returnable_objects)

    return returnable_objects


class DateSearch:
    def __init__(
        self,
        max_join=7,
        make_joints_parse=True,
        default_language="en",
    ):
        self.max_join = max_join
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

        for index, translated_object in enumerate(original):
            parsed_date_object = None
            if limit_date_search_results and returnable_objects:
                if len(returnable_objects) == limit_date_search_results:
                    return [returnable_objects]

            if not len(translated_object) >= 4:
                continue

            if self.make_joints_parse:
                joint_based_search_dates = _joint_parse(
                    translated_object, self.max_join, parser
                )
                if joint_based_search_dates:
                    returnable_objects.extend(joint_based_search_dates)
            else:
                parsed_date_object = parser.get_date_data(translated_object)
                if parsed_date_object.date_obj:
                    date_text= _final_text_clean(original[index])
                    returnable_objects.append(
                        (date_text, parsed_date_object.date_obj)
                    )
        
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
