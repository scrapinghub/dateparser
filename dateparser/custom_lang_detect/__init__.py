import importlib

loaded_parser = None
language_parser = None

def language_parser_m(paser_module="fast_text"):
  global loaded_parser
  global language_parser

  try:
    if loaded_parser == None:
      paser_module = importlib.import_module("dateparser.custom_lang_detect." + paser_module)
      language_parser = paser_module.language_parser
      print("custom loader init")
  except:
    print("Requested model not found", paser_module)

  loaded_parser = paser_module
  return  language_parser
