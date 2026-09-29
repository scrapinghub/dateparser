import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

import dateparser.data.date_translation_data.en as en_data
from dateparser.conf import settings as base_settings
from dateparser.date import DateDataParser
from dateparser.languages.dictionary import Dictionary
from dateparser.search import search_dates
from dateparser.search.search import DateSearchWithDetection, _ExactLanguageSearch
from tests import BaseTestCase


class TestThreadSafety(BaseTestCase):
    """Regression tests for thread-safety issues.

    See https://github.com/scrapinghub/dateparser/issues/441,
    https://github.com/scrapinghub/dateparser/issues/1291 and
    https://github.com/scrapinghub/dateparser/issues/1369.
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

    def test_dictionary_cache_eviction_concurrently(self):
        # Issue #1291: concurrent population/eviction of the size-limited
        # dictionary caches raised intermittent ``KeyError`` because the cache
        # was read after a concurrent eviction could remove the entry.
        dictionaries = [
            Dictionary(
                en_data.info,
                base_settings.replace(CACHE_SIZE_LIMIT=1, SKIP_TOKENS=["tok%d" % i]),
            )
            for i in range(24)
        ]

        def hammer(index):
            dictionary = dictionaries[index % len(dictionaries)]
            for _ in range(50):
                dictionary.split("2 days ago")
                dictionary.are_tokens_valid(["2", "days", "ago"])
            return True

        results = self._run_concurrently(hammer, range(24))
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
            self._run_concurrently(parse, range(100), workers=16)
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
            results = self._run_concurrently(search, range(40), workers=8)
        finally:
            stop.set()
            watcher.join()

        self.assertTrue(all(result is not None for result in results))
        self.assertEqual(observed, {baseline})

    def test_detect_language_does_not_leave_narrowed_detector_on_instance(self):
        # Issue #1369 site 1: detect_language used to stash a FullTextLanguageDetector
        # on the process-wide singleton. _best_language narrows detector.languages
        # in place, so a concurrent search_dates can load another call's already-
        # narrowed detector and return None or a wrong date.
        ds = DateSearchWithDetection()
        detected = ds.detect_language("19 марта 2001", languages=["ru", "en"])
        self.assertEqual(detected, "ru")
        detector = getattr(ds, "language_detector", None)
        if detector is not None:
            leftover = [locale.shortname for locale in detector.languages]
            self.assertEqual(
                set(leftover),
                {"ru", "en"},
                "detect_language left a single-use detector narrowed in place "
                "on the instance; concurrent search_dates can observe this "
                "(issue #1369). leftover=%r" % leftover,
            )

    def test_concurrent_search_dates_does_not_share_language_detector(self):
        # Issue #1369 site 1: the store/load gap is a few bytecodes, so park each
        # thread immediately after it stores the detector. Sequential search_dates
        # is not a valid RED for this race.
        ru_text = "Договор подписан 19 марта 2001 года в Москве"
        en_text = "The satellite was launched on 4 October 1957 from Baikonur"
        sequential_ru = search_dates(ru_text, languages=["ru"])
        sequential_en = search_dates(en_text, languages=["en"])
        self.assertIsNotNone(sequential_ru)
        self.assertIsNotNone(sequential_en)

        slot = {}
        barrier = threading.Barrier(2, timeout=10)

        def _get(self):
            return slot["v"]

        def _set(self, value):
            slot["v"] = value
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                pass

        DateSearchWithDetection.language_detector = property(_get, _set)
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                ru, en = executor.map(
                    lambda args: search_dates(args[0], languages=[args[1]]),
                    [(ru_text, "ru"), (en_text, "en")],
                )
        finally:
            del DateSearchWithDetection.language_detector

        self.assertEqual(ru, sequential_ru)
        self.assertEqual(en, sequential_en)

    def test_concurrent_search_dates_does_not_share_locale_slot(self):
        # Issue #1369 site 2: _ExactLanguageSearch.self.language is a 1-slot cache
        # on the same singleton. Park after get_current_language so a store from
        # the other thread lands before translate_search.
        ru_text = "Договор подписан 19 марта 2001 года в Москве"
        en_text = "The satellite was launched on 4 October 1957 from Baikonur"
        sequential_ru = search_dates(ru_text, languages=["ru"])
        sequential_en = search_dates(en_text, languages=["en"])
        self.assertIsNotNone(sequential_ru)
        self.assertIsNotNone(sequential_en)

        original = _ExactLanguageSearch.get_current_language
        barrier = threading.Barrier(2, timeout=10)

        def patched(self, shortname):
            result = original(self, shortname)
            try:
                barrier.wait()
            except threading.BrokenBarrierError:
                pass
            return result

        _ExactLanguageSearch.get_current_language = patched
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                ru, en = executor.map(
                    lambda args: search_dates(args[0], languages=[args[1]]),
                    [(ru_text, "ru"), (en_text, "en")],
                )
        finally:
            _ExactLanguageSearch.get_current_language = original

        self.assertEqual(ru, sequential_ru)
        self.assertEqual(en, sequential_en)


if __name__ == "__main__":
    unittest.main()
