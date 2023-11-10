from typing import List

import atheris
import sys

from fuzz_helpers import EnhancedFuzzedDataProvider

with atheris.instrument_imports():
    import dateparser

import dateparser.data
import dateparser.parser

import pytz
import re

language_codes = dateparser.data.languages_info.language_order
directives = ["%a", "%A", "%w", "%d", "%b", "%B", "%m", "%y", "%Y", "%H", "%I", "%p", "%M",
              "%S", "%f", "%z", "%Z", "%j", "%U", "%W", "%c", "%x", "%X", "%%", "%G", "%u",
              "%V", "%:Z"]
locale_codes = ["fr-PF", "qu-EC", "af-NA"]
date_order = list(dateparser.parser.date_order_chart.keys())
timezone = list(pytz.all_timezones)
preferred_date = ["last", "first", "current"]
preferred_dates_from = ["past", "future", "current_period"]
parsers = ["timestamp", "negative-timestamp", "relative-time", "custom-formats", "absolute-time", "no-spaces-time"]


def _get_format_strings(fdp: EnhancedFuzzedDataProvider) -> List[str]:
    format_strings = []
    for _ in range(fdp.ConsumeIntInRange(0, 5)):
        format_strings.append(fdp.ConsumeString(1).join(fdp.ConsumeSublist(directives)))
    return format_strings


def TestOneInput(data):
    fdp = EnhancedFuzzedDataProvider(data)

    settings = {
        "DATE_ORDER": fdp.PickValueInList(date_order),
        "PREFER_LOCALE_DATE_ORDER": fdp.ConsumeBool(),
        "TIMEZONE": fdp.PickValueInList(timezone),
        "TO_TIMEZONE": fdp.PickValueInList(timezone),
        "RETURN_AS_TIMEZONE_AWARE": fdp.ConsumeBool(),
        "PREFER_MONTH_OF_YEAR": fdp.PickValueInList(preferred_date),
        "PREFER_DAY_OF_MONTH": fdp.PickValueInList(preferred_date),
        "PREFER_DATES_FROM": fdp.PickValueInList(preferred_dates_from),
        "RELATIVE_BASE": fdp.ConsumeDate(),
        "STRICT_PARSING": fdp.ConsumeBool(),
        "REQUIRE_PARTS": [],
        "SKIP_TOKENS": [fdp.ConsumeRandomString() for _ in range(fdp.ConsumeIntInRange(0, 3))],
        "NORMALIZE": fdp.ConsumeBool(),
        "RETURN_TIME_AS_PERIOD": fdp.ConsumeBool(),
        "PARSERS": fdp.ConsumeSublist(parsers),
        "DEFAULT_LANGUAGES": fdp.ConsumeSublist(language_codes),
        "LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD": fdp.ConsumeProbability(),
    }

    try:
        dateparser.parse(
            fdp.ConsumeRandomString(),
            date_formats=_get_format_strings(fdp),
            languages=fdp.ConsumeSublist(language_codes),
            locales=fdp.ConsumeSublist(locale_codes),
            region=fdp.ConsumeString(2),
            settings=settings
        )
    except re.error:
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
