=========================
Custom language detection
=========================

`dateparser` allows to customize the language detection behavior by using the ``detect_languages_function`` parameter.
It supports the `langdetect <https://github.com/Mimino666/langdetect>`_ library out of the box, and allows you to implement your own custom language detection.

.. warning::

    For short strings the language detection could fail, so it's highly recommended to use ``detect_languages_function``
    along with ``DEFAULT_LANGUAGES``.

Built-in implementations
========================

langdetect
~~~~~~~~~~
Language detection with langdetect.

To use langdetect, first install it::

    pip install dateparser[langdetect]

Then import the langdetect wrapper and pass it as ``detect_languages_function``
parameter. Example::

    >>> from dateparser.custom_language_detection.langdetect import detect_languages
    >>> dateparser.parse('12/12/12', detect_languages_function=detect_languages)

.. note::

    **Deprecated fastText support**: The fastText integration has been removed as the library
    is archived and no longer maintained. If you were using fastText, please migrate to langdetect.

Custom implementation
=====================

``dateparser`` allows the integration of any library to detect languages by
wrapping that library in a function that accepts 2 parameters, ``text`` and
``confidence_threshold``, and returns a list of the detected language codes in
ISO 639 standards.


Wrapper for boilerplate for implementing custom language detections::

    def detect_languages(text, confidence_threshold):
        """
        Takes 2 parameters, `text` and `confidence_threshold`, and returns
        a list of `languages codes`.

        * `text` is the input string whose language needs to be detected.

        * `confidence_threshold` is a number between 0 and 1 that indicates the
        minimum confidence required for language matches.

        For language detection libraries that, for each language, indicate how
        confident they are that the language matches the input text, you should
        filter out languages with a confidence lower than this value (adjusted,
        if needed, to the confidence range of the target library).

        This value comes from the dateparser setting
        `LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD`.

        The result must be a list of languages codes (strings).
        """
        # here you can apply your own logic
        return language_codes

