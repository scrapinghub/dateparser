import fasttext
import os

from dateparser.conf import apply_settings

dir_path = os.path.dirname(os.path.realpath(__file__))

_model = "lid.176.ftz"
_model_path = dir_path + '/' + _model

if not os.path.exists(_model_path):
    import urllib.request
    print("Downloading model", _model)
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/" + _model
    try:
        urllib.request.urlretrieve(url, _model_path)
    except urllib.error.HTTPError:
        print("Fasttext model", _model, "cannot be downloaded due to HTTP error")
        raise urllib.error.HTTPError

_language_parser = fasttext.load_model(_model_path)


@apply_settings
def detect_languages(text, settings=None):
    text = text.replace('\n', ' ').replace('\r', '')
    language_codes = []
    parser_data = _language_parser.predict(text, k=5)
    for idx, langauge_candidate in enumerate(parser_data[1]):
        if langauge_candidate > settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD:
            _language_code = parser_data[0][idx].replace("__label__", "")
            language_codes.append(_language_code)
    return language_codes
