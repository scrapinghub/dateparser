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
    parser_data = _language_parser.predict(text)
    language_codes = ["en"]
    confidence_score = parser_data[1][0]
    if confidence_score > settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD:
        language_codes = [parser_data[0][0].replace("__label__", "")]

    return language_codes