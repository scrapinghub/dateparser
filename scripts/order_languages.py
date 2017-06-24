import requests
import re
import json
import os

from get_cldr_data import language_locale_dict

territory_info_url = "https://api.github.com/repos/unicode-cldr/cldr-core/contents/supplemental/territoryInfo.json?ref=master"


def get_language_order():
    territory_response = requests.get(territory_info_url)
    territory_data = territory_response.json()
    territory_content = json.loads(territory_data["content"].decode('base64'))
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
                            key=lambda x: language_population_dict[x], reverse=True)
    for index in range(0, len(language_order)):
        language_order[index] = re.sub(r'_', r'-', language_order[index])

    available_languages = language_locale_dict.keys()
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
    return language_order


def main():
    os.chdir(os.path.dirname(__file__))
    parent_directory = "../data/cldr_language_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    language_order = get_language_order()
    language_order_dict = {'language_order': language_order}
    json_string = json.dumps(language_order_dict, indent=4)
    filename = parent_directory + 'language_order.json'
    with open(filename, 'w') as f:
        f.write(json_string)

if __name__ == '__main__':
    main()
