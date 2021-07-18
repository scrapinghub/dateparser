from dateparser.data.languages_info import language_map


def map_languages(language_codes):
    return_language_codes = []
    for language_code in language_codes:
        if language_code in language_map:
            return_language_codes += language_map[language_code]
    return return_language_codes
