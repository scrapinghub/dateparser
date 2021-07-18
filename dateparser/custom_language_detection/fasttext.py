import fasttext
import os

from dateparser_cli.fasttext_manager import fasttext_downloader
from dateparser_cli.utils import date_parser_model_home


_supported_models = ["large.bin", "small.bin"]
_downloaded_models = os.listdir(date_parser_model_home)

_model_path = None

for downloaded_model in _downloaded_models:
    if downloaded_model in _supported_models:
        _model_path = date_parser_model_home + "/" + downloaded_model

if not _model_path:
    fasttext_downloader()

_language_parser = fasttext.load_model(_model_path)


def detect_languages(text, confidence_threshold=0.5):
    text = text.replace('\n', ' ').replace('\r', '')
    language_codes = []
    parser_data = _language_parser.predict(text, k=5)
    for idx, langauge_candidate in enumerate(parser_data[1]):
        if langauge_candidate > confidence_threshold:
            language_code = parser_data[0][idx].replace("__label__", "")
            language_codes.append(language_code)
    return language_codes
