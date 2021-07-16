import re
from typing import List, Dict

from dateparser.conf import apply_settings
from dateparser.date import DateDataParser
from dateparser.search_dates.languages import DetectLanguage


_detect_languages = DetectLanguage()

_date_separator = re.compile(r"[ ,|\(\)@]")  # never part of the date
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


def _split_objects(text) -> List[str]:
    splited_text = [
        p for p in _date_separator.split(text) if p and p not in _drop_words
    ]
    return splited_text


def _create_joined_parse(text, max_join, reverse_list=True) -> List[str]:
    split_objects = _split_objects(text)
    joint_objects = []

    for i in range(len(split_objects)):
        for j in reversed(range(min(max_join, len(split_objects) - i))):
            x = " ".join(split_objects[i:i + j + 1])
            if _bad_date_re.match(x):
                continue

            joint_objects.append(x)

    joint_objects = sorted(joint_objects, key=len)

    if reverse_list:
        joint_objects.reverse()

    return joint_objects


class DateSearch:
    def __init__(
        self,
        max_join=7,
        make_joints_parse=True,
        minimum_date_str_length=4,
        default_language="en",
    ):
        self.max_join = max_join
        self.make_joints_parse = make_joints_parse
        self.minimum_date_str_length = minimum_date_str_length
        self.default_language = default_language

    @apply_settings
    def search_parse(
        self, text, language_shortname, parse_first_date_only, settings
    ) -> List[tuple]:

        returnable_objects = []

        parser = DateDataParser(languages=[language_shortname], settings=settings)
        original, translated = _detect_languages.translate_objects(
            text, language_shortname, settings
        )

        for index, translated_object in enumerate(translated):
            parsed_date_object = None

            if parse_first_date_only and returnable_objects:
                return [returnable_objects[0]]

            if not len(translated_object) >= self.minimum_date_str_length:
                continue

            if self.make_joints_parse:
                joint_based_search_dates = _create_joined_parse(
                    translated_object, self.max_join
                )

                for date_object_candidate in joint_based_search_dates:
                    parsed_date_object = parser.get_date_data(date_object_candidate)
                    if parsed_date_object.date_obj:
                        break
            else:
                parsed_date_object = parser.get_date_data(translated_object)

            if parsed_date_object.date_obj:
                returnable_objects.append(
                    (original[index], parsed_date_object.date_obj)
                )

        return returnable_objects

    @apply_settings
    def search_dates(
        self, text, languages=None, parse_first_date_only=False, settings=None
    ) -> Dict:

        language_shortname = (
            _detect_languages.detect_language(text=text, languages=languages)
            or self.default_language
        )

        if not language_shortname:
            return {"Language": None, "Dates": None}
        return {
            "Language": language_shortname,
            "Dates": self.search_parse(
                text=text,
                language_shortname=language_shortname,
                parse_first_date_only=parse_first_date_only,
                settings=settings,
            ),
        }
