=========================
Custom language detection
=========================

`dateparser` allows to customize the language detection behavior. It currently supports two
 language detection libraries out of the box: `fasttext <https://github.com/facebookresearch/fastText>`_ 
and `langdetect <https://github.com/Mimino666/langdetect>`_, and allows you to implement your own custom language detection.



Usage of fastText and langdetect
================================

fastText
~~~~~~~~
Language detection with fastText.

Import fasttext wrapper and pass it as ``detect_languages_function``
parameter. Example::

    >>> from dateparser.custom_language_detection.fasttext import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_function=detect_languages)

the fastText integration currently supports the large and the small models. You can
download your model of choice using ``dateparser-download``.

Downloading small model::

    >>> dateparser-download --fasttext small

Downloading large model::

    >>> dateparser-download --fasttext large

Deleting all cached models::

    >>> dateparser-download --clear_cache

.. note::

    ``fastText`` uses ``small`` as default so it will download and use if no model
    is already cached.

langdetect
~~~~~~~~~~
Language detection with langdetect.

Import langdetect wrapper and pass it as ``detect_languages_function``
parameter. Example::

    >>> from dateparser.custom_language_detection.langdetect import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_function=detect_languages)


.. note::

    From some tests we did, we recommend to use ``fastText`` for faster and more accurate results.

Custom implementation
=====================

``dateparser`` allows the integration of any library to detect the languages
by wrapping them in a function that accepts ``text`` and ``confidence_threshold`` 
and returns a list of the detected language codes in ISO 639 standards.


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
