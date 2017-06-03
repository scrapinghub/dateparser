import requests
import re
import json

territory_info_url = "https://api.github.com/repos/unicode-cldr/cldr-core/contents/supplemental/territoryInfo.json?ref=master"

territory_response = requests.get(territory_info_url)
territory_data = territory_response.json()
territory_content = json.loads(territory_data["content"].decode('base64'))
territory_info_data = territory_content["supplemental"]["territoryInfo"]
language_population_dict = {}
count = 0
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

language_order = sorted(language_population_dict.keys(),key=lambda x:language_population_dict[x],reverse = True)
for index in range(0,len(language_order)):
    language_order[index] = re.sub(r'_',r'-',language_order[index])
