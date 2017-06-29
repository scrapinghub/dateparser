import json
from ruamel.yaml import SafeLoader
import os
import shutil
from collections import OrderedDict

from utils import combine_dicts

cldr_date_directory = '../data/cldr_language_data/date_translation_data/'
cldr_numeral_directory = '../data/cldr_language_data/numeral_translation_data/'
supplementary_directory = '../data/supplementary_language_data/'
supplementary_date_directory = '../data/supplementary_language_data/date_translation_data/'
translation_data_directory = '../data/translation_data/'
date_translation_directory = '../data/translation_data/date_translation_data/'
numeral_translation_directory = '../data/translation_data/numeral_translation_data/'

os.chdir(os.path.dirname(__file__))
cldr_languages = map(lambda x: x[:-5], os.listdir(cldr_date_directory))
supplementary_languages = map(lambda x: x[:-5], os.listdir(supplementary_date_directory))
all_languages = set(cldr_languages).union(set(supplementary_languages))
cldr_numeral_languages = map(lambda x: x[:-5], os.listdir(cldr_numeral_directory))


def _get_complete_data(language):
    cldr_data = {}
    supplementary_data = {}
    if language in cldr_languages:
        with open(cldr_date_directory + language + '.json') as f:
            cldr_data = json.load(f, object_pairs_hook=OrderedDict)
    if language in supplementary_languages:
        with open(supplementary_date_directory + language + '.yaml') as g:
            supplementary_data = SafeLoader(g).get_data()
    complete_data = combine_dicts(cldr_data, supplementary_data)
    return complete_data


def main():
    if not os.path.isdir(translation_data_directory):
        os.mkdir(translation_data_directory)
    if os.path.isdir(date_translation_directory):
        shutil.rmtree(date_translation_directory)
    os.mkdir(date_translation_directory)
    for language in all_languages:
        date_translation_data = _get_complete_data(language)
        translation_data = json.dumps(
            date_translation_data, indent=4, ensure_ascii=False).encode('utf-8')
        with open(date_translation_directory + language + '.py', 'w') as out:
            out.write(language + ' = ' + translation_data)

    if os.path.isdir(numeral_translation_directory):
        shutil.rmtree(numeral_translation_directory)
    os.mkdir(numeral_translation_directory)
    for language in cldr_numeral_languages:
        with open(cldr_numeral_directory + language + '.json') as f:
            numeral_translation_data = json.load(f, object_pairs_hook=OrderedDict)
        numeral_data = json.dumps(
            numeral_translation_data, indent=4, ensure_ascii=False).encode('utf-8')
        with open(numeral_translation_directory + language + '.py', 'w') as out:
            out.write(language + ' = ' + numeral_data)

    with open(supplementary_directory + 'base_data.yaml') as f:
        base_data = SafeLoader(f).get_data()
        base_data = json.dumps(base_data, indent=4, ensure_ascii=False).encode('utf-8')
    with open(translation_data_directory + 'base_data.py', 'w') as out:
        out.write(base_data)


if __name__ == '__main__':
    main()
