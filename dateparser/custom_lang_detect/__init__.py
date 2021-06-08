import importlib
from dateparser.conf import apply_settings


class CustomLanguageDetectCache:
    loaded_parser = None
    detect_languages_module = None

@apply_settings
def detect_languages(settings=None):
  if not CustomLanguageDetectCache.loaded_parser:
    print("custom loader init")
    if settings.LANGUAGE_DETECTION_EXTERNAL:
      paser_module = importlib.import_module(settings.LANGUAGE_DETECTION_METHOD)
      CustomLanguageDetectCache.detect_languages_module = paser_module.detect_languages
    else:
      paser_module = importlib.import_module("dateparser.custom_lang_detect." + settings.LANGUAGE_DETECTION_METHOD)
      CustomLanguageDetectCache.detect_languages_module = paser_module.detect_languages
    CustomLanguageDetectCache.loaded_parser = paser_module

  return  CustomLanguageDetectCache.detect_languages_module