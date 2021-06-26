============
Custom language detect
============

:func:`dateparser.parse` be default supports two language detection
libraries `fasttext <https://github.com/facebookresearch/fastText>`_ 
and `langdetect <https://github.com/Mimino666/langdetect>`_ 

dateparser allow integration of any library
you can impliment any language detection library by wrap it with a 
function accepting ``text`` and ``confidence_threshold`` and returns
list of detected language codes.


Wrapper for boilerplate for implimenting custom language detections::

    def detect_languages(text, confidence_threshold):
        language_codes = []
        parser_data = languages_dectetion_function(text)
        for langauge_candidate in parser_data:
            if langauge_candidate > confidence_threshold:
                language_codes.append(language_code)
        return language_codes


Which can be further used in parse fuunction as:
``dateparser.parse(date_text, detect_languages_func=detect_languages)``

.. note::

    ``confidence_threshold`` is the float which can be used to
    filter the results.
