import requests
import re
import json
import os
import shutil
import time
from collections import OrderedDict
import base64

OAuth_Access_Token = 'OAuth_Access_Token'       # Add OAuth_Access_Token here
headers = {'Authorization': 'token %s' % OAuth_Access_Token}
cldr_rbnf_url = "https://api.github.com/repos/unicode-cldr/cldr-rbnf/contents/rbnf/"

DIGIT_PATTERN = re.compile('^\d*$')

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def _get_numeral_data(language):
    cldr_language_rbnf_url = cldr_rbnf_url + language + ".json?ref=master"
    while(True):
        try:
            rbnf_response = requests.get(cldr_language_rbnf_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if rbnf_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(rbnf_response.status_code))

    rbnf_content = base64.b64decode(rbnf_response.json()["content"]).decode("utf-8")
    cldr_rbnf_data = json.loads(rbnf_content)
    spellout_dict = cldr_rbnf_data.get("rbnf").get("rbnf").get("SpelloutRules")
    numeral_dict = OrderedDict()

    if spellout_dict:
        spellout_keys = sorted(spellout_dict.keys())
        for spellout_key in spellout_keys:
            spellout_key_dict = spellout_dict[spellout_key]
            num_keys = sorted([int(key) for key in spellout_key_dict.keys()
                              if DIGIT_PATTERN.match(key)])
            numeral_dict[spellout_key] = OrderedDict()
            for i in range(0, len(num_keys)-1):
                if num_keys[i+1] == num_keys[i] + 1:
                    numeral_dict[spellout_key][str(num_keys[i])] = spellout_key_dict[str(num_keys[i])]
                else:
                    num_range = (num_keys[i], num_keys[i+1]-1)
                    numeral_dict[spellout_key][str(num_range)] = spellout_key_dict[str(num_keys[i])]
            numeral_dict[spellout_key][str((num_keys[len(num_keys)-1], "inf"))] = spellout_key_dict[
                str(num_keys[len(num_keys)-1])]

    return numeral_dict


def _get_rbnf_languages():
    while(True):
        try:
            cldr_rbnf_response = requests.get(cldr_rbnf_url, headers=headers)
        except requests.exceptions.ConnectionError:
            print("Waiting...")
            time.sleep(5)
            continue
        break

    if cldr_rbnf_response.status_code != 200:
        raise RuntimeError("Bad Response " + str(cldr_rbnf_response.status_code))
    cldr_rbnf_content = cldr_rbnf_response.json()
    rbnf_languages = [language['name'][:-5] for language in cldr_rbnf_content]
    return rbnf_languages


rbnf_languages = _get_rbnf_languages()


def main():
    parent_directory = "../data/cldr_language_data"
    directory = "../data/cldr_language_data/numeral_translation_data/"
    if not os.path.isdir(parent_directory):
        os.mkdir(parent_directory)
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)

    for language in rbnf_languages:
        numeral_dict = _get_numeral_data(language)
        if numeral_dict:
            filename = directory + language + ".json"
            print("writing " + filename)
            json_string = json.dumps(numeral_dict, indent=4, separators=(',', ': '),
                                     ensure_ascii=False).encode('utf-8')
            with open(filename, 'wb') as f:
                f.write(json_string)


if __name__ == '__main__':
    main()
