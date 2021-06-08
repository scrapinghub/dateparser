from dateparser.search import search_dates

settings={
    'LANGUAGE_DETECTION_ENABLED': True,
    'LANGUAGE_DETECTION_METHOD': 'fast_text',
    'LANGUAGE_DETECTION_STRICT_USE' : True
}

for x in range(5):
    print(search_dates("2 ottobre 1935", settings=settings))