from dateparser.data.languages_info import language_map


def map_languages(language_codes):
    """
    Returns the candidates from the supported languages codes.
    :param languages:
        A list of language codes, e.g. ['en', 'es'] in ISO 639 Standard.
    :type languages: list
    :return: Returns list[str] representing supported languages
    :rtype: list[str]
    """
    return [
        language_code
        for language_code_key in language_codes
        if language_code_key in language_map
        for language_code in language_map[language_code_key]
    ]
