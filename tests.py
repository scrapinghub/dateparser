from dateparser import parse

settings={
    'LANGUAGE_DETECTION_ENABLED': True,
    'LANGUAGE_DETECTION_EXTERNAL': True,
    'LANGUAGE_DETECTION_METHOD': 'lang_detect'
    
}


for x in range(5):
    print(parse("5th June 2021", lang_settings=settings))