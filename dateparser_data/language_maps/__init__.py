import json
import os

_dir_path = os.path.dirname(os.path.realpath(__file__))
_languages_map = json.load(open(_dir_path + '/data/languages_map.json'))

def map_language(language_codes):
    return_language_codes = []
    for language_code in language_codes:
        if language_code in _languages_map:
            return_language_codes += _languages_map[language_code]
    return return_language_codes
