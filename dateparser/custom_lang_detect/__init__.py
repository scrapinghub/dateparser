import importlib
import sys

loaded_parser = None
detect_languages_module = None

def detect_languages(paser_module="fast_text", is_external=False):
  global loaded_parser
  global detect_languages_module



  if not loaded_parser:
    if is_external:
      paser_module = importlib.import_module(paser_module)
      detect_languages_module = paser_module.detect_languages
    else:
      paser_module = importlib.import_module("dateparser.custom_lang_detect." + paser_module)
      detect_languages_module = paser_module.detect_languages
      print("custom loader init")

  loaded_parser = paser_module
  return  detect_languages_module
