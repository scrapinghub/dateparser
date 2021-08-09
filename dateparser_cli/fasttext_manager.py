from pathlib import Path
import urllib.request
import os
import logging

from .utils import dateparser_model_home, create_data_model_home
from .exceptions import FastTextModelNotFoundException


def fasttext_downloader(model_name):
    create_data_model_home()
    models = {
        "small": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",
        "large": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    }
    if model_name not in models:
        message = "dateparser-download: Couldn't find a model called \"{}\". Supported models are: {}".format(
            model_name, ", ".join(models.keys())
        )
        raise FastTextModelNotFoundException(message)

    models_directory_path = os.path.join(dateparser_model_home, (model_name + ".bin"))

    if not Path(models_directory_path).is_file():
        model_url = models[model_name]
        logging.info("dateparser-download: Downloading model {}...".format(model_name))
        try:
            urllib.request.urlretrieve(model_url, models_directory_path)
        except urllib.error.HTTPError as e:
            raise Exception("dateparser-download: Fasttext model cannot be downloaded due to HTTP error") from e
    else:
        logging.info("dateparser-download: The model is already downloaded")
