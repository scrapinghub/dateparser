"""Date search based on parsing token n-grams.

This module implements an alternative strategy for
:func:`dateparser.search.search_dates` that looks for the longest sequences
of tokens that can be parsed as dates. It originates from a production date
extraction pipeline where it consistently produced more predictable results
than the translation-based search.
"""

import logging
from collections.abc import Callable, Iterator, Sequence
from datetime import datetime
from functools import partial

import regex as re

from dateparser.conf import Settings
from dateparser.date import DateData, DateDataParser, parse_with_formats

logger = logging.getLogger(__name__)

_DateResult = tuple[str, datetime, str | None]

# Characters that never occur inside a date expression and can therefore be
# used to split a text into tokens. Unlike whitespace, ",", "|", "(", ")"
# and "@", characters such as ".", "/", "-" and ":" *can* be part of a date
# (e.g. "1.10.2020", "2020-10-01", "10:30") and must not be split on.
_TOKEN_RE = re.compile(r"[^\s,|()@]+")

# Words that often connect a date to the surrounding text and cause
# annoying false positives; dropping them allows parsing token sequences
# such as "on May 6th 2004" or "6 of October".
_NOISE_TOKENS = frozenset(["on", "at", "of", "a"])

# Whole candidates that are blacklisted because they are known to produce
# false positives. They can still be parsed as part of a longer candidate.
_BAD_CANDIDATE_RE = re.compile(
    "^("
    + "|".join(  # noqa: FLY002
        [
            r"\d{1,3}",  # bare numbers of less than 4 digits
            r"#\d+",  # sequence numbers
            r"[-/.]+",  # bare separators, parsed as the current date
            r"\w\.?",  # single letters, with an optional dot
            "an",  # parsed as a year in some languages
        ]
    )
    + ")$"
)

# Punctuation stripped from the returned substrings, matching the behavior
# of the translation-based search strategy.
_STRIP_CHARS = " .,:()[]-'"


class _NgramDateSearch:
    """Search for dates by trying to parse token n-grams, longest first.

    The text is split into tokens using characters that never occur inside
    a date expression as separators. The tokens are then scanned left to
    right; at each position the longest n-gram (up to ``max_tokens``
    tokens) is tried first, so that the most complete date is parsed.
    Whenever an n-gram is parsed successfully, the scan continues after it,
    so the reported dates never overlap.
    """

    def __init__(self, max_tokens: int = 7) -> None:
        self.max_tokens = max_tokens

    def search_parse(
        self,
        languages: list[str],
        text: str,
        settings: Settings,
        date_formats: Sequence[str] | None = None,
        limit: int | None = None,
    ) -> list[_DateResult]:
        """Find all dates in ``text`` and return ``(substring, date, period)``
        tuples.

        ``languages`` are tried in the given order for every candidate
        n-gram. The scan stops once ``limit`` dates are found.

        Text that matches ``date_formats`` is found first, in a separate scan.
        A longer n-gram may still contain such a match, e.g. to add a time to
        a date, as long as it keeps the date and time parts of the match, but
        no n-gram may contain only part of one.
        """
        parser = DateDataParser(
            languages=languages, use_given_order=True, settings=settings
        )
        tokens = [
            token
            for token in _TOKEN_RE.finditer(text)
            if token.group() not in _NOISE_TOKENS
        ]

        def span(index: int, size: int) -> str:
            return text[tokens[index].start() : tokens[index + size - 1].end()]

        def parse_formats(index: int, size: int) -> DateData | None:
            assert date_formats
            return _try_parse(
                partial(_parse_with_formats, parser, date_formats),
                span(index, size),
                languages,
            )

        format_dates = dict(self._scan(tokens, parse_formats)) if date_formats else {}
        inside_format_dates = {
            index + offset for index, size in format_dates for offset in range(1, size)
        }
        format_sizes = dict(format_dates.keys())

        def parse(index: int, size: int) -> DateData | None:
            if (index, size) in format_dates:
                return format_dates[index, size]
            if index + size in inside_format_dates:
                return None
            words = [token.group() for token in tokens[index : index + size]]
            if _BAD_CANDIDATE_RE.match(" ".join(words)):
                return None
            date_data = parse_words(words)
            matches = [
                (start, format_sizes[start])
                for start in range(index, index + size)
                if start in format_sizes
            ]
            if date_data is None or all(
                _agrees(date_data, format_dates[match]) for match in matches
            ):
                return date_data
            # The n-gram reads a format match differently, e.g. "12/03/2024
            # 10:00" as December with a "%d/%m/%Y" format, so parse it again
            # with each match written unambiguously.
            for start, length in reversed(matches):
                iso = _iso_format(format_dates[start, length])
                if iso is None:
                    return None
                words[start - index : start - index + length] = [iso]
            date_data = parse_words(words)
            if date_data is not None and all(
                _agrees(date_data, format_dates[match]) for match in matches
            ):
                return date_data
            return None

        def parse_words(words: list[str]) -> DateData | None:
            return _try_parse(
                lambda c: parser.get_date_data(c, date_formats),
                " ".join(words),
                languages,
            )

        results: list[_DateResult] = []
        for (index, size), date_data in self._scan(tokens, parse):
            assert date_data.date_obj is not None
            results.append(
                (
                    span(index, size).strip(_STRIP_CHARS),
                    date_data.date_obj,
                    date_data.period,
                )
            )
            if len(results) == limit:
                break
        return results

    def _scan(
        self,
        tokens: Sequence[re.Match[str]],
        parse: Callable[[int, int], DateData | None],
    ) -> Iterator[tuple[tuple[int, int], DateData]]:
        """Yield the index and size of every n-gram of *tokens* that *parse*
        parses, longest first, with the parsed date data."""
        index = 0
        while index < len(tokens):
            for size in range(min(self.max_tokens, len(tokens) - index), 0, -1):
                date_data = parse(index, size)
                if date_data is not None:
                    yield (index, size), date_data
                    index += size
                    break
            else:
                index += 1


def _parse_with_formats(
    parser: DateDataParser, date_formats: Sequence[str], date_string: str
) -> DateData | None:
    date_data = parse_with_formats(date_string, date_formats, parser._settings)
    if date_data.date_obj is not None:
        return date_data
    return parser._parse_with_localized_formats(date_string, date_formats)


_PART_FIELDS = {
    "year": ("year",),
    "month": ("month",),
    "day": ("day",),
    "time": ("hour", "minute", "second"),
}


def _agrees(date_data: DateData, format_data: DateData) -> bool:
    """Return whether *date_data* has the date and time parts that
    *format_data* was parsed with."""
    return all(
        getattr(date_data.date_obj, field) == getattr(format_data.date_obj, field)
        for part in format_data.parts
        for field in _PART_FIELDS[part]
    )


def _iso_format(format_data: DateData) -> str | None:
    """Return the parts of *format_data* in ISO 8601 format, or ``None`` if it
    lacks a year, month or day."""
    date_obj = format_data.date_obj
    assert date_obj is not None
    if not {"year", "month", "day"} <= set(format_data.parts):
        return None
    if "time" in format_data.parts:
        return date_obj.isoformat(" ")
    return date_obj.date().isoformat()


def _try_parse(
    parse: Callable[[str], DateData | None], candidate: str, languages: Sequence[str]
) -> DateData | None:
    try:
        date_data = parse(candidate)
    except Exception:
        logger.warning(
            f"Failed to parse {candidate!r} (languages={languages!r})", exc_info=True
        )
        return None
    if date_data is None or date_data.date_obj is None:
        return None
    return date_data
