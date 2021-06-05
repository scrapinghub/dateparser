import langdetect

langdetect.DetectorFactory.seed = 0


_CONFIDENCE_THRESHOLD = 0.5


def detect_languages(text):
    language_codes = ["en"] 

    try:
        parser_data = str(langdetect.detect_langs(text)[0]).split(":")
        confidence_score = float(parser_data[1])
        
        if confidence_score > _CONFIDENCE_THRESHOLD:
            language_codes = [parser_data[0]]
    except langdetect.lang_detect_exception.LangDetectException:
        print("langdetect parsing error")

    return language_codes