"""

IMPORT ALL THE REQUIRED LIBRARIES AND SET CONSTANTS


DEFINE A FUNCTION WITH NAME "detect_languages" WHICH ACCEPTS ONE PARAM "text".


SEE EXAMPLES BELOW : 

"""

import langdetect
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

    """
    RETURN LIST OF LANGUAGES IN ISO 639
    """

    return language_codes