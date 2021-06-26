import langdetect


langdetect.DetectorFactory.seed = 0


def detect_languages(text, confidence_threshold=0.5):
    language_codes = []
    try:
        parser_data = langdetect.detect_langs(text)
        for langauge_candidate in parser_data:
            if langauge_candidate.prob > confidence_threshold:
                language_codes.append(langauge_candidate.lang)
    except langdetect.lang_detect_exception.LangDetectException:
        pass
    return language_codes
