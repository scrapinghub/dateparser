import importlib


def language_parser_m(paser_module="fast_text"):
  try:
    importlib.import_module("dateparser.custom_lang_detect." + paser_module)
    print("custom loader init")
  except:
    print("Requested model not found", paser_module)

  return  fast_text.language_parser
