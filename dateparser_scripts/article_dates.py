import argparse
import csv
import io
import os
import random
import re
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict, namedtuple
from datetime import datetime
from functools import cache
from multiprocessing import Pool
from pathlib import Path

from dateparser.data.languages_info import language_order
from dateparser.date import DateDataParser
from dateparser.search import search_dates

URL = (
    "https://github.com/scrapinghub/dateparser/files/6532578/"
    "article_date_sample_Oct_2020_Mar_2021_public.csv.zip"
)
"""Dataset shared in #928: 300k article publication dates collected from the
web between October 2020 and March 2021."""

COLLECTION_END = datetime(2021, 4, 1)
"""No publication date in the dataset can be later than this, so later parsed
dates are wrong, and relative dates are resolved against it."""

SETTINGS = {"RELATIVE_BASE": COLLECTION_END}

Result = namedtuple("Result", "text language date hinted locale found error")

PROBLEMS = {
    "error": lambda r: r.error is not None,
    "unparsed": lambda r: r.date is None,
    "searchable": lambda r: r.found,
    "future": lambda r: (
        r.date is not None and r.date.replace(tzinfo=None) > COLLECTION_END
    ),
    "hint-dependent": lambda r: r.hinted is not None and r.hinted != r.date,
    "misdetected": lambda r: (
        r.hinted is not None
        and r.locale is not None
        and re.search(r"[^\W\d_]{2}", r.text) is not None
        and r.locale.split("-")[0] != r.language
    ),
}
"""Checks run on every row. See CONTRIBUTING.rst for what each one means."""


def cache_path():
    root = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(root) / "dateparser" / URL.rsplit("/", 1)[1]


def load(path):
    """Return a Counter of (text, language) pairs, downloading the dataset
    to *path* first if missing."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {URL} to {path}", file=sys.stderr)
        urllib.request.urlretrieve(URL, path)
    with zipfile.ZipFile(path) as archive:
        (name,) = archive.namelist()
        with archive.open(name) as f:
            rows = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
            return Counter(
                (row["datePublishedRaw"], row["articleLanguage"]) for row in rows
            )


@cache
def parser(language=None):
    return DateDataParser(languages=[language] if language else None, settings=SETTINGS)


def evaluate(item):
    text, language = item
    result = Result(text, language, None, None, None, False, None)
    try:
        data = parser().get_date_data(text)
        result = result._replace(date=data.date_obj, locale=data.locale)
        if language in language_order:
            hinted = parser(language).get_date_data(text).date_obj
            result = result._replace(hinted=hinted)
        if data.date_obj is None:
            found = search_dates(text, settings=SETTINGS) is not None
            result = result._replace(found=found)
    except Exception as exception:
        result = result._replace(error=f"{type(exception).__name__}: {exception}")
    return result


def shape(text):
    """Return *text* with digits replaced by 9 and words by a, so that
    strings written in the same format share a shape."""
    return re.sub(r"[^\W\d_]+", "a", re.sub(r"\d", "9", text))


def report(results, counts, top, examples, out):
    total = sum(counts.values())
    hits = {name: [r for r in results if check(r)] for name, check in PROBLEMS.items()}

    def weight(rs):
        return sum(counts[r.text, r.language] for r in rs)

    print(f"{total} rows, {len(results)} distinct\n", file=out)
    for name, rs in hits.items():
        print(f"{name}: {weight(rs)} ({weight(rs) / total:.1%})", file=out)

    by_language = defaultdict(list)
    for r in results:
        by_language[r.language].append(r)
    print(f"\n{'language':>8} {'rows':>7}", *(f"{n:>14}" for n in hits), file=out)
    ranked = sorted(by_language.items(), key=lambda item: -weight(item[1]))
    for language, rs in ranked[:top]:
        rows = weight(rs)
        cells = (f"{weight(filter(PROBLEMS[n], rs)) / rows:>14.1%}" for n in hits)
        print(f"{language or '-':>8} {rows:>7}", *cells, file=out)

    for name, rs in hits.items():
        groups = defaultdict(list)
        for r in rs:
            groups[shape(r.text)].append(r)
        ranked = sorted(groups.items(), key=lambda item: -weight(item[1]))
        print(f"\n== {name}: top shapes", file=out)
        for s, group in ranked[:top]:
            print(f"{weight(group):>7}  {s!r}", file=out)
            for r in group[:examples]:
                print(
                    f"         {r.language or '-':>3} {r.text!r} -> {r.date}"
                    f" (hinted: {r.hinted}, detected: {r.locale}"
                    f"{', ' + r.error if r.error else ''})",
                    file=out,
                )


def main(argv=None):
    arg_parser = argparse.ArgumentParser(
        description="Evaluate dateparser against the dataset from #928."
    )
    arg_parser.add_argument("--data", type=Path, default=cache_path())
    arg_parser.add_argument("--sample", type=int, help="evaluate this many random rows")
    arg_parser.add_argument("--language", help="only rows in this language")
    arg_parser.add_argument(
        "--top", type=int, default=15, help="how many languages and shapes to list"
    )
    arg_parser.add_argument("--examples", type=int, default=3)
    arg_parser.add_argument("--jobs", type=int, default=os.cpu_count())
    arg_parser.add_argument(
        "--output",
        type=Path,
        help="write one line per distinct row, to compare runs with diff",
    )
    args = arg_parser.parse_args(argv)

    counts = load(args.data)
    if args.language is not None:
        counts = Counter({k: n for k, n in counts.items() if k[1] == args.language})
    if args.sample:
        rows = random.Random(0).sample(list(counts.elements()), args.sample)
        counts = Counter(rows)
    items = sorted(counts)
    with Pool(args.jobs) as pool:
        results = pool.map(evaluate, items, chunksize=100)

    report(results, counts, args.top, args.examples, sys.stdout)
    if args.output:
        with args.output.open("w", encoding="utf-8") as f:
            for r in results:
                print(*(repr(v) for v in r), sep="\t", file=f)


if __name__ == "__main__":
    main()
