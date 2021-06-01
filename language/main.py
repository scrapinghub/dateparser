import fasttext
import dateparser

_language_parser = fasttext.load_model("data/lid.176.ftz")
_CONFIDENCE_THRESHOLD = 0.5


def main(text):
    parser_data = _language_parser.predict(text)
    language_code = "en"

    confidence_score = parser_data[1][0]

    if confidence_score > _CONFIDENCE_THRESHOLD:
        language_code = parser_data[0][0].replace("__label__", "")

    date_object = dateparser.parse(text, languages=[language_code])
    return date_object, language_code


text = "2 ਅਗਸਤ 1682 ਸ਼ਨਿੱਚਰ"
print(main(text))