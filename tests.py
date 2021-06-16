from dateparser.search import search_dates
from dateparser.custom_lang_detect.fast_text import detect_languages


for x in range(5):
    print(search_dates('January 3, 2017 - February 1st'))