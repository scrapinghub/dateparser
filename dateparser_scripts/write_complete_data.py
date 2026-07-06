import json
import os
import shutil
from pathlib import Path

import regex as re
from ruamel.yaml import YAML

from dateparser_scripts.order_languages import avoid_languages
from dateparser_scripts.utils import combine_dicts

root = Path(__file__).parent.parent

cldr_date_directory = root / "dateparser_data/cldr_language_data/date_translation_data"
supplementary_directory = root / "dateparser_data/supplementary_language_data"
supplementary_date_directory = (
    root / "dateparser_data/supplementary_language_data/date_translation_data"
)
translation_data_directory = root / "dateparser/data"
date_translation_directory = root / "dateparser/data/date_translation_data"

cldr_languages = list(
    set(map(lambda x: x[:-5], os.listdir(cldr_date_directory))) - avoid_languages
)
supplementary_languages = [x[:-5] for x in os.listdir(supplementary_date_directory)]
all_languages = set(cldr_languages).union(set(supplementary_languages))

RELATIVE_PATTERN = re.compile(r"\{0\}")
POSSESSIVE_DIGIT_PATTERN = re.compile(r"\\d\+\[\.,\]\?\\d\*")


def _make_possessive(s):
    return POSSESSIVE_DIGIT_PATTERN.sub(r"\\d++[.,]?\\d*+", s)


def _to_plain_types(obj):
    """Recursively convert ruamel.yaml CommentedMap/CommentedSeq to plain
    dict/list so that json.dumps produces stable output across all
    Python versions.

    Python 3.14 changed the json C encoder to bypass the Python-level
    ``__iter__``/``items()`` of dict subclasses and access the underlying C
    dict directly.  ruamel.yaml's CommentedMap relies on its Python-level
    iteration for correct key ordering, so the C shortcut produces a
    different (non-deterministic) key order on 3.14.  Converting to plain
    types before serialisation avoids the issue entirely.
    """
    if isinstance(obj, dict):
        return {k: _to_plain_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_plain_types(v) for v in obj]
    return obj


def _modify_relative_data(relative_data):
    modified_relative_data = {}
    for key, value in relative_data.items():
        for i, string in enumerate(value):
            string = RELATIVE_PATTERN.sub(r"(\\d++[.,]?\\d*+)", string)
            string = _make_possessive(string)
            value[i] = string
        modified_relative_data[key] = value
    return modified_relative_data


def _modify_simplifications(simplifications):
    for simplification in simplifications:
        for pattern in list(simplification.keys()):
            new_pattern = _make_possessive(pattern)
            if new_pattern != pattern:
                simplification[new_pattern] = simplification.pop(pattern)


def _modify_data(language_data):
    relative_data = language_data.get("relative-type-regex", {})
    relative_data = _modify_relative_data(relative_data)
    simplifications = language_data.get("simplifications", [])
    _modify_simplifications(simplifications)
    locale_specific_data = language_data.get("locale_specific", {})
    for _, info in locale_specific_data.items():
        locale_relative_data = info.get("relative-type-regex", {})
        locale_relative_data = _modify_relative_data(locale_relative_data)


def _get_complete_date_translation_data(language):
    cldr_data = {}
    supplementary_data = {}
    if language in cldr_languages:
        with open(cldr_date_directory / f"{language}.json") as f:
            cldr_data = json.load(f)
    if language in supplementary_languages:
        with open(supplementary_date_directory / f"{language}.yaml") as g:
            yaml = YAML()
            supplementary_data = dict(yaml.load(g))
    complete_data = combine_dicts(cldr_data, supplementary_data)
    if "name" not in complete_data:
        complete_data["name"] = language
    return complete_data


def _write_file(filename, text, mode, in_memory, in_memory_result):
    if in_memory:
        in_memory_result[filename] = text
    else:
        with open(filename, mode) as out:
            out.write(text)


def write_complete_data(in_memory=False):
    """
    This function is responsible of generating the needed py files from the
    CLDR files (JSON format) and supplementary language data (YAML format).

    Use it with in_memory=True to avoid writing real files and getting a
    dictionary containing the file names and their content (used when testing).
    """
    in_memory_result = {}

    if not in_memory:
        if not os.path.isdir(translation_data_directory):
            os.mkdir(translation_data_directory)
        if os.path.isdir(date_translation_directory):
            shutil.rmtree(date_translation_directory)
        os.mkdir(date_translation_directory)

    with open(supplementary_directory / "base_data.yaml") as f:
        yaml = YAML()
        base_data = yaml.load(f)

    for language in all_languages:
        date_translation_data = _get_complete_date_translation_data(language)
        date_translation_data = combine_dicts(date_translation_data, base_data)
        date_translation_data = _to_plain_types(date_translation_data)
        _modify_data(date_translation_data)
        translation_data = json.dumps(
            date_translation_data, indent=4, separators=(",", ": "), ensure_ascii=False
        )
        out_text = ("info = " + translation_data + "\n").encode("utf-8")
        _write_file(
            date_translation_directory / f"{language}.py",
            out_text,
            "wb",
            in_memory,
            in_memory_result,
        )

    init_text = (
        "from dateparser.data import date_translation_data\n"
        "\n"
        "from .languages_info import language_locale_dict, language_order\n"
    )

    _write_file(
        translation_data_directory / "__init__.py",
        init_text,
        "w",
        False,
        in_memory_result,
    )
    _write_file(
        date_translation_directory / "__init__.py", "", "w", False, in_memory_result
    )

    return in_memory_result


if __name__ == "__main__":
    write_complete_data()
