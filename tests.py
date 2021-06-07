from dateparser import parse

settings={
    'LANGUAGE_DETECTION_ENABLED': True,
    'LANGUAGE_DETECTION_METHOD': 'fast_text',
    'LANGUAGE_DETECTION_STRICT_USE' : True,
    'LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD' : 0.5
}

for x in range(5):
    print(parse("2 ottobre 1935", settings=settings))