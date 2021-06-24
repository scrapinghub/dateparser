import json
import os

_dir_path = os.path.dirname(os.path.realpath(__file__))
languages_map = json.load(open(_dir_path + '/data/languages_map.json'))
