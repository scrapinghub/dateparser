import json
import os
import shutil

import regex as re

from dateparser_scripts.order_languages import _get_language_locale_dict
from dateparser_scripts.utils import get_dict_difference, get_raw_data, CLDR_JSON_DIR

APOSTROPHE_LOOK_ALIKE_CHARS = [
    "\N{RIGHT SINGLE QUOTATION MARK}",  # '\u2019'
    "\N{MODIFIER LETTER APOSTROPHE}",  # '\u02bc'
    "\N{MODIFIER LETTER TURNED COMMA}",  # '\u02bb'
    "\N{ARMENIAN APOSTROPHE}",  # '\u055a'
    "\N{LATIN SMALL LETTER SALTILLO}",  # '\ua78c'
    "\N{PRIME}",  # '\u2032'
    "\N{REVERSED PRIME}",  # '\u2035'
    "\N{MODIFIER LETTER PRIME}",  # '\u02b9'
    "\N{FULLWIDTH APOSTROPHE}",  # '\uff07'
]

DATE_ORDER_PATTERN = re.compile(
    "([DMY])+\u200f*[-/. \t]*([DMY])+\u200f*[-/. \t]*([DMY])+"
)
RELATIVE_PATTERN = re.compile(r"(?<![\+\-]\s*)\{0\}")
DEFAULT_MONTH_PATTERN = re.compile(r"^M?\d+$", re.U)
RE_SANITIZE_APOSTROPHE = re.compile("|".join(APOSTROPHE_LOOK_ALIKE_CHARS))
AM_PATTERN = re.compile(r"^\s*[Aa]\s*\.?\s*[Mm]\s*\.?\s*$")
PM_PATTERN = re.compile(r"^\s*[Pp]\s*\.?\s*[Mm]\s*\.?\s*$")
PARENTHESIS_PATTERN = re.compile(r"[\(\)]")


def _filter_relative_string(relative_string):
    return (
        isinstance(relative_string, str)
        and RELATIVE_PATTERN.search(relative_string)
        and not PARENTHESIS_PATTERN.search(relative_string)
    )


def _filter_month_name(month_name):
    return not DEFAULT_MONTH_PATTERN.match(month_name)


def _retrieve_locale_data(locale):
    def load(scope, file_id):
        file_path = (
            CLDR_JSON_DIR
            / "cldr-json"
            / f"cldr-{scope}-full"
            / "main"
            / locale
            / f"{file_id}.json"
        )
        with file_path.open() as f:
            return json.load(f)

    cldr_gregorian_data = load("dates", "ca-gregorian")
    cldr_datefields_data = load("dates", "dateFields")
    _units = load("units", "units")

    gregorian_dict = cldr_gregorian_data["main"][locale]["dates"]["calendars"][
        "gregorian"
    ]
    date_fields_dict = cldr_datefields_data["main"][locale]["dates"]["fields"]
    units = _units["main"][locale]["units"]["long"]

    json_dict = {}

    field_keys_1 = ["stand-alone", "format"]
    field_keys_2 = [
        "wide",
        "abbreviated",
    ]  # neglecting "narrow" to avoid problems in translation
    year_keys = ["year", "year-short", "year-narrow"]
    month_keys = ["month", "month-short", "month-narrow"]
    week_keys = ["week", "week-short", "week-narrow"]
    day_keys = ["day", "day-short", "day-narrow"]
    hour_keys = ["hour", "hour-short", "hour-narrow"]
    minute_keys = ["minute", "minute-short", "minute-narrow"]
    second_keys = ["second", "second-short", "second-narrow"]
    relative_keys = ["relativeTimePattern-count-one", "relativeTimePattern-count-other"]
    # Per-weekday CLDR fields (mon, mon-short, mon-narrow, ...) carry
    # relative-type--1/0/1 phrases ("last Monday" / "this Monday" / "next
    # Monday"). We map each locale's phrases to a canonical English target so
    # the parser can resolve them uniformly across languages (#573).
    weekday_keys = {
        "monday": ["mon", "mon-short", "mon-narrow"],
        "tuesday": ["tue", "tue-short", "tue-narrow"],
        "wednesday": ["wed", "wed-short", "wed-narrow"],
        "thursday": ["thu", "thu-short", "thu-narrow"],
        "friday": ["fri", "fri-short", "fri-narrow"],
        "saturday": ["sat", "sat-short", "sat-narrow"],
        "sunday": ["sun", "sun-short", "sun-narrow"],
    }
    # CLDR relative-type key -> canonical modifier word. Only "last" (-1) and
    # "next" (+1) are imported: the "this" (0) phrase is, in many locales,
    # identical to the bare weekday name (e.g. nb "torsdag", sr "u nedelju"),
    # so importing it would shadow the plain weekday translation. "this
    # <weekday>" is left to supplementary data where it is genuinely distinct.
    weekday_relative_types = {
        "relative-type--1": "last",
        "relative-type-1": "next",
    }

    json_dict["name"] = locale

    try:
        date_format_string = gregorian_dict["dateFormats"]["short"].upper()
    except AttributeError:
        date_format_string = gregorian_dict["dateFormats"]["short"]["_value"].upper()

    json_dict["date_order"] = DATE_ORDER_PATTERN.sub(
        r"\1\2\3", DATE_ORDER_PATTERN.search(date_format_string).group()
    )

    json_dict["january"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["1"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["february"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["2"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["march"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["3"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["april"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["4"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["may"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["5"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["june"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["6"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["july"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["7"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["august"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["8"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["september"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["9"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["october"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["10"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["november"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["11"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["december"] = list(
        filter(
            _filter_month_name,
            [
                gregorian_dict["months"][key1][key2]["12"]
                for key1 in field_keys_1
                for key2 in field_keys_2
            ],
        )
    )

    json_dict["monday"] = [
        gregorian_dict["days"][key1][key2]["mon"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["tuesday"] = [
        gregorian_dict["days"][key1][key2]["tue"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["wednesday"] = [
        gregorian_dict["days"][key1][key2]["wed"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["thursday"] = [
        gregorian_dict["days"][key1][key2]["thu"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["friday"] = [
        gregorian_dict["days"][key1][key2]["fri"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["saturday"] = [
        gregorian_dict["days"][key1][key2]["sat"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["sunday"] = [
        gregorian_dict["days"][key1][key2]["sun"]
        for key1 in field_keys_1
        for key2 in field_keys_2
    ]

    json_dict["am"] = [
        AM_PATTERN.sub("am", x)
        for x in [
            gregorian_dict["dayPeriods"][key1][key2]["am"]
            for key1 in field_keys_1
            for key2 in field_keys_2
        ]
    ]

    json_dict["pm"] = [
        PM_PATTERN.sub("pm", x)
        for x in [
            gregorian_dict["dayPeriods"][key1][key2]["pm"]
            for key1 in field_keys_1
            for key2 in field_keys_2
        ]
    ]

    json_dict["year"] = [date_fields_dict[key]["displayName"] for key in year_keys]

    json_dict["month"] = [date_fields_dict[key]["displayName"] for key in month_keys]

    json_dict["week"] = [date_fields_dict[key]["displayName"] for key in week_keys]

    json_dict["day"] = [date_fields_dict[key]["displayName"] for key in day_keys]

    json_dict["hour"] = [date_fields_dict[key]["displayName"] for key in hour_keys]
    hour_unit = units["duration-hour"]["displayName"]
    if hour_unit not in json_dict["hour"]:
        json_dict["hour"].append(hour_unit)

    json_dict["minute"] = [date_fields_dict[key]["displayName"] for key in minute_keys]

    json_dict["second"] = [date_fields_dict[key]["displayName"] for key in second_keys]

    json_dict["relative-type"] = {}

    json_dict["relative-type"]["1 year ago"] = [
        date_fields_dict[key]["relative-type--1"] for key in year_keys
    ]

    json_dict["relative-type"]["0 year ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in year_keys
    ]

    json_dict["relative-type"]["in 1 year"] = [
        date_fields_dict[key]["relative-type-1"] for key in year_keys
    ]

    json_dict["relative-type"]["1 month ago"] = [
        date_fields_dict[key]["relative-type--1"] for key in month_keys
    ]

    json_dict["relative-type"]["0 month ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in month_keys
    ]

    json_dict["relative-type"]["in 1 month"] = [
        date_fields_dict[key]["relative-type-1"] for key in month_keys
    ]

    json_dict["relative-type"]["1 week ago"] = [
        date_fields_dict[key]["relative-type--1"] for key in week_keys
    ]

    json_dict["relative-type"]["0 week ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in week_keys
    ]

    json_dict["relative-type"]["in 1 week"] = [
        date_fields_dict[key]["relative-type-1"] for key in week_keys
    ]

    json_dict["relative-type"]["1 day ago"] = [
        date_fields_dict[key]["relative-type--1"] for key in day_keys
    ]

    json_dict["relative-type"]["0 day ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in day_keys
    ]

    json_dict["relative-type"]["in 1 day"] = [
        date_fields_dict[key]["relative-type-1"] for key in day_keys
    ]

    json_dict["relative-type"]["0 hour ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in hour_keys
    ]

    json_dict["relative-type"]["0 minute ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in minute_keys
    ]

    json_dict["relative-type"]["0 second ago"] = [
        date_fields_dict[key]["relative-type-0"] for key in second_keys
    ]

    # Weekday relative phrases -> canonical "<modifier> <weekday>" targets.
    # e.g. es "el próximo martes" -> "next tuesday". The canonical English
    # phrase is then translated and resolved by the parser like any weekday.
    #
    # In some locales a relative phrase is identical to the bare weekday name
    # (e.g. nb "torsdag" is both "Thursday" and "this Thursday"). Mapping such a
    # phrase would break the plain weekday translation, so those collisions are
    # skipped: the bare-weekday handling already covers them.
    bare_weekday_names = {
        name.lower()
        for names in (json_dict[weekday] for weekday in weekday_keys)
        for name in names
    }
    # Phrases already claimed by another relative-type entry (e.g. sr "prošle
    # nedelje" is both "last week" and "last Sunday"; "week" wins as it is
    # established behavior). Weekday phrases must not clobber these.
    claimed_phrases = {
        phrase.lower()
        for phrases in json_dict["relative-type"].values()
        for phrase in phrases
    }
    for weekday, keys in weekday_keys.items():
        for rel_key, modifier in weekday_relative_types.items():
            target = "{} {}".format(modifier, weekday)
            phrases = []
            for key in keys:
                field = date_fields_dict.get(key)
                if not field:
                    continue
                phrase = field.get(rel_key)
                # Skip missing entries, CLDR "no value" markers, phrases that
                # collide with a bare weekday name, and phrases already used by
                # another relative-type entry.
                if (
                    phrase
                    and phrase != "∅∅∅"
                    and phrase.lower() not in bare_weekday_names
                    and phrase.lower() not in claimed_phrases
                ):
                    phrases.append(phrase)
            if phrases:
                json_dict["relative-type"][target] = phrases

    json_dict["relative-type-regex"] = {}

    json_dict["relative-type-regex"]["in \\1 year"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in year_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 year ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in year_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 month"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in month_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 month ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in month_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 week"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in week_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 week ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in week_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 day"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in day_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 day ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in day_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 hour"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in hour_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 hour ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in hour_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 minute"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in minute_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 minute ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in minute_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["in \\1 second"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-future"].get(key2)
                for key1 in second_keys
                for key2 in relative_keys
            ],
        )
    )

    json_dict["relative-type-regex"]["\\1 second ago"] = list(
        filter(
            _filter_relative_string,
            [
                date_fields_dict[key1]["relativeTime-type-past"].get(key2)
                for key1 in second_keys
                for key2 in relative_keys
            ],
        )
    )

    return json_dict


def _clean_string(given_string):
    given_string = RE_SANITIZE_APOSTROPHE.sub("'", given_string)
    given_string = given_string.replace(".", "")
    given_string = given_string.lower()
    return " ".join(given_string.split())


def _clean_dict(json_dict):
    """Remove duplicates and sort"""
    for key, value in json_dict.items():
        if isinstance(value, list):
            json_dict[key] = sorted(dict.fromkeys(map(_clean_string, value)))
        elif isinstance(value, dict):
            json_dict[key] = dict(sorted(value.items()))
            json_dict[key] = _clean_dict(json_dict[key])
    return dict(filter(lambda x: x[1], json_dict.items()))


def main():
    get_raw_data()
    language_locale_dict = _get_language_locale_dict()
    parent_directory = "../dateparser_data/cldr_language_data"
    directory = "../dateparser_data/cldr_language_data/date_translation_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for language in language_locale_dict:
        json_language_dict = _clean_dict(_retrieve_locale_data(language))
        locale_specific_dict = {}
        locales_list = language_locale_dict[language]
        for locale in locales_list:
            json_locale_dict = _clean_dict(_retrieve_locale_data(locale))
            locale_specific_dict[locale] = _clean_dict(
                get_dict_difference(json_language_dict, json_locale_dict)
            )
        json_language_dict["locale_specific"] = dict(
            sorted(locale_specific_dict.items())
        )
        filename = directory + language + ".json"
        print("writing " + filename)
        json_string = json.dumps(
            json_language_dict, indent=4, separators=(",", ": "), ensure_ascii=False
        ).encode("utf-8")
        with open(filename, "wb") as f:
            f.write(json_string)


if __name__ == "__main__":
    main()
