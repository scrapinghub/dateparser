import fasttext
import os

from dateparser.conf import apply_settings

dir_path = os.path.dirname(os.path.realpath(__file__))

model = "lid.176.ftz"
_model_path = dir_path + '/data/' + model

if os.path.exists(_model_path) == False:
    import urllib.request
    print("Downloading model", model)
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/" + model
    urllib.request.urlretrieve(url, _model_path)

_language_parser = fasttext.load_model(_model_path)

@apply_settings
def detect_languages(text, settings=None):
    language_codes = []
    parser_data = _language_parser.predict(text, k=5)
    for idx, langauge_candidate in enumerate(parser_data[1]):
        if langauge_candidate > settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD:
            _language_code = parser_data[0][idx].replace("__label__", "")
            language_codes.append(_language_code)

    if not language_codes:
        language_codes = settings.DEFAULT_LANGUAGE
        
    return language_codes
