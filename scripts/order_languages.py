import requests
import re
import json
import os
import time
import base64

OAuth_Access_Token = 'OAuth_Access_Token'       # Add OAuth_Access_Token here
headers = {'Authorization': 'token %s' % OAuth_Access_Token}
cldr_dates_full_url = "https://api.github.com/repos/unicode-cldr/cldr-dates-full/contents/main/"
territory_info_url = "https://api.github.com/repos/unicode-cldr/cldr-core/contents/supplemental/territoryInfo.json?ref=master"

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _get_language_locale_dict():
    while(True):
        try:
            dates_full_response = requests.get(cldr_dates_full_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if dates_full_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(dates_full_response.status_code))
    dates_content = dates_full_response.json()

    available_locale_names = [locale['name'] for locale in dates_content]
    available_language_names = [locale_name for locale_name in available_locale_names
                                if not re.search(r'-[A-Z0-9]+$', locale_name)]
    available_language_names.remove('root')
    language_locale_dict = {}
    for language_name in available_language_names:
        language_locale_dict[language_name] = []
        for locale_name in available_locale_names:
            if re.match(language_name + '-[A-Z0-9]+$', locale_name):
                language_locale_dict[language_name].append(locale_name)
    return language_locale_dict


language_locale_dict = _get_language_locale_dict()


def _get_language_order():
    while(True):
        try:
            territory_response = requests.get(territory_info_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if territory_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(territory_response.status_code))

    territory_data = territory_response.json()
    territory_content = json.loads(base64.b64decode(territory_data["content"]).decode('utf-8'))
    territory_info_data = territory_content["supplemental"]["territoryInfo"]
    language_population_dict = {}
    for territory in territory_info_data:
        population = int(territory_info_data[territory]["_population"])
        try:
            lang_dict = territory_info_data[territory]["languagePopulation"]
            for language in lang_dict:
                language_population = float(lang_dict[language]["_populationPercent"]) * population
                if language in language_population_dict:
                    language_population_dict[language] += language_population
                else:
                    language_population_dict[language] = language_population
        except:
            pass

    language_order = sorted(language_population_dict.keys(),
                            key=lambda x: (language_population_dict[x], x), reverse=True)
    for index in range(0, len(language_order)):
        language_order[index] = re.sub(r'_', r'-', language_order[index])

    cldr_languages = language_locale_dict.keys()
    supplementary_date_directory = "../data/supplementary_language_data/date_translation_data"
    supplementary_languages = list(map(lambda x: x[:-5], os.listdir(supplementary_date_directory)))
    available_languages = set(cldr_languages).union(set(supplementary_languages))
    language_order = [shortname for shortname in language_order if shortname in available_languages]
    absent_languages = set(available_languages) - set(language_order)
    remaining_languages = []
    for language in absent_languages:
        parent_language = re.sub(r'-\w+', '', language)
        if parent_language in language_order:
            language_order.insert(language_order.index(parent_language) + 1, language)
        else:
            remaining_languages.append(language)
    language_order = language_order + sorted(remaining_languages)
    language_order = list(map(str, language_order))
    return language_order


language_order = _get_language_order()


def main():
    parent_directory = "../data/translation_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    language_order_string = 'language_order = ' + json.dumps(
            language_order, separators=(',', ': '), indent=4)
    filename = parent_directory + 'language_order.py'
    with open(filename, 'w') as f:
        f.write(language_order_string)


if __name__ == '__main__':
    main()
