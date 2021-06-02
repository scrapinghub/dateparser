try:
    import fasttext
except:
    import sys
    import subprocess
    print("Installing fast_text library")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install','fasttext'])
    import fasttext

model = "lid.176.ftz"


def check_model_existence(path):
    from pathlib import Path
    return (Path.cwd() / 'data' / path).exists()

def download_model(path):
    import urllib.request
    print("Downloading model", path)
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/" + path
    print(url)
    urllib.request.urlretrieve(url, 'data/' + path)

    
if check_model_existence(model) == False:
    download_model(model)

_language_parser = fasttext.load_model("data/" + model)
_CONFIDENCE_THRESHOLD = 0.5


def language_parser(text):
    parser_data = _language_parser.predict(text)
    language_codes = ["en"]

    confidence_score = parser_data[1][0]

    if confidence_score > _CONFIDENCE_THRESHOLD:
        language_codes = [parser_data[0][0].replace("__label__", "")]

    return language_codes


text = "2 ਅਗਸਤ 1682 ਸ਼ਨਿੱਚਰ"
print(language_parser(text))