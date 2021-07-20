from pathlib import Path
import urllib.request
import os
import logging

from .utils import date_parser_model_home, check_if_date_parser_model_home_exists_else_create


def fasttext_downloader(model=[]):
    check_if_date_parser_model_home_exists_else_create()

    model_url = {
        "small": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz",
        "large": "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
    }

    if not model:
        model_name = "small"
    elif model and model[0] == "large":
        model_name = "large"
    else:
        logging.error(
            "Couldn't find a model called \"{}\". Supported models are:"
            " {}".format(model[0], ", ".join(model_url.keys()))
        )
        return 0

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
