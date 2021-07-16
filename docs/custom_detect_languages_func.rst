============
Custom language detection
============

``dateparser`` supports integration of custom language detection. 
 
``dateparser.parse`` and ``dateparser.search.search_dates`` out of the box
supports two language detection libraries 
`fasttext <https://github.com/facebookresearch/fastText>`_ 
and `langdetect <https://github.com/Mimino666/langdetect>`_.

You can impliment your own custom language detection by using the 
boilerplate code below.


Usage
=====

fastText
~~~~~~~~
Language detection with fastText.

Import fasttext wrapper and pass it as ``detect_languages_function``
parameter with::

    >>> from dateparser.custom_lang_detect.fasttext import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_function=detect_languages)

fastText supports currently supports fastText - large and small model you can
download your model of choice using ``dateparser-download``.

Downloading small model::

    >>> dateparser-download fasttext small

Downloading large model::

    >>> dateparser-download fasttext large

.. note::

    ``fastText`` used ``small`` as default so it will download and use if no model
    is already cached.

langdetect
~~~~~~~~
Language detection with langdetect.

Import langdetect wrapper and pass it as ``detect_languages_function``
parameter with::

    >>> from dateparser.custom_lang_detect.langdetect import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_function=detect_languages)


.. note::

    ``fastText`` is the fastest if faster,  more 
    accurate and supports more languages.

Custom implementation
=====================

``dateparser`` allows the integration of any library
you can implement any language detection library by wrapping it with a 
function accepting ``text`` and ``confidence_threshold`` and returning
list of detected language codes in ISO 639 standards.


Wrapper for boilerplate for implementing custom language detections::

    def detect_languages(text, confidence_threshold):
        """
        Takes two variables: `text` and `confidence_treshold` and returns
        a list of `languages codes`.
        
        * `text` is a string containing from where the language codes are 
        derived.
        
        * `confidence_treshold` is a number between 0 and 1 that can be 
        used to decide if the confidence is enough. It can be also ignored.
        This value comes from the dateparser setting: 
        `LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD`
        
        The result must be a list of languages codes (strings).
        """
        # here you can apply your own logic
        return language_codes

.. note::

    ``confidence_threshold`` is a float between 0 and 1 that can be used to filter the results. It comes from the ``LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD`` setting.
