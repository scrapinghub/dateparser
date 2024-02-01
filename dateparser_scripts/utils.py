import os
import shutil
from collections import OrderedDict
from pathlib import Path

from git import Repo


CLDR_JSON_DIR = (Path(__file__).parent / "../cldr-json").resolve()


def get_raw_data():
    cldr_version = "44.1.0"
    url = "https://github.com/unicode-org/cldr-json.git"
    if os.path.isdir(CLDR_JSON_DIR):
        shutil.rmtree(CLDR_JSON_DIR)

    print(f'Clonning {url} @ {cldr_version} on {CLDR_JSON_DIR}...')
    Repo.clone_from(url, CLDR_JSON_DIR, branch=cldr_version, depth=1)


def get_dict_difference(parent_dict, child_dict):
    difference_dict = OrderedDict()
    for key, child_value in child_dict.items():
        parent_value = parent_dict.get(key)
        child_specific_value = None
        if not parent_value:
            child_specific_value = child_value
        elif isinstance(child_value, list):
            child_specific_value = sorted(set(child_value) - set(parent_value))
        elif isinstance(child_value, dict):
            child_specific_value = get_dict_difference(parent_value, child_value)
        elif child_value != parent_value:
            child_specific_value = child_value
        if child_specific_value:
            difference_dict[key] = child_specific_value
    return difference_dict


def combine_dicts(primary_dict, supplementary_dict):
    combined_dict = OrderedDict()
    for key, value in primary_dict.items():
        if key in supplementary_dict:
            if isinstance(value, list):
                combined_dict[key] = value + supplementary_dict[key]
            elif isinstance(value, dict):
                combined_dict[key] = combine_dicts(value, supplementary_dict[key])
            else:
                combined_dict[key] = supplementary_dict[key]
        else:
            combined_dict[key] = primary_dict[key]
    remaining_keys = [
        key for key in supplementary_dict.keys() if key not in primary_dict.keys()
    ]
    for key in remaining_keys:
        combined_dict[key] = supplementary_dict[key]
    return combined_dict
