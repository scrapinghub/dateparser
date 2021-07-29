import os

import fasttext

from dateparser_cli.fasttext_manager import fasttext_downloader
from dateparser_cli.utils import date_parser_model_home, check_data_model_home_existance


_supported_models = ["large.bin", "small.bin"]
_DEFAULT_MODEL = "small.bin"


class FastTextCache:
    model = None


def _load_fasttext_model():

    if FastTextCache.model:
        return FastTextCache.model

    check_data_model_home_existance()
    model_path = None
    downloaded_models = os.listdir(date_parser_model_home)

    for downloaded_model in downloaded_models:
        if downloaded_model in _supported_models:
            model_path = os.path.join(date_parser_model_home, downloaded_model)

    if not model_path:
        fasttext_downloader("small")
        _load_fasttext_model()

    FastTextCache.model = fasttext.load_model(model_path)
    return FastTextCache.model


def detect_languages(text, confidence_threshold):
    _language_parser = _load_fasttext_model()
    text = text.replace('\n', ' ').replace('\r', '')
    language_codes = []
    parser_data = _language_parser.predict(text)
    for idx, langauge_candidate in enumerate(parser_data[1]):
        if langauge_candidate > confidence_threshold:
            language_code = parser_data[0][idx].replace("__label__", "")
            language_codes.append(language_code)
    return language_codes
