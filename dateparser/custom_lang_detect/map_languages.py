from dateparser_data.language_maps import languages_map


def map_languages(language_codes):
    return_language_codes = []
    for language_code in language_codes:
        if language_code in languages_map:
            return_language_codes += languages_map[language_code]
    return return_language_codes
