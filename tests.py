from dateparser import DateDataParser
from dateparser.custom_lang_detect.fast_text import detect_languages

ddp = DateDataParser(detect_languages_func=detect_languages)
ddp.get_date_data('jan 24, 2014 12:49')

text = "seen as hoping that his coming will help stem the tide"
for x in range(5):
    print(ddp.get_date_data('jan 24, 2014 12:49'))