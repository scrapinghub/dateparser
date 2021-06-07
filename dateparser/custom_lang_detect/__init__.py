import importlib
from dateparser.conf import apply_settings

loaded_parser = None
detect_languages_module = None

@apply_settings
def detect_languages(settings=None):
  global loaded_parser
  global detect_languages_module

  if not loaded_parser:
    if settings.LANGUAGE_DETECTION_EXTERNAL:
      paser_module = importlib.import_module(settings.LANGUAGE_DETECTION_METHOD)
      detect_languages_module = paser_module.detect_languages
    else:
      paser_module = importlib.import_module("dateparser.custom_lang_detect." + settings.LANGUAGE_DETECTION_METHOD)
      detect_languages_module = paser_module.detect_languages
      print("custom loader init")
    loaded_parser = paser_module

  return  detect_languages_module