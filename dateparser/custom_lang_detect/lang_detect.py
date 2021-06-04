try:
    from langdetect import detect_langs
except:
    import sys
    import subprocess
    print("Installing fast_text library")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install','langdetect'])
    from langdetect import detect_langs


from langdetect import DetectorFactory
DetectorFactory.seed = 0


_CONFIDENCE_THRESHOLD = 0.5


def language_parser(text):
    parser_data = str(detect_langs(text)[0]).split(":")
    language_codes = ["en"]
    confidence_score = float(parser_data[1])

    if confidence_score > _CONFIDENCE_THRESHOLD:
        language_codes = [parser_data[0]]

    return language_codes