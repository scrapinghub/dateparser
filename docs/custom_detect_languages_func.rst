============
Custom language detection
============

Usage
=====
:func:`dateparser.parse` supports two language detection
libraries `fasttext <https://github.com/facebookresearch/fastText>`_ 
and `langdetect <https://github.com/Mimino666/langdetect>`_.

fastText
~~~~~~~~
A language detection with fastText.

Import fasttext wrapper and pass it as ``detect_languages_func``
parameter with::

    >>> from dateparser.custom_lang_detect.fasttext import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_func=detect_languages)

fastText supports currently supports fastText - large and small model you can
download your model of choice using 

`Read more <https://fasttext.cc/blog/2017/10/02/blog-post.html>`_ about models.


langdetect
~~~~~~~~
A language detection with langdetect.

Import langdetect wrapper and pass it as ``detect_languages_func``
parameter with::

    >>> from dateparser.custom_lang_detect.langdetect import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_func=detect_languages)


.. note::

    ``fastText`` is the fastest if faster,  more 
    accurate and supports more languages.

Custom implementation
=====================

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

.. note::

    ``confidence_threshold`` is the float which can be used to
    filter the results.
