import os
from pathlib import Path
import urllib.request


_data_dir_path = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()) + "/dateparser_data"


def fasttext_downloader(model=[]):
    model_url = {
        "small": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",
        "large": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    }

    model_name = "small"
    if model:
        if model[0] == "large":
            model_name = "large"

    models_directory_path = _data_dir_path + "/language_detection_models/" + model_name + ".bin"

    if not Path(models_directory_path).is_file():
        model_url = model_url[model_name]
        print("Downloading model", model_name)
        try:
            urllib.request.urlretrieve(model_url, models_directory_path)
        except urllib.error.HTTPError:
            print("Fasttext model cannot be downloaded due to HTTP error")
            raise urllib.error.HTTPError
    else:
        print("The model is already downloaded")
