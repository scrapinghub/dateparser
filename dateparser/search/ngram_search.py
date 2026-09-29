"""Date search based on parsing token n-grams.

This module implements an alternative strategy for
:func:`dateparser.search.search_dates` that looks for the longest sequences
of tokens that can be parsed as dates. It originates from a production date
extraction pipeline where it consistently produced more predictable results
than the translation-based search.
"""

import logging

import regex as re

from dateparser.date import DateDataParser

logger = logging.getLogger(__name__)

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
    + "|".join(
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

    def __init__(self, max_tokens=7):
        self.max_tokens = max_tokens

    def search_parse(self, languages, text, settings):
        """Find all dates in ``text`` and return ``(substring, date)`` pairs.

        ``languages`` are tried in the given order for every candidate
        n-gram.
        """
        parser = DateDataParser(
            languages=languages, use_given_order=True, settings=settings
        )
        tokens = [
            token
            for token in _TOKEN_RE.finditer(text)
            if token.group() not in _NOISE_TOKENS
        ]
        results = []
        index = 0
        while index < len(tokens):
            for size in range(min(self.max_tokens, len(tokens) - index), 0, -1):
                ngram = tokens[index : index + size]
                candidate = " ".join(token.group() for token in ngram)
                if _BAD_CANDIDATE_RE.match(candidate):
                    continue
                date_obj = self._parse_candidate(parser, candidate, languages)
                if date_obj is not None:
                    substring = text[ngram[0].start() : ngram[-1].end()]
                    results.append((substring.strip(_STRIP_CHARS), date_obj))
                    index += size
                    break
            else:
                index += 1
        return results

    @staticmethod
    def _parse_candidate(parser, candidate, languages):
        try:
            return parser.get_date_data(candidate).date_obj
        except Exception:
            logger.warning(
                "Failed to parse %r (languages=%r)",
                candidate,
                languages,
                exc_info=True,
            )
            return None
