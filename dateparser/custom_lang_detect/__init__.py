import importlib
from dateparser.conf import apply_settings


@apply_settings
def detect_languages(settings=None):
  if settings.LANGUAGE_DETECTION_EXTERNAL:
    paser_module = importlib.import_module(settings.LANGUAGE_DETECTION_METHOD)
    return  paser_module.detect_languages
  else:
    paser_module = importlib.import_module("dateparser.custom_lang_detect." + settings.LANGUAGE_DETECTION_METHOD)
    return  paser_module.detect_languages
