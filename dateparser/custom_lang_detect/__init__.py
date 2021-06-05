import importlib

loaded_parser = None
detect_languages_module = None

def detect_languages(paser_module="fast_text"):
  global loaded_parser
  global detect_languages_module

  try:
    if not loaded_parser:
      paser_module = importlib.import_module("dateparser.custom_lang_detect." + paser_module)
      detect_languages_module = paser_module.detect_languages
      print("custom loader init")
  except NameError:
    print("Requested model not found", paser_module)
    import sys
    sys.exit(1)


  loaded_parser = paser_module
  return  detect_languages_module
