r"""Benchmarks for :mod:`dateparser.languages.dictionary`.

``Dictionary.split()`` first splits the input with a regex built from the
locale's ``relative-type-regex`` entries. Those entries carried the same greedy
``\d+[.,]?\d*`` that #1335 replaced with the possessive ``\d++[.,]?\d*+``, and
because the alternation is applied by ``re.split()`` across the whole input, a
long digit run backtracked quadratically here too.

The typical-input side of ``Dictionary.split()`` is covered end to end by
``test_benchmark_parse.py``, which reaches it through the real locale objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import dateparser.data.date_translation_data.en as en_data
from dateparser.conf import settings
from dateparser.languages.dictionary import Dictionary
from tests.benchmarks import LONG_DIGIT_RUN

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture


def test_dictionary_split_relative_regex_long_digit_run(
    benchmark: BenchmarkFixture,
) -> None:
    # Only the compiled relative-split regex is taken from the dictionary, as
    # ``tests/test_freshness_date_parser.py`` already does. For English the
    # regex a plain Dictionary compiles is identical to the NormalizedDictionary
    # one the parser uses, since normalization leaves these strings untouched.
    split_relative_regex = Dictionary(
        en_data.info, settings
    )._get_split_relative_regex_cache()

    # A digit run holds no relative-date string, so it must come back unsplit.
    assert split_relative_regex.split(LONG_DIGIT_RUN) == [LONG_DIGIT_RUN]

    benchmark(lambda: split_relative_regex.split(LONG_DIGIT_RUN))
