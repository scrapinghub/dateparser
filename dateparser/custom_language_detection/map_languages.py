from dateparser.data.languages_info import language_map


def map_languages(language_codes):
    """Returnes language supported candidates.

    :param languages:
        A list of language codes, e.g. ['en', 'es'] in ISO 639 Standard
    :type languages: list

    :return: Returns list[str] representing supported languages, else returns None
    :rtype: list[str]
    """
    return_language_codes = []
    for language_code in language_codes:
        if language_code in language_map:
            return_language_codes.extend(language_map[language_code])
    return return_language_codes
