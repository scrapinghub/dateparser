import langdetect
from dateparser.conf import apply_settings

langdetect.DetectorFactory.seed = 0

@apply_settings
def detect_languages(text, settings=None):
    language_codes = []
    try:
        parser_data = langdetect.detect_langs(text)
        for langauge_candidate in parser_data:
            if langauge_candidate.prob > settings.LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD:
                language_codes.append(langauge_candidate.lang)

    except langdetect.lang_detect_exception.LangDetectException:
        print("langdetect parsing error")

    if not language_codes:
        language_codes = settings.DEFAULT_LANGUAGE
        
    return language_codes
