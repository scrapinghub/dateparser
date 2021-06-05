import fasttext
    
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))

model = "lid.176.ftz"
_model_path = dir_path + '/data/' + model


if os.path.exists(_model_path) == False:
    import urllib.request
    print("Downloading model", model)
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/" + model
    urllib.request.urlretrieve(url, _model_path)

_language_parser = fasttext.load_model(_model_path)
_CONFIDENCE_THRESHOLD = 0.5

def detect_languages(text):
    parser_data = _language_parser.predict(text)
    language_codes = ["en"]

    confidence_score = parser_data[1][0]

    if confidence_score > _CONFIDENCE_THRESHOLD:
        language_codes = [parser_data[0][0].replace("__label__", "")]

    return language_codes