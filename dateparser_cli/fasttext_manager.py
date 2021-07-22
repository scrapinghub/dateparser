from pathlib import Path
import urllib.request
import os
import logging

from .utils import date_parser_model_home, check_data_model_home_existance
from .exceptions import FastTextModelNotFoundException


def fasttext_downloader(model=None):
    check_data_model_home_existance()

    model_url = {
        "small": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",
        "large": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    }

    if not model:
        message = "No model name passed Supported models are: {}".join(model_url.keys())
        raise FastTextModelNotFoundException(message)
    elif model[0] in model_url:
        model_name = model[0]
    else:
        message = "Couldn't find a model called \"{}\". Supported models are: {}".format(
            model, "in ".join(model[0], model_url.keys())
        )
        raise FastTextModelNotFoundException(message)

    models_directory_path = os.path.join(date_parser_model_home, (model_name + ".bin"))

    if not Path(models_directory_path).is_file():
        model_url = model_url[model_name]
        logging.info("Downloading model {}...".format(model_name))
        try:
            urllib.request.urlretrieve(model_url, models_directory_path)
        except urllib.error.HTTPError as e:
            raise Exception("Fasttext model cannot be downloaded due to HTTP error") from e
    else:
        logging.info("dateparser-download: The model is already downloaded")
