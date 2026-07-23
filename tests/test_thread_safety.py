import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

import dateparser
import dateparser.data.date_translation_data.en as en_data
from dateparser.conf import settings as base_settings
from dateparser.date import DateDataParser
from dateparser.languages.dictionary import Dictionary
from dateparser.search import search_dates
from tests import BaseTestCase


class TestThreadSafety(BaseTestCase):
    """Regression tests for thread-safety issues.

    See https://github.com/scrapinghub/dateparser/issues/441,
    https://github.com/scrapinghub/dateparser/issues/276 and
    https://github.com/scrapinghub/dateparser/issues/1291.
    """

    def setUp(self):
        super().setUp()
        # A tiny thread-switch interval makes the interpreter yield between
        # almost every bytecode, so the narrow check-then-read windows that
        # cause the races below are exercised reliably instead of only once in
        # a blue moon.
        self._switch_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-7)

    def tearDown(self):
        sys.setswitchinterval(self._switch_interval)
        super().tearDown()

    def _run_concurrently(self, func, args_list, workers=32):
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(func, arg) for arg in args_list]
            return [future.result() for future in futures]

    def test_relative_dates_concurrently(self):
        # Issues #441 and #276: the freshness parser used to crash on
        # ``self.now`` being shared/uninitialised across threads.
        results = self._run_concurrently(
            lambda _: dateparser.parse("1 day ago"),
            range(400),
        )
        self.assertTrue(all(result is not None for result in results))

    def test_dictionary_cache_eviction_concurrently(self):
        # Issue #1291: concurrent population/eviction of the size-limited
        # dictionary caches raised intermittent ``KeyError`` because the cache
        # was read after a concurrent eviction could remove the entry.
        dictionaries = [
            Dictionary(
                en_data.info,
                base_settings.replace(CACHE_SIZE_LIMIT=1, SKIP_TOKENS=["tok%d" % i]),
            )
            for i in range(40)
        ]

        def hammer(index):
            dictionary = dictionaries[index % len(dictionaries)]
            for _ in range(300):
                dictionary.split("2 days ago")
                dictionary.are_tokens_valid(["2", "days", "ago"])
            return True

        results = self._run_concurrently(hammer, range(64))
        self.assertTrue(all(results))

    def test_settings_date_order_not_mutated_while_parsing(self):
        # The absolute-time parser used to assign the locale-specific date order
        # onto the shared Settings object in place (restoring it afterwards), so
        # a concurrent parse could observe and use a foreign DATE_ORDER. Here the
        # German locale order (DMY) differs from the configured default (MDY); a
        # watcher thread asserts the shared setting never changes mid-parse.
        parser = DateDataParser(
            languages=["de"], settings={"PREFER_LOCALE_DATE_ORDER": True}
        )
        baseline = parser._settings.DATE_ORDER
        self.assertEqual(baseline, "MDY")

        observed = set()
        stop = threading.Event()

        def watch():
            while not stop.is_set():
                observed.add(parser._settings.DATE_ORDER)

        def parse(i):
            return parser.get_date_data(
                ["02.03.2014", "2014-03-02", "11.12.2013"][i % 3]
            )

        watcher = threading.Thread(target=watch)
        watcher.start()
        try:
            self._run_concurrently(parse, range(3000), workers=16)
        finally:
            stop.set()
            watcher.join()

        self.assertEqual(observed, {baseline})

    def test_search_does_not_mutate_shared_relative_base(self):
        # search_dates used to assign RELATIVE_BASE onto the shared default
        # Settings while resolving relative dates, polluting it for concurrent
        # parses/searches.
        text = (
            "19 марта 2001. Сегодня был хороший день. "
            "2 дня назад был хороший день. Вчера тоже был хороший день."
        )
        baseline = base_settings.RELATIVE_BASE

        observed = set()
        stop = threading.Event()

        def watch():
            while not stop.is_set():
                observed.add(base_settings.RELATIVE_BASE)

        def search(i):
            return search_dates(text, languages=["ru"])

        watcher = threading.Thread(target=watch)
        watcher.start()
        try:
            results = self._run_concurrently(search, range(150), workers=12)
        finally:
            stop.set()
            watcher.join()

        self.assertTrue(all(result is not None for result in results))
        self.assertEqual(observed, {baseline})


if __name__ == "__main__":
    unittest.main()
