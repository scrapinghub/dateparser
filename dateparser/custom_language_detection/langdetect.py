from langdetect.detector_factory import DetectorFactory, PROFILES_DIRECTORY
import langdetect


# The below Factory is set to prevent setting global state of the library
# but still get consistent results.
# Refer - https://github.com/Mimino666/langdetect

class Factory:
    data = None


def init_factory():
    if Factory.data is None:
        Factory.data = DetectorFactory()
        Factory.data.load_profile(PROFILES_DIRECTORY)
        Factory.data.seed = 0


def detect_langs(text):
    init_factory()
    detector = Factory.data.create()
    detector.append(text)
    return detector.get_probabilities()


def detect_languages(text, confidence_threshold):
    language_codes = []
    try:
        parser_data = detect_langs(text)
        for langauge_candidate in parser_data:
            if langauge_candidate.prob > confidence_threshold:
                language_codes.append(langauge_candidate.lang)
    except langdetect.lang_detect_exception.LangDetectException:
        pass
    return language_codes
