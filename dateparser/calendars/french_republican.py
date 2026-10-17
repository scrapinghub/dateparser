import re
import unicodedata
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from convertdate import french_republican

from dateparser.calendars import CalendarBase

if TYPE_CHECKING:
    from dateparser.conf import Settings

_MONTHS = {
    name: index
    for index, names in enumerate(
        (
            ("vendemiaire",),
            ("brumaire",),
            ("frimaire",),
            ("nivose",),
            ("pluviose",),
            ("ventose",),
            ("germinal",),
            ("floreal",),
            ("prairial",),
            ("messidor",),
            ("thermidor",),
            ("fructidor",),
            ("sansculottides", "sans-culottides", "jours complementaires"),
        ),
        start=1,
    )
    for name in names
}
_YEAR_WORDS = {
    name: index
    for index, names in enumerate(
        (
            ("un", "premier"),
            ("deux", "deuxieme", "second"),
            ("trois", "troisieme"),
            ("quatre", "quatrieme"),
            ("cinq", "cinquieme"),
            ("six", "sixieme"),
            ("sept", "septieme"),
            ("huit", "huitieme"),
            ("neuf", "neuvieme"),
            ("dix", "dixieme"),
            ("onze", "onzieme"),
            ("douze", "douzieme"),
            ("treize", "treizieme"),
            ("quatorze", "quatorzieme"),
        ),
        start=1,
    )
    for name in names
}
# Catalog records often follow the year with "de la République" and with its
# Gregorian equivalent, e.g. "An X de la République [i.e. 1802]".
_RE_DATE = re.compile(
    rf"(?:(?:(?P<day>\d{{1,2}})(?:er)?\s+)?(?P<month>{'|'.join(_MONTHS)})\s+)?"
    r"an(?:no)?\.?\s+(?:(?P<year>\d{1,3})|(?P<roman>"
    r"C{0,3}(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))"
    rf"|(?P<word>{'|'.join(_YEAR_WORDS)}))\.?(?:er|e|eme|me)?\.?"
    r"(?:\s+de\s+la\s+republ[^\[\]()]*)?"
    r"(?:\s*(?:[\[(][^\[\]()]*\d{4}[^\[\]()]*[\])]|[-=,]?\s*\d{4}(?:/\d{2,4})?))?",
    flags=re.IGNORECASE,
)
_ROMAN_NUMERAL_VALUES = {"C": 100, "L": 50, "X": 10, "V": 5, "I": 1}


def _roman_to_int(numeral: str) -> int:
    values = [_ROMAN_NUMERAL_VALUES[char] for char in numeral.upper()]
    return sum(
        -value if value < next_value else value
        for value, next_value in zip(values, [*values[1:], 0], strict=True)
    )


def _month_length(year: int, month: int) -> int:
    if month < 13:
        return 30
    return 6 if french_republican.leap(year) else 5


class _french_republican_parser:
    @classmethod
    def parse(
        cls, datestring: str, settings: "Settings"
    ) -> tuple[datetime, str | None, tuple[str, ...]]:
        normalized = "".join(
            char
            for char in unicodedata.normalize("NFKD", datestring.strip())
            if not unicodedata.combining(char)
        )
        match = _RE_DATE.fullmatch(normalized)
        if not match or not (match["year"] or match["roman"] or match["word"]):
            raise ValueError(datestring)
        if match["year"]:
            year = int(match["year"])
        elif match["roman"]:
            year = _roman_to_int(match["roman"])
        else:
            year = _YEAR_WORDS[match["word"].lower()]
        if not year:
            raise ValueError(datestring)
        now = settings.RELATIVE_BASE or datetime.now(tz=timezone.utc).replace(
            tzinfo=None
        )
        _, now_month, now_day = french_republican.from_gregorian(
            now.year, now.month, now.day
        )
        if match["month"]:
            month = _MONTHS[match["month"].lower()]
        else:
            month = {"first": 1, "last": 13}.get(
                settings.PREFER_MONTH_OF_YEAR, now_month
            )
        if match["day"]:
            day = int(match["day"])
        else:
            day = min(
                {"first": 1, "last": 30}.get(settings.PREFER_DAY_OF_MONTH, now_day),
                _month_length(year, month),
            )
        date = datetime(*french_republican.to_gregorian(year, month, day))
        period = "day" if match["day"] else "month" if match["month"] else "year"
        parts = ("year", "month", "day")[: ("year", "month", "day").index(period) + 1]
        return date, period, parts


class FrenchRepublicanCalendar(CalendarBase):
    """Calendar class for the `French Republican calendar
    <https://en.wikipedia.org/wiki/French_Republican_calendar>`_."""

    parser = _french_republican_parser
