import os
import glob
from pathlib import Path
import json


def main():
    dateparser_data_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    all_files_name = glob.glob(dateparser_data_dir + "/cldr_language_data/date_translation_data/*.json")

    all_language_code = [Path(file_name).stem for file_name in all_files_name]
    all_language_code.sort()

    data = {}

    while all_language_code:
        micro_data = []
        for obj in all_language_code:
            if not micro_data:
                micro_data.append(obj)
            else:
                if micro_data[0] == obj[:len(micro_data[0])] and "-" in obj:
                    micro_data.append(obj)
        for x in micro_data:
            all_language_code.remove(x)
        data[micro_data[0]] = micro_data
    with open(dateparser_data_dir + '/language_maps/data/languages_map.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
