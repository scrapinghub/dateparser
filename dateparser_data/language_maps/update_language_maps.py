
def main():
    data = {}

    while all_language_code:
        micro_data = []
        for obj in all_language_code:
            if not micro_data:
                micro_data.append(obj)
            else:
                if obj.startswith(micro_data[0] + '-'):
                    micro_data.append(obj)
        for x in micro_data:
            all_language_code.remove(x)
        data[micro_data[0]] = micro_data
    with open(dateparser_data_dir + '/language_maps/data/languages_map.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
