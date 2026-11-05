"""CodSpeed benchmarks.

These are only collected when ``pytest-codspeed`` is installed, which is the
case in the dedicated ``benchmark`` tox environment (see ``tox.ini``). In every
other environment they are skipped, so the regular test runs are unaffected.
"""

import pytest

pytest.importorskip("pytest_codspeed", reason="Benchmark tests require pytest-codspeed")

# Relative date strings in the form the freshness parser actually receives them:
# the locale translates the input first, which turns plural units singular
# ("2 hours, 50 minutes ago" -> "2 hour 50 minute ago"). PATTERN only matches
# singular units, so benchmarking the untranslated strings would measure a failed
# scan instead of the real workload.
#
# Each benchmark runs the whole list rather than a single string: CodSpeed's
# simulation mode measures one call, and a lone match on a short string is too
# small a unit of work to be meaningful.
TRANSLATED_RELATIVE_STRINGS = [
    "1 minute ago",
    "2 hour 50 minute ago",
    "3 day ago",
    "in 2 week",
    "10.5 year ago",
    "1 day 2 hour 3 minute 4 second ago",
]

# A long run of digits: the input shape that made the relative-date regexes
# backtrack superlinearly before #1335. Deliberately pathological rather than
# realistic -- it is what turns a reintroduced regression into an unmissable
# signal.
#
# The length is chosen so that a regressed run still *finishes and reports*:
# with the old greedy quantifiers this takes ~380ms against ~0.7ms for the
# possessive ones, a ~500x jump that no threshold can miss, while remaining a
# handful of seconds under CodSpeed's instrumentation. The 3200 digits of the
# original #1335 repro would instead need ~20 minutes per benchmark once
# regressed, so the job would time out without ever reporting.
LONG_DIGIT_RUN = "9" * 800
