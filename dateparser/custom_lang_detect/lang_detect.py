import langdetect
from dateparser.conf import apply_settings

langdetect.DetectorFactory.seed = 0

@apply_settings
def detect_languages(text, settings=None):
    language_codes = ["en"] 

    try:
        parser_data = str(langdetect.detect_langs(text)[0]).split(":")
        confidence_score = float(parser_data[1])
        
        if confidence_score > settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD:
            language_codes = [parser_data[0]]
    except langdetect.lang_detect_exception.LangDetectException:
        print("langdetect parsing error")

    return language_codes