import fasttext
import os
from pathlib import Path

from dateparser_cli.fasttext_manager import fasttext_downloader


_supported_models = ["large.bin", "small.bin"]
_data_dir_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.absolute()) \
    + "/dateparser_data/language_detection_models"
_downloaded_models = os.listdir(_data_dir_path)

_model_path = None

for downloaded_model in _downloaded_models:
    if downloaded_model in _supported_models:
        _model_path = _data_dir_path + "/" + downloaded_model

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
